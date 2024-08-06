import json
from typing import Optional

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.db.models.vector_store_db_model import VectorStoreDbModel
from app.extensions.ext_database import with_session
from app.types.vector_store_object import VectorStoreObject, ListVectorStoreObject, VectorStoreDeletedObject, \
    FileCountsObject
from app.utils.base import gen_id

ID_PREFIX = "vs_"


class VectorStoreDao:
    @staticmethod
    @with_session
    def create_vector_store(session,
                            name: str,
                            vs_id=None,
                            metadata={},
                            ):
        if vs_id is None:
            vs_id = gen_id(ID_PREFIX)
        new_vector_store = VectorStoreDbModel(name=name,
                                              vs_id=vs_id,
                                              metadata_=metadata)
        session.add(new_vector_store)
        session.commit()
        session.refresh(new_vector_store)
        file_counts = FileCountsObject()
        if new_vector_store.metadata_ and isinstance(new_vector_store.metadata_, str):
            _metadata = json.loads(new_vector_store.metadata_)
        else:
            _metadata = new_vector_store.metadata_
        return VectorStoreObject(
            id=new_vector_store.vs_id,
            name=new_vector_store.name,
            status=new_vector_store.status,
            metadata=_metadata,
            file_counts=file_counts,
            created_at=new_vector_store.created_at.timestamp(),
            last_active_at=new_vector_store.last_active_at.timestamp(),
            last_used_at=new_vector_store.last_used_at.timestamp(),
            usage_bytes=new_vector_store.usage_bytes,
        )

    @staticmethod
    @with_session
    def list_vector_store(
            db: Session,
            limit: int = 20,
            order: str = "desc",
            after: Optional[str] = None,
            before: Optional[str] = None,

    ):
        query = db.query(VectorStoreDbModel)

        if order == "asc":
            query = query.order_by(asc(VectorStoreDbModel.created_at))
        else:
            query = query.order_by(desc(VectorStoreDbModel.created_at))

        if after:
            query = query.filter(VectorStoreDbModel.id > after)
        if before:
            query = query.filter(VectorStoreDbModel.id < before)

        vector_stores = query.limit(limit).all()
        return ListVectorStoreObject(
            data=[vector_store.to_object() for vector_store in vector_stores],
        )

    @staticmethod
    @with_session
    def retrieve_vector_store(db: Session, vector_store_id: str):
        vector_store = db.query(VectorStoreDbModel).filter(VectorStoreDbModel.vs_id == vector_store_id).first()
        if not vector_store:
            return None
        return vector_store.to_object()

    @staticmethod
    @with_session
    def modify_vector_store(db: Session, vector_store_id: str, update: dict):
        vector_store = db.query(VectorStoreDbModel).filter(VectorStoreDbModel.vs_id == vector_store_id).first()
        if not vector_store:
            return None
        for key, value in update.dict(exclude_unset=True).items():
            setattr(vector_store, key, value)
        return vector_store.to_object()

    @staticmethod
    @with_session
    def delete_vector_store(db: Session, vector_store_id: str):
        vector_store = db.query(VectorStoreDbModel).filter(VectorStoreDbModel.vs_id == vector_store_id).first()
        if not vector_store:
            return None
        db.commit()
        return VectorStoreDeletedObject(id=vector_store.vs_id)
