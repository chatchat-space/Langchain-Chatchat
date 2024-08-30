from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import Base


class AiModelDbModel(Base, BaseDbModelMixin):

    __tablename__ = "ai_model"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, index=True)
    model_name = "ai_model"
    import_type = "local"

