from langchain.chains import RetrievalQA
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredFileLoader
from chatglm_llm import ChatGLM
import sentence_transformers
import torch
import os
import readline


# Global Parameters
EMBEDDING_MODEL = "text2vec"
VECTOR_SEARCH_TOP_K = 6
LLM_MODEL = "chatglm-6b"
LLM_HISTORY_LEN = 3
DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# Show reply with source text from input document
REPLY_WITH_SOURCE = True

embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec": "GanymedeNil/text2vec-large-chinese",
}

llm_model_dict = {
    "chatglm-6b-int4-qe": "THUDM/chatglm-6b-int4-qe",
    "chatglm-6b-int4": "THUDM/chatglm-6b-int4",
    "chatglm-6b": "THUDM/chatglm-6b",
}


def init_cfg(LLM_MODEL, EMBEDDING_MODEL, LLM_HISTORY_LEN, V_SEARCH_TOP_K=6):
    global chatglm, embeddings, VECTOR_SEARCH_TOP_K
    VECTOR_SEARCH_TOP_K = V_SEARCH_TOP_K

    chatglm = ChatGLM()
    chatglm.load_model(model_name_or_path=llm_model_dict[LLM_MODEL])
    chatglm.history_len = LLM_HISTORY_LEN

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[EMBEDDING_MODEL],)
    embeddings.client = sentence_transformers.SentenceTransformer(embeddings.model_name,
                                                                  device=DEVICE)


def init_knowledge_vector_store(filepath:str):
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

    vector_store = FAISS.from_documents(docs, embeddings)
    return vector_store


def get_knowledge_based_answer(query, vector_store, chat_history=[]):
    global chatglm, embeddings
    system_template = """基于以下内容，简洁和专业的来回答用户的问题。
    如果无法从中得到答案，请说 "不知道" 或 "没有足够的相关信息"，不要试图编造答案。答案请使用中文。
    ----------------
    {context}
    ----------------
    """
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    chatglm.history = chat_history
    knowledge_chain = RetrievalQA.from_llm(
        llm=chatglm,
        retriever=vector_store.as_retriever(search_kwargs={"k": VECTOR_SEARCH_TOP_K}),
        prompt=prompt
    )

    knowledge_chain.return_source_documents = True

    result = knowledge_chain({"query": query})
    chatglm.history[-1][0] = query
    return result, chatglm.history


if __name__ == "__main__":
    init_cfg(LLM_MODEL, EMBEDDING_MODEL, LLM_HISTORY_LEN)
    vector_store = None
    while not vector_store:
        filepath = input("Input your local knowledge file path 请输入本地知识文件路径：")
        vector_store = init_knowledge_vector_store(filepath)
    history = []
    while True:
        query = input("Input your question 请输入问题：")
        resp, history = get_knowledge_based_answer(query=query,
                                                   vector_store=vector_store,
                                                   chat_history=history)
        if REPLY_WITH_SOURCE:
            print(resp)
        else:
            print(resp["result"])
