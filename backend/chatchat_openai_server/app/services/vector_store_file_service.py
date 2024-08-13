from app._types.vector_store_file_object import VectorStoreFileObject
from app.db.dao.vector_store_file_dao import VectorStoreFileDao
from app.depends.depend_mq import mq_service
from app.tasks.file_to_vs_store_task import file_to_vs_store_task


class VectorStoreFileService:
    @staticmethod
    def create_vector_store_file(vector_store_id: str
                                 , file_id: str):
        return VectorStoreFileDao.create_vector_store_file(vector_store_id, file_id)

    @staticmethod
    def process_vector_store_file(vector_store_id: str, file_id: str) -> VectorStoreFileObject:
        vector_store_file = VectorStoreFileService.retrieve_vector_store_file(vector_store_id, file_id)
        # mq_service.enqueue(vector_store_file)
        file_to_vs_store_task.delay(vector_store_id, file_id)
        return vector_store_file

    @staticmethod
    def list_vector_store_files(vector_store_id: str):
        return VectorStoreFileDao.list_vector_store_files(vector_store_id)

    @staticmethod
    def retrieve_vector_store_file(vector_store_id: str, file_id: str) -> VectorStoreFileObject:
        return VectorStoreFileDao.retrieve_vector_store_file(vector_store_id, file_id)

    @staticmethod
    def delete_vector_store_file(vector_store_id: str, file_id: str):
        return VectorStoreFileDao.delete_vector_store_file(vector_store_id, file_id)
