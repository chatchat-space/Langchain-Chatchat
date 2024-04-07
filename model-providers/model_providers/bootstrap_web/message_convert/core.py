import logging
import typing
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

from model_providers.core.bootstrap.openai_protocol import (
    ChatCompletionMessage,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionStreamResponse,
    ChatCompletionStreamResponseChoice,
    ChatMessage,
    Embeddings,
    EmbeddingsResponse,
    Finish,
    Role,
    UsageInfo,
)
from model_providers.core.model_runtime.entities.llm_entities import (
    LLMResult,
    LLMResultChunk,
)
from model_providers.core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    ImagePromptMessageContent,
    PromptMessage,
    SystemPromptMessage,
    TextPromptMessageContent,
    ToolPromptMessage,
    UserPromptMessage,
)
from model_providers.core.model_runtime.entities.text_embedding_entities import (
    TextEmbeddingResult,
)
from model_providers.core.utils.generic import jsonify

if typing.TYPE_CHECKING:
    from model_providers.core.bootstrap.openai_protocol import ChatCompletionMessage

logger = logging.getLogger(__name__)

MessageLike = Union[ChatMessage, PromptMessage]

MessageLikeRepresentation = Union[
    MessageLike,
    Tuple[Union[str, Type], Union[str, List[dict], List[object]]],
    str,
]


def create_stream_chunk(
    request_id: str,
    model: str,
    delta: "ChatCompletionMessage",
    index: Optional[int] = 0,
    finish_reason: Optional[Finish] = None,
) -> str:
    choice = ChatCompletionStreamResponseChoice(
        index=index, delta=delta, finish_reason=finish_reason
    )
    chunk = ChatCompletionStreamResponse(id=request_id, model=model, choices=[choice])
    return jsonify(chunk)


def _convert_prompt_message_to_dict(message: PromptMessage) -> dict:
    """
    Convert PromptMessage to dict for OpenAI Compatibility API
    """
    if isinstance(message, UserPromptMessage):
        message = cast(UserPromptMessage, message)
        if isinstance(message.content, str):
            message_dict = {"role": "user", "content": message.content}
        else:
            raise ValueError("User message content must be str")
    elif isinstance(message, AssistantPromptMessage):
        message = cast(AssistantPromptMessage, message)
        message_dict = {"role": "assistant", "content": message.content}
        if message.tool_calls and len(message.tool_calls) > 0:
            message_dict["function_call"] = {
                "name": message.tool_calls[0].function.name,
                "arguments": message.tool_calls[0].function.arguments,
            }
    elif isinstance(message, SystemPromptMessage):
        message = cast(SystemPromptMessage, message)
        message_dict = {"role": "system", "content": message.content}
    elif isinstance(message, ToolPromptMessage):
        # check if last message is user message
        message = cast(ToolPromptMessage, message)
        message_dict = {"role": "function", "content": message.content}
    else:
        raise ValueError(f"Unknown message type {type(message)}")

    return message_dict


def _create_template_from_message_type(
    message_type: str, template: Union[str, list]
) -> PromptMessage:
    """Create a message prompt template from a message type and template string.

    Args:
        message_type: str the type of the message template (e.g., "human", "ai", etc.)
        template: str the template string.

    Returns:
        a message prompt template of the appropriate type.
    """
    if isinstance(template, str):
        content = template
    elif isinstance(template, list):
        content = []
        for tmpl in template:
            if isinstance(tmpl, str) or isinstance(tmpl, dict) and "text" in tmpl:
                if isinstance(tmpl, str):
                    text: str = tmpl
                else:
                    text = cast(dict, tmpl)["text"]  # type: ignore[assignment]  # noqa: E501
                content.append(TextPromptMessageContent(data=text))
            elif isinstance(tmpl, dict) and "image_url" in tmpl:
                img_template = cast(dict, tmpl)["image_url"]
                if isinstance(img_template, str):
                    img_template_obj = ImagePromptMessageContent(data=img_template)
                elif isinstance(img_template, dict):
                    img_template = dict(img_template)
                    if "url" in img_template:
                        url = img_template["url"]
                    else:
                        url = None
                    img_template_obj = ImagePromptMessageContent(data=url)
                else:
                    raise ValueError()
                content.append(img_template_obj)
            else:
                raise ValueError()
    else:
        raise ValueError()

    if message_type in ("human", "user"):
        _message = UserPromptMessage(content=content)
    elif message_type in ("ai", "assistant"):
        _message = AssistantPromptMessage(content=content)
    elif message_type == "system":
        _message = SystemPromptMessage(content=content)
    elif message_type in ("function", "tool"):
        _message = ToolPromptMessage(content=content)
    else:
        raise ValueError(
            f"Unexpected message type: {message_type}. Use one of 'human',"
            f" 'user', 'ai', 'assistant', or 'system' and 'function' or 'tool'."
        )

    return _message


