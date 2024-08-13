from app.core.base.base_dao import BaseDao
from app.db.models import CodeResourceDbModel


class CodeResourceDao(BaseDao):
    model = CodeResourceDbModel
