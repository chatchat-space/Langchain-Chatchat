"""
前端消息传输结构
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class BaseMessageDto(BaseModel):
    """Message Dto."""

    content: str


class OpenAiMessageDto(BaseModel):
    """
    see @Link{langchain.schema._message_from_dict}
    """
    type: Optional[str] = Field(
        default="user"
    )
    data: BaseMessageDto


class OpenAiChatMsgDto(BaseModel):
    model_name: str
    messages: List[OpenAiMessageDto]
    temperature: Optional[float] = Field(
        default=0.7
    )
    max_tokens: Optional[int] = Field(
        default=512
    )
    stop: List[str] = Field(
        default=[]
    )
    stream: Optional[bool] = Field(
        default=False
    )
    presence_penalty: Optional[int] = Field(
        default=0
    )
    frequency_penalty: Optional[int] = Field(
        default=0
    )
