import json

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql.functions import now

from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import Base, with_session
from app._types.vector_store_object import VectorStoreStatus, VectorStoreObject, FileCountsObject
from app.utils.base import gen_id

ID_PREFIX = "vs_"


class VectorStoreDbModel(Base, BaseDbModelMixin):
    __tablename__ = "vector_store"

    vs_id = Column(String, index=True)
    name = Column(String, index=True)
    status = Column(String, default=VectorStoreStatus.COMPLETED.code)
    store_type = Column(String)
    vector_store_class = Column(String)
    vector_store_config = Column(JSON, default={})
    file_counts_in_progress = Column(Integer, default=0)
    file_counts_completed = Column(Integer, default=0)
    file_counts_cancelled = Column(Integer, default=0)
    file_counts_failed = Column(Integer, default=0)
    file_counts_total = Column(Integer, default=0)
    metadata_ = Column('metadata', JSON, default={})
    usage_bytes = Column(Integer, default=0)
    last_active_at = Column(DateTime, default=now())
    last_used_at = Column(DateTime, default=now())

    def to_object(self) -> VectorStoreObject:
        if isinstance(self.metadata_, str):
            _metadata = json.loads(self.metadata_)
        else:
            _metadata = self.metadata_
        return VectorStoreObject(
            id=self.vs_id,
            name=self.name,
            status=self.status,
            file_counts=FileCountsObject(
                in_progress=self.file_counts_in_progress,
                completed=self.file_counts_completed,
                cancelled=self.file_counts_cancelled,
                failed=self.file_counts_failed,
                total=self.file_counts_total,
            ),
            vector_store_config=self.vector_store_config,
            metadata=_metadata,
            created_at=self.created_at.timestamp(),
            usage_bytes=self.usage_bytes,
            last_active_at=self.last_active_at.timestamp(),
            last_used_at=self.last_used_at.timestamp(),
        )
