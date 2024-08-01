from functools import lru_cache

from apscheduler.schedulers.background import BackgroundScheduler

from chatchat.server._types.task.kb_file_rag_task import KbFileRagTask
from chatchat.server.core.lock.default_distributed_lock import DefaultDistributedLock
from chatchat.server.core.task.default_scheduler import get_scheduler
from chatchat.server.db.repository.kb_file_rag_task_repository import get_not_started_tasks, get_task_by_id
from chatchat.server.knowledge_base.migrate import create_tables

scheduler = None
RAG_TASK_LOCK_PREFIX = "RAG_TASK_LOCK_"


def scan_kb_file_rag_task():
    page = 1
    page_size = 50
    print("scan_kb_file_rag_task")
    while True:
        not_started_tasks = get_not_started_tasks(page, page_size)
        for not_started_task in not_started_tasks:
            print(not_started_task)


def not_started_rag_task_handler(not_started_task: KbFileRagTask):
    lock = DefaultDistributedLock(f'{RAG_TASK_LOCK_PREFIX}{not_started_task.kb_id}_{not_started_task.field_id}')
    try:
        if lock.lock():
            _not_started_task = get_task_by_id(not_started_task.id)
    finally:
        lock.release()


def in_progress_rag_task_handler():
    ...


# def job_function():
#     print("Hello, world!")


def def_task_for_default_scheduler():
    create_tables()
    global scheduler
    if scheduler is not None:
        return
    scheduler = get_scheduler()
    scheduler.add_job(scan_kb_file_rag_task, 'interval', seconds=1)
    scheduler.start()
