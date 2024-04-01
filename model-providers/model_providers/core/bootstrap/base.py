from abc import abstractmethod
from collections import deque
from typing import List, Optional

from fastapi import Request

from model_providers.core.bootstrap.openai_protocol import (
    ChatCompletionRequest,
    EmbeddingsRequest,
)
from model_providers.core.model_manager import ModelManager


class Bootstrap:
    """最大的任务队列"""

    _MAX_ONGOING_TASKS: int = 1

    """任务队列"""
    _QUEUE: deque = deque()

    _provider_manager: ModelManager

    def __init__(self):
        self._version = "v0.0.1"

    @property
    def provider_manager(self) -> ModelManager:
        return self._provider_manager

    @provider_manager.setter
    def provider_manager(self, provider_manager: ModelManager):
        self._provider_manager = provider_manager

    @classmethod
    @abstractmethod
    def from_config(cls, cfg=None):
        return cls()

    @property
    def version(self):
        return self._version

    @property
    def queue(self) -> deque:
        return self._QUEUE

    @classmethod
    async def run(cls):
        raise NotImplementedError

    @classmethod
    async def destroy(cls):
        raise NotImplementedError


class OpenAIBootstrapBaseWeb(Bootstrap):
    def __init__(self):
        super().__init__()

    @abstractmethod
    async def list_models(self, provider: str, request: Request):
        pass

    @abstractmethod
    async def create_embeddings(
        self, provider: str, request: Request, embeddings_request: EmbeddingsRequest
    ):
        pass

    @abstractmethod
    async def create_chat_completion(
        self, provider: str, request: Request, chat_request: ChatCompletionRequest
    ):
        pass
