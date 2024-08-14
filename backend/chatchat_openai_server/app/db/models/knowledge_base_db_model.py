from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql.functions import now

from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import Base
from app._types.vector_store_object import VectorStoreStatus

ID_PREFIX = "is_"


class KnowledgeBaseDbModel(Base, BaseDbModelMixin):
    __tablename__ = "knowledge_base"

    index_store_id = Column(String, index=True)
    name = Column(String, index=True)
    index_type = Column(String, index=True)
    rag_process = Column(String)
    rag_process_config = Column(JSON)
    status = Column(String, default=VectorStoreStatus.COMPLETED.code)
    metadata_ = Column('metadata', JSON, default={})
    usage_bytes = Column(Integer, default=0)
    last_active_at = Column(DateTime, default=now())
    last_used_at = Column(DateTime, default=now())

