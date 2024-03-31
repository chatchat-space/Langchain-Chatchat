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
    ModelCard,
    ModelList,
)
from model_providers.core.model_manager import ModelInstance, ModelManager
from model_providers.core.model_runtime.entities.message_entities import (
    UserPromptMessage,
)
from model_providers.core.model_runtime.entities.model_entities import (
    AIModelEntity,
    ModelType,
)
from model_providers.core.utils.generic import dictify, jsonify

logger = logging.getLogger(__name__)


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
        if chat_request.stream:
            # Invoke model

            response = model_instance.invoke_llm(
                prompt_messages=[UserPromptMessage(content="北京今天的天气怎么样")],
                model_parameters={**chat_request.to_model_parameters_dict()},
                stop=chat_request.stop,
                stream=chat_request.stream,
                user="abc-123",
            )

            return EventSourceResponse(response, media_type="text/event-stream")
        else:
            # Invoke model

            response = model_instance.invoke_llm(
                prompt_messages=[UserPromptMessage(content="北京今天的天气怎么样")],
                model_parameters={**chat_request.to_model_parameters_dict()},
                stop=chat_request.stop,
                stream=chat_request.stream,
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
