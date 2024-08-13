import json

from sqlalchemy import Column, Integer, String, JSON

from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import Base
from app._types.vector_store_file_object import VectorStoreFileStatus, VectorStoreFileObject
from app.utils.base import gen_id

ID_PREFIX = "file_"


class VectorStoreFileDbModel(Base, BaseDbModelMixin):
    __tablename__ = "vector_store_file"

    file_id = Column(String, index=True, default=lambda: gen_id(ID_PREFIX))
    usage_bytes = Column(Integer)
    vector_store_id = Column(String, nullable=False)
    status = Column(String, default=VectorStoreFileStatus.IN_PROGRESS)
    last_error = Column(String, default="")
    metadata_ = Column('metadata', JSON, default={})

    def to_object(self) -> VectorStoreFileObject:
        if isinstance(self.metadata_, str):
            _metadata = json.loads(self.metadata_)
        else:
            _metadata = self.metadata_
        return VectorStoreFileObject(
            id=self.file_id,
            org_id=self.org_id,
            usage_bytes=self.usage_bytes,
            created_at=self.created_at.timestamp(),
            vector_store_id=self.vector_store_id,
            status=self.status,
            last_error=self.last_error,
            metadata=_metadata,
        )
