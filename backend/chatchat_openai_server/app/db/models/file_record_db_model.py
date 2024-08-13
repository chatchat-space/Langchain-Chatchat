import json

from sqlalchemy import Column, Integer, String, JSON

from app.core.base.base_db_model import BaseDbModelMixin
from app._types.file_object import FileObject
from app.depends.depend_database import Base
from app.utils.base import gen_id

ID_PREFIX = "file_"


class FileRecordDbModel(Base, BaseDbModelMixin):
    __tablename__ = "file_record"

    file_id = Column(String, index=True, default=lambda: gen_id(ID_PREFIX))
    filename = Column(String)
    extension = Column(String)
    store_file_path = Column(String)
    bytes = Column(Integer)
    purpose = Column(String)
    metadata_ = Column('metadata', JSON, default={})

    def to_object(self) -> FileObject:
        if isinstance(self.metadata_, str):
            _metadata = json.loads(self.metadata_)
        else:
            _metadata = self.metadata_
        return FileObject(
            id=self.file_id,
            filename=self.filename,
            bytes=self.bytes,
            created_at=self.created_at.timestamp(),
            purpose=self.purpose,
            metadata=_metadata,
            store_file_path=self.store_file_path,
            org_id=self.org_id,
        )
