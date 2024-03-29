import asyncio
import json
import logging
import multiprocessing as mp
import os
import pprint
import threading
from typing import Any, Dict, Optional

import tiktoken
from fastapi import APIRouter, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from uvicorn import Config, Server

from model_providers.core.bootstrap import OpenAIBootstrapBaseWeb
from model_providers.core.bootstrap.openai_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    EmbeddingsRequest,
    EmbeddingsResponse,
    FunctionAvailable,
    ModelList,
)
from model_providers.core.model_runtime.entities.message_entities import (
    UserPromptMessage,
)
from model_providers.core.model_runtime.entities.model_entities import ModelType
from model_providers.core.model_runtime.model_providers import model_provider_factory
from model_providers.core.model_runtime.model_providers.__base.ai_model import AIModel
from model_providers.core.model_runtime.model_providers.__base.large_language_model import (
    LargeLanguageModel,
)
from model_providers.core.utils.generic import dictify, jsonify

logger = logging.getLogger(__name__)


async def create_stream_chat_completion(
    model_type_instance: LargeLanguageModel, chat_request: ChatCompletionRequest
):
    try:
        response = model_type_instance.invoke(
            model=chat_request.model,
            credentials={
                "openai_api_key": "sk-",
                "minimax_api_key": os.environ.get("MINIMAX_API_KEY"),
                "minimax_group_id": os.environ.get("MINIMAX_GROUP_ID"),
            },
            prompt_messages=[UserPromptMessage(content="北京今天的天气怎么样")],
            model_parameters={**chat_request.to_model_parameters_dict()},
            stop=chat_request.stop,
            stream=chat_request.stream,
            user="abc-123",
        )
        return response

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


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
            "/v1/models",
            self.list_models,
            response_model=ModelList,
            methods=["GET"],
        )

        self._router.add_api_route(
            "/v1/embeddings",
            self.create_embeddings,
            response_model=EmbeddingsResponse,
            status_code=status.HTTP_200_OK,
            methods=["POST"],
        )
        self._router.add_api_route(
            "/v1/chat/completions",
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

    async def list_models(self, request: Request):
        pass

    async def create_embeddings(
        self, request: Request, embeddings_request: EmbeddingsRequest
    ):
        logger.info(
            f"Received create_embeddings request: {pprint.pformat(embeddings_request.dict())}"
        )
        if os.environ["API_KEY"] is None:
            authorization = request.headers.get("Authorization")
            authorization = authorization.split("Bearer ")[-1]
        else:
            authorization = os.environ["API_KEY"]
        client = ZhipuAI(api_key=authorization)
        # 判断embeddings_request.input是否为list
        input = None
        if isinstance(embeddings_request.input, list):
            tokens = embeddings_request.input
            try:
                encoding = tiktoken.encoding_for_model(embeddings_request.model)
            except KeyError:
                logger.warning("Warning: model not found. Using cl100k_base encoding.")
                model = "cl100k_base"
                encoding = tiktoken.get_encoding(model)
            for i, token in enumerate(tokens):
                text = encoding.decode(token)
                input += text

        else:
            input = embeddings_request.input

        response = client.embeddings.create(
            model=embeddings_request.model,
            input=input,
        )
        return EmbeddingsResponse(**dictify(response))

    async def create_chat_completion(
        self, request: Request, chat_request: ChatCompletionRequest
    ):
        logger.info(
            f"Received chat completion request: {pprint.pformat(chat_request.dict())}"
        )
        if os.environ["API_KEY"] is None:
            authorization = request.headers.get("Authorization")
            authorization = authorization.split("Bearer ")[-1]
        else:
            authorization = os.environ["API_KEY"]
        model_provider_factory.get_providers(provider_name="openai")
        provider_instance = model_provider_factory.get_provider_instance("openai")
        model_type_instance = provider_instance.get_model_instance(ModelType.LLM)
        if chat_request.stream:
            generator = create_stream_chat_completion(model_type_instance, chat_request)
            return EventSourceResponse(generator, media_type="text/event-stream")
        else:
            response = model_type_instance.invoke(
                model="gpt-4",
                credentials={
                    "openai_api_key": "sk-",
                    "minimax_api_key": os.environ.get("MINIMAX_API_KEY"),
                    "minimax_group_id": os.environ.get("MINIMAX_GROUP_ID"),
                },
                prompt_messages=[UserPromptMessage(content="北京今天的天气怎么样")],
                model_parameters={
                    "temperature": 0.7,
                    "top_p": 1.0,
                    "top_k": 1,
                    "plugin_web_search": True,
                },
                stop=["you"],
                stream=False,
                user="abc-123",
            )

            chat_response = ChatCompletionResponse(**dictify(response))

            return chat_response


def run(
    cfg: Dict,
    logging_conf: Optional[dict] = None,
    started_event: mp.Event = None,
):
    logging.config.dictConfig(logging_conf)  # type: ignore
    try:
        import signal

        # 跳过键盘中断，使用xoscar的信号处理
        signal.signal(signal.SIGINT, lambda *_: None)
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
