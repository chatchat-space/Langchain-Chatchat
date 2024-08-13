from celery import Celery

from app.configs.celery_config import CeleryConfig


celery_app: Celery = None


def init_celery(config: CeleryConfig):
    global celery_app
    celery_app = Celery(config.main_queue,
                        broker=config.broker_url,
                        backend=config.backend_url)
    from app.tasks.file_to_vs_store_task import file_to_vs_store_task
    return celery_app
