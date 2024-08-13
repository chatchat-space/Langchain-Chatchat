import yaml
from pydantic import BaseModel

from app.configs.celery_config import CeleryConfig


class AppConfig(BaseModel):
    storage: dict = None
    database: dict = None
    cache: dict = None
    mq: dict = None
    celery: CeleryConfig


with open("conf/app.yml", "r") as file:
    yaml_config = yaml.safe_load(file)
    if yaml_config is None:
        yaml_config = {}

app_config: AppConfig = AppConfig(**yaml_config)
