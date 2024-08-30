from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import Base


class AiModelProviderDbModel(Base, BaseDbModelMixin):
    provider_name: str
    import_type = "local"
