from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredFileLoader
from models.chatglm_llm import ChatGLM
from configs.model_config import *
import datetime
from textsplitter import ChineseTextSplitter
from typing import List, Tuple
from langchain.docstore.document import Document
import numpy as np
from utils import torch_gc

# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 6

# LLM input history length
LLM_HISTORY_LEN = 3

DEVICE_ = EMBEDDING_DEVICE
DEVICE_ID = "0" if torch.cuda.is_available() else None
DEVICE = f"{DEVICE_}:{DEVICE_ID}" if DEVICE_ID else DEVICE_


def load_file(filepath):
    if filepath.lower().endswith(".md"):
        loader = UnstructuredFileLoader(filepath, mode="elements")
        docs = loader.load()
    elif filepath.lower().endswith(".pdf"):
        loader = UnstructuredFileLoader(filepath)
        textsplitter = ChineseTextSplitter(pdf=True)
        docs = loader.load_and_split(textsplitter)
    else:
        loader = UnstructuredFileLoader(filepath, mode="elements")
        textsplitter = ChineseTextSplitter(pdf=False)
        docs = loader.load_and_split(text_splitter=textsplitter)
    return docs


def generate_prompt(related_docs: List[str],
                    query: str,
                    prompt_template=PROMPT_TEMPLATE) -> str:
    context = "\n".join([doc.page_content for doc in related_docs])
    prompt = prompt_template.replace("{question}", query).replace("{context}", context)
    return prompt


def get_docs_with_score(docs_with_score):
    docs = []
    for doc, score in docs_with_score:
        doc.metadata["score"] = score
        docs.append(doc)
    return docs


def seperate_list(ls: List[int]) -> List[List[int]]:
    lists = []
    ls1 = [ls[0]]
    for i in range(1, len(ls)):
        if ls[i - 1] + 1 == ls[i]:
            ls1.append(ls[i])
        else:
            lists.append(ls1)
            ls1 = [ls[i]]
    lists.append(ls1)
    return lists


def similarity_search_with_score_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
) -> List[Tuple[Document, float]]:
    scores, indices = self.index.search(np.array([embedding], dtype=np.float32), k)
    docs = []
    id_set = set()
    for j, i in enumerate(indices[0]):
        if i == -1:
            # This happens when not enough docs are returned.
            continue
        _id = self.index_to_docstore_id[i]
        doc = self.docstore.search(_id)
        id_set.add(i)
        docs_len = len(doc.page_content)
        for k in range(1, max(i, len(docs) - i)):
            break_flag = False
            for l in [i + k, i - k]:
                if 0 <= l < len(self.index_to_docstore_id):
                    _id0 = self.index_to_docstore_id[l]
                    doc0 = self.docstore.search(_id0)
                    if docs_len + len(doc0.page_content) > self.chunk_size:
                        break_flag=True
                        break
                    elif doc0.metadata["source"] == doc.metadata["source"]:
                        docs_len += len(doc0.page_content)
                        id_set.add(l)
            if break_flag:
                break
    id_list = sorted(list(id_set))
    id_lists = seperate_list(id_list)
    for id_seq in id_lists:
        for id in id_seq:
            if id == id_seq[0]:
                _id = self.index_to_docstore_id[id]
                doc = self.docstore.search(_id)
            else:
                _id0 = self.index_to_docstore_id[id]
                doc0 = self.docstore.search(_id0)
                doc.page_content += doc0.page_content
        if not isinstance(doc, Document):
            raise ValueError(f"Could not find document for id {_id}, got {doc}")
        docs.append((doc, scores[0][j]))
    torch_gc(DEVICE)
    return docs


