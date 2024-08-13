from pydantic import BaseModel, Field


class CeleryConfig(BaseModel):
    main_queue: str = Field(default="celery_main")
    broker_url: str
    backend_url: str