def _convert_to_message(
    message: MessageLikeRepresentation,
) -> Union[PromptMessage]:
    """Instantiate a message from a variety of message formats.

    The message format can be one of the following:

    - BaseMessagePromptTemplate
    - BaseMessage
    - 2-tuple of (role string, template); e.g., ("human", "{user_input}")
    - 2-tuple of (message class, template)
    - string: shorthand for ("human", template); e.g., "{user_input}"

    Args:
        message: a representation of a message in one of the supported formats

    Returns:
        an instance of a message or a message template
    """
    if isinstance(message, ChatMessage):
        _message = _create_template_from_message_type(
            message.role.to_origin_role(), message.content
        )

    elif isinstance(message, PromptMessage):
        _message = message
    elif isinstance(message, str):
        _message = _create_template_from_message_type("human", message)
    elif isinstance(message, tuple):
        if len(message) != 2:
            raise ValueError(f"Expected 2-tuple of (role, template), got {message}")
        message_type_str, template = message
        if isinstance(message_type_str, str):
            _message = _create_template_from_message_type(message_type_str, template)
        else:
            raise ValueError(f"Expected message type string, got {message_type_str}")
    else:
        raise NotImplementedError(f"Unsupported message type: {type(message)}")

    return _message


async def _stream_openai_chat_completion(
    response: Generator,
) -> AsyncGenerator[str, None]:
    request_id, model = None, None
    for chunk in response:
        if not isinstance(chunk, LLMResultChunk):
            yield "[ERROR]"
            return

        if model is None:
            model = chunk.model
        if request_id is None:
            request_id = "request_id"
            yield create_stream_chunk(
                request_id,
                model,
                ChatCompletionMessage(role=Role.ASSISTANT, content=""),
            )

        new_token = chunk.delta.message.content

        if new_token:
            delta = ChatCompletionMessage(
                role=Role.value_of(chunk.delta.message.role.to_origin_role()),
                content=new_token,
                tool_calls=chunk.delta.message.tool_calls,
            )
            yield create_stream_chunk(
                request_id=request_id,
                model=model,
                delta=delta,
                index=chunk.delta.index,
                finish_reason=chunk.delta.finish_reason,
            )

    yield create_stream_chunk(
        request_id, model, ChatCompletionMessage(), finish_reason=Finish.STOP
    )
    yield "[DONE]"


async def _openai_chat_completion(response: LLMResult) -> ChatCompletionResponse:
    choice = ChatCompletionResponseChoice(
        index=0,
        message=ChatCompletionMessage(
            **_convert_prompt_message_to_dict(message=response.message)
        ),
        finish_reason=Finish.STOP,
    )
    usage = UsageInfo(
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens,
    )
    return ChatCompletionResponse(
        id="request_id",
        model=response.model,
        choices=[choice],
        usage=usage,
    )


async def _openai_embedding_text(response: TextEmbeddingResult) -> EmbeddingsResponse:
    embedding = [
        Embeddings(embedding=embedding, index=index)
        for index, embedding in enumerate(response.embeddings)
    ]

    return EmbeddingsResponse(
        model=response.model,
        data=embedding,
        usage=UsageInfo(
            prompt_tokens=response.usage.tokens,
            total_tokens=response.usage.total_tokens,
            completion_tokens=response.usage.total_tokens,
        ),
    )


convert_to_message = _convert_to_message
stream_openai_chat_completion = _stream_openai_chat_completion
openai_chat_completion = _openai_chat_completion
openai_embedding_text = _openai_embedding_text
