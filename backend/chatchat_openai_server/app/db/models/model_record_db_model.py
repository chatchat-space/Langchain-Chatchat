import json

from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql.functions import now

from app.extensions.ext_database import Base
from app.types.model_object import ModelObject
from app.utils.base import gen_id


class ModelRecordDbModel(Base):
    __tablename__ = "model_record"

    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    model_id = Column(String, index=True)
    model_name = Column(String)
    model_platform = Column(String)
    created = Column(DateTime, default=now())
    owned_by = Column(String)
    metadata_ = Column('metadata', JSON, default={})

    def to_object(self) -> ModelObject:
        if isinstance(self.metadata_, str):
            _metadata = json.loads(self.metadata_)
        else:
            _metadata = self.metadata_
        return ModelObject(
            org_id=self.org_id,
            id=self.model_id,
            created=self.created,
            owned_by=self.owned_by,
            metadata=_metadata,
        )
