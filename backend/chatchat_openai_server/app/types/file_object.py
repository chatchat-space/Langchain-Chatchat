import enum
from typing import List

from pydantic import BaseModel


class FilePurpose(enum.Enum):
    ASSISTANTS = ('assistants', '对assistant和Message文件使用')
    VISION = ('vision', '为助手的图像文件输入')
    BATCH = ('batch', '用于批处理API')
    FINE_TUNE = ('fine-tune', '微调使用')

    def __init__(self, code, desc):
        self.code = code
        self.desc = desc


class FileObject(BaseModel):
    id: str
    object: str = 'file'
    bytes: int
    created_at: int
    filename: str
    purpose: str
    metadata: dict
    store_file_path: str
    org_id: str = None

    class Config:
        orm_mode = True


class ListFileObject(BaseModel):
    object: str = 'list'
    data: List[FileObject]


class FileDeletedObject(BaseModel):
    id: str = None
    object: str = 'file.deleted'
    deleted: bool = True
