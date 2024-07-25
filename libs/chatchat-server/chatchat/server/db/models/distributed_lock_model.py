from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, func, Boolean

from chatchat.server.db.base import Base


class DistributedLockModel(Base):
    __tablename__ = 'distributed_lock'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="知识库ID")
    lock_key = Column(String, unique=True, nullable=False, comment="锁的key")
    owner = Column(String, comment="拥有者")
    lock_status = Column(Boolean, nullable=False, default=False, comment="锁的状态")
    start_lock_time = Column(DateTime, default=func.now(), comment="开始加锁时间")
    update_lock_time = Column(DateTime, nullable=True, comment="更新锁的时间")
    expire_time = Column(DateTime, nullable=True, comment="锁的过期时间")
