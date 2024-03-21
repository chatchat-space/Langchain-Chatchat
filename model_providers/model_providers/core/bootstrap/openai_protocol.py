import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, root_validator
from typing_extensions import Literal


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


class Finish(str, Enum):
    STOP = "stop"
    LENGTH = "length"
    TOOL = "tool_calls"


class ModelCard(BaseModel):
    id: str
    object: Literal["model"] = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
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
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[float] = None
    n: int = 1
    max_tokens: Optional[int] = None
    stop: Optional[list[str]] = None,
    stream: Optional[bool] = False

    def to_model_parameters_dict(self, *args, **kwargs):
        # 调用父类的to_dict方法，并排除tools字段
        helper.dump_model
        return super().dict(exclude={'tools','messages','functions','function_call'}, *args, **kwargs)


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
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo


class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
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
