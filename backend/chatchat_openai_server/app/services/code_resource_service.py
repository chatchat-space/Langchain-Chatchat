from app.db.dao.code_resource_dao import CodeResourceDao


class CodeResourceService:
    @staticmethod
    def add(item):
        return CodeResourceDao.add(item)
