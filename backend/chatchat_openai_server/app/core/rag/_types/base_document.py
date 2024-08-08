from typing import Optional, Union

from pydantic import BaseModel, Field


class BaseDocument(BaseModel):
    id: Union[str, int] = Field(default=None)
    page_content: Optional[str] = Field(default=None)
    metadata: Optional[dict] = Field(default_factory=dict)
