from chatchat.server.file_rag.retrievers import (
    BaseRetrieverService,
    VectorstoreRetrieverService,
    EnsembleRetrieverService,
)

Retrivals = {
    "vectorstore": VectorstoreRetrieverService,
    "ensemble": EnsembleRetrieverService,
}

def get_Retriever(type: str = "vectorstore") -> BaseRetrieverService:
    return Retrivals[type]