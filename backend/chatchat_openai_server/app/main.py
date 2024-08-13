from fastapi import FastAPI
from app.configs.app_config import app_config
from app.depends.depend_cache import init_cache
from app.depends.depend_celery import init_celery
from app.depends.depend_database import init_database
from app.depends.depend_mq import init_mq
from app.depends.depend_storage import init_storage


def init_router(_app, config):
    from app.router import v1_router
    _app.include_router(v1_router)


def init_app():
    _app = FastAPI()
    init_database(app_config.database)
    init_mq(app_config.mq)
    init_storage(app_config.storage)
    init_cache(app_config.cache)
    _task_app = init_celery(app_config.celery)
    init_router(_app, app_config)
    return _app, _task_app


app, task_app = init_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
