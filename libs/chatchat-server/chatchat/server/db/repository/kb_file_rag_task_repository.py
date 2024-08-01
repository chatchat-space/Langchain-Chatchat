from datetime import datetime
from typing import List

from chatchat.server._types.task.kb_file_rag_task import TaskStatus
from chatchat.server.db.models.kb_file_rag_task_model import KbFileRagTaskModel
from chatchat.server.db.session import with_session


@with_session
def get_task_by_id(session, task_id) -> KbFileRagTaskModel:
    return session.query(KbFileRagTaskModel).filter_by(id=task_id).first()


@with_session
def create_task(session, field_id: str, task_status: str = TaskStatus.NOT_STARTED) -> KbFileRagTaskModel:
    new_task = KbFileRagTaskModel(
        field_id=field_id,
        task_status=task_status,
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow()
    )
    session.add(new_task)
    session.commit()
    return new_task


@with_session
def get_tasks(session, page: int = 1, page_size: int = 50, task_status=TaskStatus.NOT_STARTED) -> List[
    KbFileRagTaskModel]:
    return session.query(KbFileRagTaskModel) \
        .filter(KbFileRagTaskModel.task_status == task_status) \
        .order_by(KbFileRagTaskModel.create_time.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()


def get_not_started_tasks(session, page: int = 1, page_size: int = 50) -> List[KbFileRagTaskModel]:
    return get_tasks(session, page, page_size)
