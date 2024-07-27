from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, func, Boolean

from chatchat.server.db.base import Base


class KbFileRagTask(Base):
    __tablename__ = 'kb_file_rag_task'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="id")
    field_id = Column(String, comment="文件id")
    #  0: 未开始 1: 进行中 2: 已完成 3: 失败 4: 待取消 5: 已经取消
    task_status = Column(String, comment="任务状态")
    version = Column(Integer, default=0, comment="版本号")
    process_start_time = Column(DateTime, comment="处理开始时间")
    process_end_time = Column(DateTime, comment="处理结束时间")
    process_result = Column(String, comment="处理结果")
    create_time = Column(DateTime, comment="创建时间")
    update_time = Column(DateTime, comment="更新时间")
