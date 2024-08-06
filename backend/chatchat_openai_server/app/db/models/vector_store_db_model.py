import json

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql.functions import now

from app.extensions.ext_database import Base, with_session
from app.types.vector_store_object import VectorStoreStatus, VectorStoreObject, FileCountsObject
from app.utils.base import gen_id

ID_PREFIX = "vs_"


class VectorStoreDbModel(Base):
    __tablename__ = "vector_store"

    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    vs_id = Column(String, index=True)
    name = Column(String, index=True)
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
            metadata=_metadata,
            created_at=self.created_at.timestamp(),
            usage_bytes=self.usage_bytes,
            last_active_at=self.last_active_at.timestamp(),
            last_used_at=self.last_used_at.timestamp(),
        )


@with_session
def db_create_vector_store(session,
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
