import enum
from typing import Optional, List

from pydantic import BaseModel


class IndexStoreFileStatus(enum.Enum):
    IN_PROGRESS = ("in_progress", "正在进行中")
    COMPLETED = ("completed", "完成")
    FAILED = ("failed", "失败的")
    CANCELLED = ("cancelled", "取消的")
    DELETED = ("deleted", "删除")

    def __init__(self, code, desc):
        self.code = code
        self.desc = desc


class StaticStrategyObject(BaseModel):
    max_chunk_size_tokens: int
    chunk_overlap_tokens: int


class ChunkingStrategyObject(BaseModel):
    type: str
    static: StaticStrategyObject


class IndexStoreFileObject(BaseModel):
    id: str
    org_id: str
    object: str = 'index_store.file'
    usage_bytes: int
    created_at: int
    vector_store_id: str
    status: str
    last_error: str
    # chunking_strategy: StaticStrategyObject = None
    metadata: dict

    class Config:
        orm_mode = True


class ListVectorStoreFileObject(BaseModel):
    object: str = 'list'
    data: List[IndexStoreFileObject]
    first_id: str = None
    last_id: str = None
    has_more: bool = False


class IndexStoreFileDeletedObject(BaseModel):
    id: str = None
    object: str = 'vector_store.file.deleted'
    deleted: bool = True
