from sqlalchemy.orm import Session

from app.db.models import VectorStoreFileDbModel
from app.extensions.ext_database import with_session
from app.types.vector_store_file_object import VectorStoreFileStatus, VectorStoreFileDeletedObject, \
    VectorStoreFileObject, ListVectorStoreFileObject


class VectorStoreFileDao:
    @staticmethod
    @with_session
    def create_vector_store_file(db: Session, vector_store_id: str, file_id: str) -> VectorStoreFileObject:
        vs_file = VectorStoreFileDbModel(
            # org_id=request.org_id,
            file_id=file_id,
            usage_bytes=0,
            vector_store_id=vector_store_id,
            status=VectorStoreFileStatus.IN_PROGRESS.code,
            # metadata_=request.metadata_
        )

        db.add(vs_file)
        db.commit()
        db.refresh(vs_file)
        return vs_file.to_object()

    @staticmethod
    @with_session
    def list_vector_store_files(db: Session, vector_store_id: str):
        vs_files = db.query(VectorStoreFileDbModel).filter(
            VectorStoreFileDbModel.vector_store_id == vector_store_id).all()
        return ListVectorStoreFileObject(
            data=[vs_file.to_object() for vs_file in vs_files]
        )

    @staticmethod
    @with_session
    def retrieve_vector_store_file(db: Session, vector_store_id: str, file_id: str):
        vs_file = db.query(VectorStoreFileDbModel).filter(VectorStoreFileDbModel.vector_store_id == vector_store_id,
                                                          VectorStoreFileDbModel.file_id == file_id).first()
        if not vs_file:
            return None
        return vs_file.to_object()

    @staticmethod
    @with_session
    def delete_vector_store_file(db: Session, vector_store_id: str, file_id: str):
        vs_file = db.query(VectorStoreFileDbModel).filter(VectorStoreFileDbModel.vector_store_id == vector_store_id,
                                                          VectorStoreFileDbModel.file_id == file_id).first()
        if not vs_file:
            return None
        db.delete(vs_file)
        db.commit()
        return VectorStoreFileDeletedObject(id=vs_file.file_id)
