from datetime import datetime

from pydantic.v1 import BaseModel


class TaskStatus:
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELED = "Canceled"
    CANCELED_MANUALLY = "Canceled Manually"


class KbFileRagTask(BaseModel):

    id: int
    field_id: str
    kb_id: str
    #  0: 未开始 1: 进行中 2: 已完成 3: 失败 4: 待取消 5: 已经取消
    task_status: str
    version: int
    process_start_time: datetime
    process_end_time: datetime
    process_result: str
    create_time: datetime
    update_time: datetime
