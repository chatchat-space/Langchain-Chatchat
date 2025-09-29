# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional

from openai import BaseModel


class PlatformToolsMessageToolCall(BaseModel):
    name: Optional[str]
    args: Optional[Dict[str, Any]]
    id: Optional[str]


class PlatformToolsMessageToolCallChunk(BaseModel):
    name: Optional[str]
    args: Optional[Dict[str, Any]]
    id: Optional[str]
    index: Optional[int]
