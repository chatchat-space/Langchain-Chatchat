from datetime import datetime

from pydantic import BaseModel

from app._types.base.base_enum import BaseEnum


class ResourceTypeEnum(BaseEnum):
    ...


class CodeResourceObject(BaseModel):
    id: str
    org_id: str
    resource_id: str
    resource_name: str
    resource_type: str
    main_resource_file: str
    main_class: str
    pkg_full_name: str
    store_path: str
    code_content: str
    metadata: dict

