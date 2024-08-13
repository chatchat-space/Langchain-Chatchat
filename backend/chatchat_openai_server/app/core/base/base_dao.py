from sqlalchemy.orm import Session
from typing import Type, List, Dict, Any

from sqlalchemy.sql.functions import now

from app.core.base.base_db_model import BaseDbModelMixin
from app.depends.depend_database import with_session
from app._types.base.pagination import Pagination


class BaseDao:
    model: Type[BaseDbModelMixin]  # 需要在子类中定义具体的模型类

    @staticmethod
    @with_session
    def add(db: Session, add_data) -> Any:
        """创建记录"""
        db.add(add_data)
        db.commit()
        db.refresh(add_data)
        return add_data.to_object()

    @staticmethod
    @with_session
    def get_by_id(db: Session, id_: str) -> Any:
        """根据ID获取记录"""
        instance = db.query(BaseDao.model).filter_by(id=id_, is_deleted=False).first()
        if not instance:
            return None
        return instance.to_object()

    @staticmethod
    @with_session
    def get_by_business_id(db: Session, business_id: str) -> Any:
        """根据业务ID获取记录"""
        # 需要根据业务 ID 计算出实际的数据库 ID，这里只是示例
        instance_id = business_id.split("_", 1)[-1]  # 从业务 ID 中提取实际 ID
        return BaseDao.get_by_id(db=db, id_=instance_id)

    @staticmethod
    @with_session
    def update(db: Session, id_: str, **kwargs) -> Any:
        """更新记录"""
        instance = db.query(BaseDao.model).filter_by(id=id_, is_deleted=False).first()
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.updated_at = now()
        db.commit()
        db.refresh(instance)
        return instance.to_object()

    @staticmethod
    @with_session
    def update_by_business_id(db: Session, business_id: str, **kwargs) -> Any:
        """根据业务 ID 更新记录"""
        instance = BaseDao.get_by_business_id(db=db, business_id=business_id)
        if not instance:
            return None
        return BaseDao.update(db=db, id_=instance["id"], **kwargs)

    @staticmethod
    @with_session
    def delete(db: Session, id_: str) -> Any:
        """软删除记录"""
        instance = db.query(BaseDao.model).filter_by(id=id_).first()
        if not instance:
            return None
        instance.is_deleted = True
        db.commit()
        return instance.to_object()

    @staticmethod
    @with_session
    def delete_by_business_id(db: Session, business_id: str) -> Any:
        """根据业务 ID 软删除记录"""
        instance = BaseDao.get_by_business_id(db=db, business_id=business_id)
        if not instance:
            return None
        return BaseDao.delete(db=db, id_=instance["id"])

    @staticmethod
    @with_session
    def filter(db: Session, filters: Dict[str, Any] = None) -> List[Any]:
        """过滤查询记录"""
        query = db.query(BaseDao.model).filter_by(is_deleted=False)
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(BaseDao.model, key) == value)
        return [instance.to_object() for instance in query.all()]

    @staticmethod
    @with_session
    def paginate(
            db: Session,
            page: int = 1,
            per_page: int = 10,
            filters: Dict[str, Any] = None
    ) -> Pagination:
        """分页查询记录"""
        query = db.query(BaseDao.model).filter_by(is_deleted=False)
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(BaseDao.model, key) == value)
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return Pagination(
            total=total,
            page=page,
            per_page=per_page,
            data=[instance.to_object() for instance in items],
            filters=filters
        )

    @staticmethod
    @with_session
    def bulk_create(db: Session, instances: List[Dict[str, Any]]) -> List[Any]:
        """批量创建记录"""
        objects = [BaseDao.model(**instance) for instance in instances]
        db.bulk_save_objects(objects)
        db.commit()
        return [obj.to_object() for obj in objects]

    @staticmethod
    @with_session
    def bulk_update(db: Session, updates: List[Dict[str, Any]]) -> None:
        """批量更新记录"""
        for update in updates:
            instance = db.query(BaseDao.model).filter_by(id=update['id'], is_deleted=False).first()
            if instance:
                for key, value in update.items():
                    setattr(instance, key, value)
                instance.updated_at = now()
        db.commit()

    @staticmethod
    @with_session
    def hard_delete(db: Session, id_: str) -> None:
        """物理删除记录"""
        instance = db.query(BaseDao.model).filter_by(id=id_).first()
        if instance:
            db.delete(instance)
            db.commit()