class LocalDocQA:
    llm: object = None
    embeddings: object = None
    top_k: int = VECTOR_SEARCH_TOP_K
    chunk_size: int = CHUNK_SIZE

    def init_cfg(self,
                 embedding_model: str = EMBEDDING_MODEL,
                 embedding_device=EMBEDDING_DEVICE,
                 llm_history_len: int = LLM_HISTORY_LEN,
                 llm_model: str = LLM_MODEL,
                 llm_device=LLM_DEVICE,
                 top_k=VECTOR_SEARCH_TOP_K,
                 use_ptuning_v2: bool = USE_PTUNING_V2
                 ):
        self.llm = ChatGLM()
        self.llm.load_model(model_name_or_path=llm_model_dict[llm_model],
                            llm_device=llm_device,
                            use_ptuning_v2=use_ptuning_v2)
        self.llm.history_len = llm_history_len

        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model],
                                                model_kwargs={'device': embedding_device})
        self.top_k = top_k

    def init_knowledge_vector_store(self,
                                    filepath: str or List[str],
                                    vs_path: str or os.PathLike = None):
        loaded_files = []
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("路径不存在")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    docs = load_file(filepath)
                    print(f"{file} 已成功加载")
                    loaded_files.append(filepath)
                except Exception as e:
                    print(e)
                    print(f"{file} 未能成功加载")
                    return None
            elif os.path.isdir(filepath):
                docs = []
                for file in os.listdir(filepath):
                    fullfilepath = os.path.join(filepath, file)
                    try:
                        docs += load_file(fullfilepath)
                        print(f"{file} 已成功加载")
                        loaded_files.append(fullfilepath)
                    except Exception as e:
                        print(e)
                        print(f"{file} 未能成功加载")
        else:
            docs = []
            for file in filepath:
                try:
                    docs += load_file(file)
                    print(f"{file} 已成功加载")
                    loaded_files.append(file)
                except Exception as e:
                    print(e)
                    print(f"{file} 未能成功加载")
        if len(docs) > 0:
            if vs_path and os.path.isdir(vs_path):
                vector_store = FAISS.load_local(vs_path, self.embeddings)
                vector_store.add_documents(docs)
                torch_gc(DEVICE)
            else:
                if not vs_path:
                    vs_path = os.path.join(VS_ROOT_PATH,
                                           f"""{os.path.splitext(file)[0]}_FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}""")
                vector_store = FAISS.from_documents(docs, self.embeddings)
                torch_gc(DEVICE)

            vector_store.save_local(vs_path)
            return vs_path, loaded_files
        else:
            print("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")
            return None, loaded_files

    def get_knowledge_based_answer(self,
                                   query,
                                   vs_path,
                                   chat_history=[],
                                   streaming: bool = STREAMING):
        vector_store = FAISS.load_local(vs_path, self.embeddings)
        FAISS.similarity_search_with_score_by_vector = similarity_search_with_score_by_vector
        vector_store.chunk_size = self.chunk_size
        related_docs_with_score = vector_store.similarity_search_with_score(query,
                                                                            k=self.top_k)
        related_docs = get_docs_with_score(related_docs_with_score)
        prompt = generate_prompt(related_docs, query)

        # if streaming:
        #     for result, history in self.llm._stream_call(prompt=prompt,
        #                                                  history=chat_history):
        #         history[-1][0] = query
        #         response = {"query": query,
        #                     "result": result,
        #                     "source_documents": related_docs}
        #         yield response, history
        # else:
        for result, history in self.llm._call(prompt=prompt,
                                              history=chat_history,
                                              streaming=streaming):
            history[-1][0] = query
            response = {"query": query,
                        "result": result,
                        "source_documents": related_docs}
            yield response, history


if __name__ == "__main__":
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg()
    query = "本项目使用的embedding模型是什么，消耗多少显存"
    vs_path = "/Users/liuqian/Downloads/glm-dev/vector_store/aaa"
    last_print_len = 0
    for resp, history in local_doc_qa.get_knowledge_based_answer(query=query,
                                                                 vs_path=vs_path,
                                                                 chat_history=[],
                                                                 streaming=True):
        print(resp["result"][last_print_len:], end="", flush=True)
        last_print_len = len(resp["result"])
    source_text = [f"""出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n"""
                   # f"""相关度：{doc.metadata['score']}\n\n"""
                   for inum, doc in
                   enumerate(resp["source_documents"])]
    print("\n\n" + "\n\n".join(source_text))
    # for resp, history in local_doc_qa.get_knowledge_based_answer(query=query,
    #                                                              vs_path=vs_path,
    #                                                              chat_history=[],
    #                                                              streaming=False):
    #     print(resp["result"])
    pass
