from typing import Any, List  
from chatchat.server.file_rag.retrievers.base import BaseRetrieverService  
from langchain.retrievers import TimeWeightedVectorStoreRetriever  
from langchain.vectorstores import VectorStore  
from langchain_core.retrievers import BaseRetriever  
  
class TimeWeightedVectorstoreRetrieverService(BaseRetrieverService):  
    def __init__(  
        self,  
        retriever: BaseRetriever = None,  
        top_k: int = 5,  
        decay_rate: float = 0.01  
    ):  
        self.retriever = retriever  
        self.top_k = top_k  
        self.decay_rate = decay_rate  
  
    @classmethod  
    def from_vectorstore(  
        cls,  
        vectorstore: VectorStore,  
        decay_rate: float,  
        top_k: int,  
    ) -> "TimeWeightedVectorstoreRetrieverService":  
        if not isinstance(decay_rate, (int, float)):  
            raise ValueError("decay_rate must be a float.")  
        retriever = TimeWeightedVectorStoreRetriever(  
            vectorstore=vectorstore,  
            decay_rate=decay_rate,  
            k=top_k  
        )  
        return cls(retriever=retriever)  
  
    def get_related_documents(self, query: str) -> List[Any]:  
        if self.retriever is None:  
            raise ValueError("Retriever is not initialized.")  
        try:  
            return self.retriever.get_relevant_documents(query)[:self.top_k]  
        except Exception as e:  
            raise ValueError(f"Error retrieving documents: {e}")  