import asyncio
import json
import logging
import multiprocessing as mp
import os
import pprint
import threading
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

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from uvicorn import Config, Server

from model_providers.bootstrap_web.common import create_stream_chunk
from model_providers.core.bootstrap import OpenAIBootstrapBaseWeb
from model_providers.core.bootstrap.openai_protocol import (
    ChatCompletionMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionStreamResponse,
    ChatMessage,
    EmbeddingsRequest,
    EmbeddingsResponse,
    Finish,
    FunctionAvailable,
    ModelCard,
    ModelList,
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
    PromptMessageContent,
    PromptMessageContentType,
    PromptMessageTool,
    SystemPromptMessage,
    TextPromptMessageContent,
    ToolPromptMessage,
    UserPromptMessage,
)
from model_providers.core.model_runtime.entities.model_entities import (
    AIModelEntity,
    ModelType,
)
from model_providers.core.model_runtime.errors.invoke import InvokeError
from model_providers.core.utils.generic import dictify, jsonify

logger = logging.getLogger(__name__)

MessageLike = Union[ChatMessage, PromptMessage]

MessageLikeRepresentation = Union[
    MessageLike,
    Tuple[Union[str, Type], Union[str, List[dict], List[object]]],
    str,
]


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


class RESTFulOpenAIBootstrapBaseWeb(OpenAIBootstrapBaseWeb):
    """
    Bootstrap Server Lifecycle
    """

    def __init__(self, host: str, port: int):
        super().__init__()
        self._host = host
        self._port = port
        self._router = APIRouter()
        self._app = FastAPI()
        self._server_thread = None

    @classmethod
    def from_config(cls, cfg=None):
        host = cfg.get("host", "127.0.0.1")
        port = cfg.get("port", 20000)

        logger.info(
            f"Starting openai Bootstrap Server Lifecycle at endpoint: http://{host}:{port}"
        )
        return cls(host=host, port=port)

    def serve(self, logging_conf: Optional[dict] = None):
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._router.add_api_route(
            "/{provider}/v1/models",
            self.list_models,
            response_model=ModelList,
            methods=["GET"],
        )

        self._router.add_api_route(
            "/{provider}/v1/embeddings",
            self.create_embeddings,
            response_model=EmbeddingsResponse,
            status_code=status.HTTP_200_OK,
            methods=["POST"],
        )
        self._router.add_api_route(
            "/{provider}/v1/chat/completions",
            self.create_chat_completion,
            response_model=ChatCompletionResponse,
            status_code=status.HTTP_200_OK,
            methods=["POST"],
        )

        self._app.include_router(self._router)

        config = Config(
            app=self._app, host=self._host, port=self._port, log_config=logging_conf
        )
        server = Server(config)

        def run_server():
            server.run()

        self._server_thread = threading.Thread(target=run_server)
        self._server_thread.start()

    async def join(self):
        await self._server_thread.join()

    def set_app_event(self, started_event: mp.Event = None):
        @self._app.on_event("startup")
        async def on_startup():
            if started_event is not None:
                started_event.set()

    async def list_models(self, provider: str, request: Request):
        logger.info(f"Received list_models request for provider: {provider}")
        # 返回ModelType所有的枚举
        llm_models: list[AIModelEntity] = []
        for model_type in ModelType.__members__.values():
            try:
                provider_model_bundle = (
                    self._provider_manager.provider_manager.get_provider_model_bundle(
                        provider=provider, model_type=model_type
                    )
                )
                llm_models.extend(
                    provider_model_bundle.model_type_instance.predefined_models()
                )
            except Exception as e:
                logger.error(
                    f"Error while fetching models for provider: {provider}, model_type: {model_type}"
                )
                logger.error(e)

        # models list[AIModelEntity]转换称List[ModelCard]

        models_list = [
            ModelCard(id=model.model, object=model.model_type.to_origin_model_type())
            for model in llm_models
        ]

        return ModelList(data=models_list)

    async def create_embeddings(
        self, provider: str, request: Request, embeddings_request: EmbeddingsRequest
    ):
        logger.info(
            f"Received create_embeddings request: {pprint.pformat(embeddings_request.dict())}"
        )

        response = None
        return EmbeddingsResponse(**dictify(response))

    async def create_chat_completion(
        self, provider: str, request: Request, chat_request: ChatCompletionRequest
    ):
        logger.info(
            f"Received chat completion request: {pprint.pformat(chat_request.dict())}"
        )

        model_instance = self._provider_manager.get_model_instance(
            provider=provider, model_type=ModelType.LLM, model=chat_request.model
        )
        prompt_messages = [
            _convert_to_message(message) for message in chat_request.messages
        ]

        tools = [
            PromptMessageTool(
                name=f.function.name,
                description=f.function.description,
                parameters=f.function.parameters,
            )
            for f in chat_request.tools
        ]
        if chat_request.functions:
            tools.extend(
                [
                    PromptMessageTool(
                        name=f.name, description=f.description, parameters=f.parameters
                    )
                    for f in chat_request.functions
                ]
            )

        try:
            response = model_instance.invoke_llm(
                prompt_messages=prompt_messages,
                model_parameters={**chat_request.to_model_parameters_dict()},
                tools=tools,
                stop=chat_request.stop,
                stream=chat_request.stream,
                user="abc-123",
            )

            if chat_request.stream:
                return EventSourceResponse(
                    _stream_openai_chat_completion(response),
                    media_type="text/event-stream",
                )
            else:
                return await _openai_chat_completion(response)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        except InvokeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )


def run(
    cfg: Dict,
    logging_conf: Optional[dict] = None,
    started_event: mp.Event = None,
):
    logging.config.dictConfig(logging_conf)  # type: ignore
    try:
        api = RESTFulOpenAIBootstrapBaseWeb.from_config(
            cfg=cfg.get("run_openai_api", {})
        )
        api.set_app_event(started_event=started_event)
        api.serve(logging_conf=logging_conf)

        async def pool_join_thread():
            await api.join()

        asyncio.run(pool_join_thread())
    except SystemExit:
        logger.info("SystemExit raised, exiting")
        raise
