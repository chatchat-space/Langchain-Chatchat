import json

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql.functions import now

from app.extensions.ext_database import Base, with_session
from app.types.vector_store_object import VectorStoreStatus, VectorStoreObject, FileCountsObject
from app.utils.base import gen_id

ID_PREFIX = "is_"


class IndexStoreDbModel(Base):
    __tablename__ = "index_store"

    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    index_store_id = Column(String, index=True)
    name = Column(String, index=True)
    index_type = Column(String)  # 向量 全文检索
    index_builder = Column(String)
    index_builder_config = Column(JSON)
    status = Column(String, default=VectorStoreStatus.COMPLETED.code)
    file_counts_in_progress = Column(Integer, default=0)
    file_counts_completed = Column(Integer, default=0)
    file_counts_cancelled = Column(Integer, default=0)
    file_counts_failed = Column(Integer, default=0)
    file_counts_total = Column(Integer, default=0)
    metadata_ = Column('metadata', JSON, default={})
    created_at = Column(DateTime, default=now())
    usage_bytes = Column(Integer, default=0)
    last_active_at = Column(DateTime, default=now())
    last_used_at = Column(DateTime, default=now())
