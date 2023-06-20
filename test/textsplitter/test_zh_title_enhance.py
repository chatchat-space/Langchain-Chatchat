from configs.model_config import *
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import nltk
from vectorstores import MyFAISS
from chains.local_doc_qa import load_file


nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                            "knowledge_base", "samples", "content", "test.txt")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[EMBEDDING_MODEL],
                                       model_kwargs={'device': EMBEDDING_DEVICE})

    docs = load_file(filepath, using_zh_title_enhance=True)
    vector_store = MyFAISS.from_documents(docs, embeddings)
    query = "指令提示技术有什么示例"
    search_result = vector_store.similarity_search(query)
    print(search_result)
    pass
