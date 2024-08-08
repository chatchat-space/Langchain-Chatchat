from fastapi import FastAPI
from app.configs.app_config import app_config
from app.extensions.ext_cache import init_cache
from app.extensions.ext_database import init_database
from app.extensions.ext_mq import init_mq

from app.extensions.ext_storage import init_storage


def init_router(_app, config):
    from app.router import v1_router
    _app.include_router(v1_router)


def init_app():
    _app = FastAPI()
    init_database(app_config.database)
    init_storage(app_config.storage)
    init_cache(app_config.cache)
    init_mq(app_config.mq)
    init_router(_app, app_config)
    return _app


if __name__ == "__main__":
    import uvicorn

    app = init_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
