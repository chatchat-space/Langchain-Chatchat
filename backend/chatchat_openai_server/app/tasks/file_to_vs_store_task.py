from celery import shared_task
from langchain_core.documents import Document

from app._types.vector_store_file_object import VectorStoreFileObject
from app._types.vector_store_object import VectorStoreObject
from app.db.dao.vector_store_dao import VectorStoreDao
from app.db.dao.vector_store_file_dao import VectorStoreFileDao
from app.depends.depend_celery import celery_app


@celery_app.task
def file_to_vs_store_task(vector_store_id, file_id):
    vector_store: VectorStoreObject = VectorStoreDao.retrieve_vector_store(vector_store_id)
    vector_store_file: VectorStoreFileObject = VectorStoreFileDao.retrieve_vector_store_file(
        vector_store_id=vector_store_id,
        file_id=file_id)
    from app.services.file_service import FileService
    file_content = FileService.retrieve_file_content(vector_store_file.id)
    # text_splitter = ChineseRecursiveTextSplitter(
    #     keep_separator=True,
    #     is_separator_regex=True,
    #     chunk_size=20,
    #     chunk_overlap=0
    # )
    # documents = text_splitter.split_documents([Document(page_content=file_content)])
    # print(vector_store.vector_store_config)
    # print(documents)
