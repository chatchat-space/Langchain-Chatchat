from app.db.dao.vector_store_file_dao import VectorStoreFileDao


class VectorStoreFileService:
    @staticmethod
    def create_vector_store_file(vector_store_id: str
                                 , file_id: str):
        return VectorStoreFileDao.create_vector_store_file(vector_store_id, file_id)

    @staticmethod
    def list_vector_store_files(vector_store_id: str):
        return VectorStoreFileDao.list_vector_store_files(vector_store_id)

    @staticmethod
    def retrieve_vector_store_file(vector_store_id: str, file_id: str):
        return VectorStoreFileDao.retrieve_vector_store_file(vector_store_id, file_id)

    @staticmethod
    def delete_vector_store_file(vector_store_id: str, file_id: str):
        return VectorStoreFileDao.delete_vector_store_file(vector_store_id, file_id)
