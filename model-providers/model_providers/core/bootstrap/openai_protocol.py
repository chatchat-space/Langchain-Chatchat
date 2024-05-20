import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field as FieldInfo
from typing_extensions import Literal

from ..._models import BaseModel


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"

    @classmethod
    def value_of(cls, origin_role: str) -> "Role":
        if origin_role == "user":
            return cls.USER
        elif origin_role == "assistant":
            return cls.ASSISTANT
        elif origin_role == "system":
            return cls.SYSTEM
        elif origin_role == "function":
            return cls.FUNCTION
        elif origin_role == "tool":
            return cls.TOOL
        else:
            raise ValueError(f"invalid origin role {origin_role}")

    def to_origin_role(self) -> str:
        if self == self.USER:
            return "user"
        elif self == self.ASSISTANT:
            return "assistant"
        elif self == self.SYSTEM:
            return "system"
        elif self == self.FUNCTION:
            return "function"
        elif self == self.TOOL:
            return "tool"
        else:
            raise ValueError(f"invalid role {self}")


class Finish(str, Enum):
    STOP = "stop"
    LENGTH = "length"
    TOOL = "tool_calls"

    @classmethod
    def value_of(cls, origin_finish: str) -> "Finish":
        if origin_finish == "stop":
            return cls.STOP
        elif origin_finish == "length":
            return cls.LENGTH
        elif origin_finish == "tool_calls":
            return cls.TOOL
        else:
            raise ValueError(f"invalid origin finish {origin_finish}")

    def to_origin_finish(self) -> str:
        if self == self.STOP:
            return "stop"
        elif self == self.LENGTH:
            return "length"
        elif self == self.TOOL:
            return "tool_calls"
        else:
            raise ValueError(f"invalid finish {self}")


class ModelCard(BaseModel):
    id: str
    object: Literal[
        "text-generation",
        "embeddings",
        "reranking",
        "speech2text",
        "moderation",
        "tts",
        "text2img",
    ] = "llm"
    created: int = FieldInfo(default_factory=lambda: int(time.time()))
    owned_by: Literal["owner"] = "owner"


class ModelList(BaseModel):
    object: Literal["list"] = "list"
    data: List[ModelCard] = []


class Function(BaseModel):
    name: str
    arguments: str


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class FunctionCallDefinition(BaseModel):
    name: str


class FunctionCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: Function


class FunctionAvailable(BaseModel):
    type: Literal["function", "code_interpreter"] = "function"
    function: Optional[FunctionDefinition] = None


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatCompletionMessage(BaseModel):
    role: Optional[Role] = None
    content: Optional[str] = None
    tool_calls: Optional[List[FunctionCall]] = None
    function_call: Optional[Function] = None


class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: Optional[int] = None
    total_tokens: int


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    tools: Optional[List[FunctionAvailable]] = None
    functions: Optional[List[FunctionDefinition]] = None
    function_call: Optional[FunctionCallDefinition] = None
    temperature: Optional[float] = 0.75
    top_p: Optional[float] = 0.75
    top_k: Optional[float] = None
    n: int = 1
    max_tokens: Optional[int] = 256
    stop: Optional[List[str]] = None
    stream: Optional[bool] = False

    def to_model_parameters_dict(self, *args, **kwargs):
        # 调用父类的to_dict方法，并排除tools字段

        return super().dict(
            exclude={"tools", "messages", "functions", "function_call"}, *args, **kwargs
        )


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Finish


class ChatCompletionStreamResponseChoice(BaseModel):
    index: int
    delta: ChatCompletionMessage
    finish_reason: Optional[Finish] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int = FieldInfo(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo


class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int = FieldInfo(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionStreamResponseChoice]


class EmbeddingsRequest(BaseModel):
    input: Union[str, List[List[int]], List[int], List[str]]
    model: str
    encoding_format: Literal["base64", "float"] = "float"


class Embeddings(BaseModel):
    object: Literal["embedding"] = "embedding"
    embedding: Union[List[float], bytes]
    index: int


class EmbeddingsResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[Embeddings]
    model: str
    usage: UsageInfo
