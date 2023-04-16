from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredFileLoader
from models.chatglm_llm import ChatGLM
import sentence_transformers
import os
from configs.model_config import *
import datetime
from typing import List

# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 6

# LLM input history length
LLM_HISTORY_LEN = 3

# Show reply with source text from input document
REPLY_WITH_SOURCE = True


class LocalDocQA:
    llm: object = None
    embeddings: object = None

    def init_cfg(self,
                 embedding_model: str = EMBEDDING_MODEL,
                 embedding_device=EMBEDDING_DEVICE,
                 llm_history_len: int = LLM_HISTORY_LEN,
                 llm_model: str = LLM_MODEL,
                 llm_device=LLM_DEVICE,
                 top_k=VECTOR_SEARCH_TOP_K,
                 ):
        self.llm = ChatGLM()
        self.llm.load_model(model_name_or_path=llm_model_dict[llm_model],
                            llm_device=llm_device)
        self.llm.history_len = llm_history_len

        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model], )
        self.embeddings.client = sentence_transformers.SentenceTransformer(self.embeddings.model_name,
                                                                           device=embedding_device)
        self.top_k = top_k

    def init_knowledge_vector_store(self,
                                    filepath: str or List[str]):
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("路径不存在")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    loader = UnstructuredFileLoader(filepath, mode="elements")
                    docs = loader.load()
                    print(f"{file} 已成功加载")
                except:
                    print(f"{file} 未能成功加载")
                    return None
            elif os.path.isdir(filepath):
                docs = []
                for file in os.listdir(filepath):
                    fullfilepath = os.path.join(filepath, file)
                    try:
                        loader = UnstructuredFileLoader(fullfilepath, mode="elements")
                        docs += loader.load()
                        print(f"{file} 已成功加载")
                    except:
                        print(f"{file} 未能成功加载")
        else:
            docs = []
            for file in filepath:
                try:
                    loader = UnstructuredFileLoader(file, mode="elements")
                    docs += loader.load()
                    print(f"{file} 已成功加载")
                except:
                    print(f"{file} 未能成功加载")

        vector_store = FAISS.from_documents(docs, self.embeddings)
        vs_path = f"""./vector_store/{os.path.splitext(file)[0]}_FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}"""
        vector_store.save_local(vs_path)
        return vs_path if len(docs)>0 else None

    def get_knowledge_based_answer(self,
                                   query,
                                   vs_path,
                                   chat_history=[], ):
        prompt_template = """基于以下已知信息，简洁和专业的来回答用户的问题。
    如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
    
    已知内容:
    {context}
    
    问题:
    {question}"""
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        self.llm.history = chat_history
        vector_store = FAISS.load_local(vs_path, self.embeddings)
        knowledge_chain = RetrievalQA.from_llm(
            llm=self.llm,
            retriever=vector_store.as_retriever(search_kwargs={"k": self.top_k}),
            prompt=prompt
        )
        knowledge_chain.combine_documents_chain.document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )

        knowledge_chain.return_source_documents = True

        result = knowledge_chain({"query": query})
        self.llm.history[-1][0] = query
        return result, self.llm.history
