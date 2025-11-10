# -*- coding: utf-8 -*-
import json
import uuid
from abc import abstractmethod
from enum import Enum, auto
from numbers import Number
from typing import Any, Dict, List, Optional, Union

from openai import BaseModel
from typing_extensions import ClassVar, Self
from langchain_chatchat.utils.__init__ import PYDANTIC_V2
from pydantic import ConfigDict


class MsgType:
    TEXT = 1
    IMAGE = 2
    AUDIO = 3
    VIDEO = 4


class PlatformToolsBaseComponent(BaseModel):
    if PYDANTIC_V2:
        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)
    else:

        class Config:
            arbitrary_types_allowed = True

    @classmethod
    @abstractmethod
    def class_name(cls) -> str:
        """Get class name."""

    def to_dict(self, **kwargs: Any) -> Dict[str, Any]:
        data = self.dict(**kwargs)
        data["class_name"] = self.class_name()
        return data

    def to_json(self, **kwargs: Any) -> str:
        data = self.to_dict(**kwargs)
        return json.dumps(data, ensure_ascii=False)

    # TODO: return type here not supported by current mypy version
    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs: Any) -> Self:  # type: ignore
        if isinstance(kwargs, dict):
            data.update(kwargs)

        data.pop("class_name", None)
        return cls(**data)

    @classmethod
    def from_json(cls, data_str: str, **kwargs: Any) -> Self:  # type: ignore
        data = json.loads(data_str)
        return cls.from_dict(data, **kwargs)


class PlatformToolsApprove(PlatformToolsBaseComponent):
    """Approve or reject a tool input."""

    run_id: str
    status: int  # AgentStatus
    tool: str
    tool_input: Union[str, Dict[str, Any]]
    log: str

    @classmethod
    def class_name(cls) -> str:
        return "PlatformToolsApprove"


class PlatformToolsAction(PlatformToolsBaseComponent):
    """AgentFinish with run and thread metadata."""

    run_id: str
    status: int  # AgentStatus
    tool: str
    tool_input: Union[str, Dict[str, Any]]
    log: str

    @classmethod
    def class_name(cls) -> str:
        return "PlatformToolsAction"


class PlatformToolsFinish(PlatformToolsBaseComponent):
    """AgentFinish with run and thread metadata."""

    run_id: str
    status: int  # AgentStatus
    return_values: Dict[str, str]
    log: str

    @classmethod
    def class_name(cls) -> str:
        return "PlatformToolsFinish"


class PlatformToolsActionToolStart(PlatformToolsBaseComponent):
    """PlatformToolsAction with run and thread metadata."""

    run_id: str
    status: int  # AgentStatus
    tool: str
    tool_input: Optional[str] = None

    @classmethod
    def class_name(cls) -> str:
        return "PlatformToolsActionToolStart"


class PlatformToolsActionToolEnd(PlatformToolsBaseComponent):
    """PlatformToolsActionToolEnd with run and thread metadata."""

    run_id: str

    status: int  # AgentStatus
    tool: str
    tool_output: str

    @classmethod
    def class_name(cls) -> str:
        return "PlatformToolsActionToolEnd"


class PlatformToolsLLMStatus(PlatformToolsBaseComponent):
    run_id: str
    status: int  # AgentStatus
    text: str
    message_type: int = MsgType.TEXT

    @classmethod
    def class_name(cls) -> str:
        return "PlatformToolsLLMStatus"
