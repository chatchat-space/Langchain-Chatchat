import json

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql.functions import now

from app.extensions.ext_database import Base
from app.types.file_object import FileObject
from app.utils.base import gen_id

ID_PREFIX = "file_"


class FileRecordDbModel(Base):
    __tablename__ = "file_record"

    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    file_id = Column(String, index=True, default=lambda: gen_id(ID_PREFIX))
    filename = Column(String, index=True)
    store_file_path = Column(String)
    bytes = Column(Integer)
    purpose = Column(String)
    metadata_ = Column('metadata', JSON, default={})
    created_at = Column(DateTime, default=now())

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
