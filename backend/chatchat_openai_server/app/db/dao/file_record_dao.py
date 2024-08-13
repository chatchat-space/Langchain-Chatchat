from sqlalchemy.orm import Session

from app.db.models import FileRecordDbModel
from app.depends.depend_database import with_session
from app._types.file_object import FilePurpose, ListFileObject, FileObject, FileDeletedObject


class FileRecordDao:
    @staticmethod
    @with_session
    def add_file_record(
            db: Session,
            file_id: str,
            filename: str,
            file_size: int,
            store_file_path: str,
            metadata: dict = {},
            purpose: str = FilePurpose.ASSISTANTS.code,
    ) -> FileObject:
        file_record = FileRecordDbModel(
            file_id=file_id,
            filename=filename,
            bytes=file_size,
            store_file_path=store_file_path,
            purpose=purpose,
            metadata_=metadata
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        return file_record.to_object()

    @staticmethod
    @with_session
    def file_list(db: Session, purpose) -> ListFileObject:
        file_object_list = [file_record.to_object() for file_record in
                            db.query(FileRecordDbModel).filter(FileRecordDbModel.purpose == purpose).all()]
        return ListFileObject(
            data=file_object_list
        )

    @staticmethod
    @with_session
    def retrieve_file(db: Session, file_id: str) -> FileObject:
        file_record = db.query(FileRecordDbModel).filter(FileRecordDbModel.file_id == file_id).first()
        if not file_record:
            return None
        return file_record.to_object()

    @staticmethod
    @with_session
    def delete_file(db: Session, file_id: str) -> FileDeletedObject:
        file_record = db.query(FileRecordDbModel).filter(FileRecordDbModel.file_id == file_id).first()
        if not file_record:
            return None
        db.delete(file_record)
        return FileDeletedObject(id=file_id)

    @staticmethod
    @with_session
    def get_file_by_id(db: Session, file_id: str) -> FileObject:
        record = db.query(FileRecordDbModel).filter(FileRecordDbModel.file_id == file_id).first()
        if not record:
            return None
        return record.to_object()
