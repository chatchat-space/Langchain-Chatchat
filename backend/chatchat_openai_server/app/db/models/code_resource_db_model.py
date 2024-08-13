from sqlalchemy import Column, String, JSON

from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import Base
from app._types.code_resource_object import CodeResourceObject
from app.utils.base import gen_id


class CodeResourceDbModel(Base, BaseDbModelMixin):
    __tablename__ = "code_resource"

    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    resource_id = Column(String, index=True, default=lambda: gen_id("code_"))
    resource_name = Column(String, index=True, unique=True)
    resource_type = Column(String)
    main_resource_file = Column(String)
    main_class = Column(String)
    pkg_full_name = Column(String)
    store_path = Column(String)
    code_content = Column(String)
    metadata_ = Column('metadata', JSON, default={})

    def to_object(self):
        return CodeResourceObject(
                **self.__dict__
        )
