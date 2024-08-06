from typing import Optional

from app.db.dao.vector_store_dao import VectorStoreDao


class VectorStoreService:

    @staticmethod
    def create_vector_store(name, metadata):
        return VectorStoreDao.create_vector_store(name
                                                  , metadata=metadata)

    @staticmethod
    def list_vector_store(
            limit: int = 20,
            order: str = "desc",
            after: Optional[str] = None,
            before: Optional[str] = None,

    ):
        return VectorStoreDao.list_vector_store(limit, order, after, before)

    @staticmethod
    def retrieve_vector_store(vector_store_id: str):
        return VectorStoreDao.retrieve_vector_store(vector_store_id)

    @staticmethod
    def modify_vector_store(vector_store_id: str, update):
        return VectorStoreDao.modify_vector_store(vector_store_id, update)

    @staticmethod
    def delete_vector_store(vector_store_id: str):
        return VectorStoreDao.delete_vector_store(vector_store_id)
