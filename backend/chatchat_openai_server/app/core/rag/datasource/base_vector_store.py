from abc import abstractmethod
from typing import List, Union

from app._types.vector_store_file_object import VectorStoreFileObject
from app.core.rag._types.base_document import BaseDocument


class VectorStoreType:
    MILVUS = "milvus"


class BaseVectorStore:

    @abstractmethod
    def type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def extract_documents_from_file(self, vector_store_file: VectorStoreFileObject) -> List[BaseDocument]:
        raise NotImplementedError

    @abstractmethod
    def add_document(self, document: BaseDocument):
        raise NotImplementedError

    @abstractmethod
    def add_documents(self, documents: List[BaseDocument]):
        raise NotImplementedError

    @abstractmethod
    def get_document_by_id(self, _id: Union[str, int]):
        raise NotImplementedError

    @abstractmethod
    def get_document_by_ids(self, _ids: List[Union[str, int]]) -> List[BaseDocument]:
        raise NotImplementedError

    @abstractmethod
    def delete_document_by_id(self, _id: Union[str, int]):
        raise NotImplementedError

    @abstractmethod
    def delete_documents_by_ids(self, _ids: List[Union[str, int]]):
        raise NotImplementedError

    @abstractmethod
    def delete_all_documents(self):
        raise NotImplementedError

    @abstractmethod
    def similarity_search(self, query: str, k: int = 10) -> List[BaseDocument]:
        raise NotImplementedError
