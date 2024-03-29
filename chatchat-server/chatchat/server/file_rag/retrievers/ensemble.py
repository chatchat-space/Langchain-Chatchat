from chatchat.server.file_rag.retrievers.base import BaseRetrieverService
from langchain.vectorstores import VectorStore
from langchain_core.retrievers import BaseRetriever
from langchain.retrievers import BM25Retriever, EnsembleRetriever


class EnsembleRetrieverService(BaseRetrieverService):
    def do_init(
            self,
            retriever: BaseRetriever = None,
            top_k: int = 5,
    ):
        self.vs = None
        self.top_k = top_k
        self.retriever = None


    @staticmethod
    def from_vectorstore(
            vectorstore: VectorStore,
            top_k: int,
            score_threshold: int or float,
    ):
        faiss_retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": score_threshold,
                "k": top_k
            }
        )
        from cutword import Cutter
        cutter = Cutter()
        docs = list(vectorstore.docstore._dict.values())
        bm25_retriever = BM25Retriever.from_documents(
            docs,
            preprocess_func=cutter.cutword
        )
        bm25_retriever.k = top_k
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
        )
        return EnsembleRetrieverService(retriever=ensemble_retriever)

    def get_related_documents(self, query: str):
        self.retriever.get_relevant_documents(query)[:self.top_k]
