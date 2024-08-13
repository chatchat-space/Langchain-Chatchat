from sqlalchemy import Column, String, JSON

from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import Base
from app._types.code_resource_object import CodeResourceObject
from app.utils.base import gen_id


class ConfigResourceDbModel(Base, BaseDbModelMixin):
    __tablename__ = "config_resource"

    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    resource_id = Column(String, index=True, default=lambda: gen_id())
    resource_name = Column(String, index=True, unique=True)
    resource_type = Column(String)  # vs配置资源
    config_data = Column(String)

    # def to_object(self):
    #     return CodeResourceObject(
    #         **self.__dict__
    #     )
