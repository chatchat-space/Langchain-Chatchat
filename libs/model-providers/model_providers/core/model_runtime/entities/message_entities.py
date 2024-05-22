from abc import ABC
from enum import Enum
from typing import List, Optional, Union

from ...._models import BaseModel


class PromptMessageRole(Enum):
    """
    Enum class for prompt message.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

    @classmethod
    def value_of(cls, value: str) -> "PromptMessageRole":
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"invalid prompt message type value {value}")

    def to_origin_role(self) -> str:
        """
        Get origin role from prompt message role.

        :return: origin role
        """
        if self == self.SYSTEM:
            return "system"
        elif self == self.USER:
            return "user"
        elif self == self.ASSISTANT:
            return "assistant"
        elif self == self.TOOL:
            return "tool"
        else:
            raise ValueError(f"invalid role {self}")


class PromptMessageTool(BaseModel):
    """
    Model class for prompt message tool.
    """

    name: str
    description: str
    parameters: dict


class PromptMessageFunction(BaseModel):
    """
    Model class for prompt message function.
    """

    type: str = "function"
    function: PromptMessageTool


class PromptMessageContentType(Enum):
    """
    Enum class for prompt message content type.
    """

    TEXT = "text"
    IMAGE = "image"


class PromptMessageContent(BaseModel):
    """
    Model class for prompt message content.
    """

    type: PromptMessageContentType
    data: str


class TextPromptMessageContent(PromptMessageContent):
    """
    Model class for text prompt message content.
    """

    type: PromptMessageContentType = PromptMessageContentType.TEXT


class ImagePromptMessageContent(PromptMessageContent):
    """
    Model class for image prompt message content.
    """

    class DETAIL(Enum):
        LOW = "low"
        HIGH = "high"

    type: PromptMessageContentType = PromptMessageContentType.IMAGE
    detail: DETAIL = DETAIL.LOW


class PromptMessage(ABC, BaseModel):
    """
    Model class for prompt message.
    """

    role: PromptMessageRole
    content: Optional[Union[str, List[PromptMessageContent]]] = None
    name: Optional[str] = None


class UserPromptMessage(PromptMessage):
    """
    Model class for user prompt message.
    """

    role: PromptMessageRole = PromptMessageRole.USER


class AssistantPromptMessage(PromptMessage):
    """
    Model class for assistant prompt message.
    """

    class ToolCall(BaseModel):
        """
        Model class for assistant prompt message tool call.
        """

        class ToolCallFunction(BaseModel):
            """
            Model class for assistant prompt message tool call function.
            """

            name: str
            arguments: str

        id: str
        type: str
        function: ToolCallFunction

    role: PromptMessageRole = PromptMessageRole.ASSISTANT
    tool_calls: List[ToolCall] = []


class SystemPromptMessage(PromptMessage):
    """
    Model class for system prompt message.
    """

    role: PromptMessageRole = PromptMessageRole.SYSTEM


class ToolPromptMessage(PromptMessage):
    """
    Model class for tool prompt message.
    """

    role: PromptMessageRole = PromptMessageRole.TOOL
    tool_call_id: str
