import enum

from pydantic import BaseModel
from typing import Dict, Any, List


class VectorStoreStatus(enum.Enum):
    EXPIRED = ('expired', '已过期')
    IN_PROGRESS = ('in_progress', '在处理中')
    COMPLETED = ('completed', '完成')

    def __init__(self, code, desc):
        self.code = code
        self.desc = desc


class FileCountsObject(BaseModel):
    in_progress: int = 0
    completed: int = 0
    cancelled: int = 0
    failed: int = 0
    total: int = 0


class VectorStoreObject(BaseModel):
    id: str
    object: str = 'vector_store'
    vector_store_class: str
    vector_store_config: dict
    created_at: int = 0
    usage_bytes: int = 0
    last_active_at: int = 0
    name: str = None
    status: str = None
    file_counts: FileCountsObject = FileCountsObject()
    metadata: Dict[str, Any] = {}
    last_used_at: int = 0

    class Config:
        orm_mode = True
        from_attributes = True


class ListVectorStoreObject(BaseModel):
    object: str = 'list'
    data: List[VectorStoreObject]
    # first_id: str
    # last_id: str
    # page: int
    # total_pages: int
    # total_results: int


class VectorStoreDeletedObject(BaseModel):
    id: str = None
    object: str = 'vector_store.deleted'
    deleted: bool = True
