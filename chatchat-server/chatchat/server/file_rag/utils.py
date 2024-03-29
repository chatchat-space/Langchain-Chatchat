from chatchat.server.file_rag.retrievers import BaseRetrieverService, VectorstoreRetrieverService

Retrivals = {
    "vectorstore": VectorstoreRetrieverService,
}

def get_Retriever(type: str = "vectorstore") -> BaseRetrieverService:
    return Retrivals[type]