from functools import lru_cache

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}


@lru_cache(maxsize=1)
def get_scheduler():
    return BackgroundScheduler(executors=executors, job_defaults=job_defaults)
