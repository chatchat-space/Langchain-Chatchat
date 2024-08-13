from fastapi import UploadFile, File

from app.db.dao.file_record_dao import FileRecordDao
from app.depends.depend_storage import storage
from app.services.exceptions.file_exception import FileNotExistsException
from app._types.file_object import FilePurpose, FileObject, ListFileObject, FileDeletedObject
from app.utils.base import gen_id, get_valid_var


class FileService:

    @staticmethod
    def upload_file(
            file: UploadFile = File(...),
            metadata: dict = {},
            purpose: str = FilePurpose.ASSISTANTS.code,
    ) -> FileObject:
        try:
            file_id = gen_id('file_')
            filename = f"{file_id}_{file.filename}"
            store_file_path, file_size = storage.save_file(filename, file.file)
            file_record = FileRecordDao.add_file_record(
                file_id=file_id,
                filename=file.filename,
                file_size=file_size,
                store_file_path=store_file_path,
                metadata=metadata,
                purpose=purpose
            )
            return file_record
        finally:
            file.file.close()

    @staticmethod
    def file_list(purpose) -> ListFileObject:
        return FileRecordDao.file_list(purpose)

    @staticmethod
    def retrieve_file(file_id: str) -> FileObject:
        file_object = FileRecordDao.retrieve_file(file_id)
        return get_valid_var(file_object)

    @staticmethod
    def delete_file(file_id: str) -> FileDeletedObject:
        file_deleted_object = FileRecordDao.delete_file(file_id=file_id)
        return get_valid_var(file_deleted_object)

    @staticmethod
    def retrieve_file_content(file_id: str):
        file_object: FileObject = FileRecordDao.get_file_by_id(file_id)
        if not file_object:
            raise FileNotExistsException()
        return storage.read_file_content(file_object)
