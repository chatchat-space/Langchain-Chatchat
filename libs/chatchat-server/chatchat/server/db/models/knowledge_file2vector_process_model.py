from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, func

from chatchat.server.db.base import Base


class KnowledgeFile2VectorProcessModel(Base):
    file_id = Column(String(50), comment="文件id")
    status = Column(String(20), comment="处理状态")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    deleted = Column(Boolean, default=False, comment="是否删除")