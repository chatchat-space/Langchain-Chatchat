from configs.model_config import *
from chains.local_doc_qa import LocalDocQA
import os
import nltk

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

# Show reply with source text from input document
REPLY_WITH_SOURCE = True

if __name__ == "__main__":
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(embedding_model="ImageBind")
    query = "本项目使用的embedding模型是什么，消耗多少显存"
    vs_path = "/home/ubuntu/langchain-ChatGLM/vector_store/test_FAISS_20230526_181937"
    last_print_len = 0
    for resp, history in local_doc_qa.get_knowledge_based_answer(query=query,
                                                                 vs_path=vs_path,
                                                                 chat_history=[],
                                                                 streaming=True):
        logger.info(resp["result"][last_print_len:])
        last_print_len = len(resp["result"])
    source_text = [f"""出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n"""
                   # f"""相关度：{doc.metadata['score']}\n\n"""
                   for inum, doc in
                   enumerate(resp["source_documents"])]
    logger.info("\n\n" + "\n\n".join(source_text))
    pass