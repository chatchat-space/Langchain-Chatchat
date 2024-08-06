from typing import List

import yaml
from pydantic import BaseModel


class MinioConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool


class AppConfig(BaseModel):
    minio: MinioConfig = None
    storage: dict = None
    database: dict = None


with open("conf/app.yml", "r") as file:
    yaml_config = yaml.safe_load(file)
    if yaml_config is None:
        yaml_config = {}

app_config: AppConfig = AppConfig(**yaml_config)
