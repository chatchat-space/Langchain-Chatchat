from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ChatVectorDBChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredFileLoader
from chatglm_llm import ChatGLM

embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec": "GanymedeNil/text2vec-large-chinese"
}
chatglm = ChatGLM()


def init_knowledge_vector_store(filepath):
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict["text2vec"], )
    loader = UnstructuredFileLoader(filepath, mode="elements")
    docs = loader.load()

    vector_store = FAISS.from_documents(docs, embeddings)
    return vector_store


def get_knowledge_based_answer(query, vector_store, chat_history=[]):
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

    condese_propmt_template = """任务: 给一段对话和一个后续问题，将后续问题改写成一个独立的问题。确保问题是完整的，没有模糊的指代。
    ----------------
    聊天记录：
    {chat_history}
    ----------------
    后续问题：{question}
    ----------------
    改写后的独立、完整的问题："""
    new_question_prompt = PromptTemplate.from_template(condese_propmt_template)
    chatglm.history = chat_history
    knowledge_chain = ChatVectorDBChain.from_llm(
        llm=chatglm,
        vectorstore=vector_store,
        qa_prompt=prompt,
        condense_question_prompt=new_question_prompt,
    )

    knowledge_chain.return_source_documents = True
    knowledge_chain.top_k_docs_for_context = 10

    result = knowledge_chain({"question": query, "chat_history": chat_history})
    return result, chatglm.history


if __name__ == "__main__":
    filepath = input("Input your local knowledge file path 请输入本地知识文件路径：")
    vector_store = init_knowledge_vector_store(filepath)
    history = []
    while True:
        query = input("Input your question 请输入问题：")
        resp, history = get_knowledge_based_answer(query=query,
                                                   vector_store=vector_store,
                                                   chat_history=history)
        print(resp)
