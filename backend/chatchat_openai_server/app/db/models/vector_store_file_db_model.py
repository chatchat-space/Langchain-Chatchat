import json

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql.functions import now

from app.extensions.ext_database import Base
from app.types.vector_store_file_object import VectorStoreFileStatus, VectorStoreFileObject
from app.types.vector_store_object import VectorStoreObject, FileCountsObject
from app.utils.base import gen_id

ID_PREFIX = "file_"


class VectorStoreFileDbModel(Base):
    __tablename__ = "vector_store_file"

    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    file_id = Column(String, index=True, default=lambda: gen_id(ID_PREFIX))
    usage_bytes = Column(Integer)
    created_at = Column(DateTime, default=now())
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
