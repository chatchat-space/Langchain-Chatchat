from typing import List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql.functions import now

from app.utils.base import gen_id


class BaseDbModelMixin:
    id = Column(String, primary_key=True, index=True, default=lambda: gen_id())
    org_id = Column(String, default="")
    created_at = Column(DateTime, default=now())  # 记录的创建时间
    updated_at = Column(DateTime, default=now(), onupdate=now())  # 记录的更新时间
    created_by = Column(String)  # 创建者
    updated_by = Column(String)  # 修改者
    deleted = Column(Boolean, default=False)  # 软删除标志
    version = Column(Integer, default=1)  # 版本号，初始值为1

    def to_object(self):
        return self.__dict__

    @classmethod
    def create(cls, db_session, **kwargs):
        """创建记录"""
        instance = cls(**kwargs)
        db_session.add(instance)
        db_session.commit()
        db_session.refresh(instance)
        return instance

    @classmethod
    def get_by_id(cls, db_session, id_):
        """根据ID获取记录"""
        return db_session.query(cls).filter_by(id=id_, deleted=False).first()

    @classmethod
    def update(cls, db_session, id_, **kwargs):
        """更新记录"""
        instance = db_session.query(cls).filter_by(id=id_, deleted=False).first()
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.updated_at = now()
        db_session.commit()
        db_session.refresh(instance)
        return instance

    @classmethod
    def delete(cls, db_session, id_):
        """软删除记录"""
        instance = db_session.query(cls).filter_by(id=id_).first()
        if not instance:
            return None
        instance.deleted = True
        db_session.commit()
        return instance

    @classmethod
    def filter(cls, db_session, filters: Dict[str, Any] = None):
        """过滤查询记录"""
        query = db_session.query(cls).filter_by(deleted=False)
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(cls, key) == value)
        return query.all()

    @classmethod
    def paginate(cls, db_session, page: int = 1, per_page: int = 10, filters: Dict[str, Any] = None):
        """分页查询记录"""
        query = db_session.query(cls).filter_by(deleted=False)
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(cls, key) == value)
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {
            'total': total,
            'page': page,
            'per_page': per_page,
            'items': items
        }

    @classmethod
    def bulk_create(cls, db_session, instances: List[Dict[str, Any]]):
        """批量创建记录"""
        objects = [cls(**instance) for instance in instances]
        db_session.bulk_save_objects(objects)
        db_session.commit()
        return objects

    @classmethod
    def bulk_update(cls, db_session, updates: List[Dict[str, Any]]):
        """批量更新记录"""
        for update in updates:
            instance = db_session.query(cls).filter_by(id=update['id'], deleted=False).first()
            if instance:
                for key, value in update.items():
                    setattr(instance, key, value)
                instance.updated_at = now()
        db_session.commit()

    @classmethod
    def hard_delete(cls, db_session, id_):
        """物理删除记录"""
        instance = db_session.query(cls).filter_by(id=id_).first()
        if instance:
            db_session.delete(instance)
            db_session.commit()
