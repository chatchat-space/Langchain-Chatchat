from abc import abstractmethod
from collections import deque

from fastapi import Request


class Bootstrap:

    """最大的任务队列"""

    _MAX_ONGOING_TASKS: int = 1

    """任务队列"""
    _QUEUE: deque = deque()

    def __init__(self):
        self._version = "v0.0.1"

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
    async def list_models(self, request: Request):
        pass

    @abstractmethod
    async def create_embeddings(
        self, request: Request, embeddings_request: EmbeddingsRequest
    ):
        pass

    @abstractmethod
    async def create_chat_completion(
        self, request: Request, chat_request: ChatCompletionRequest
    ):
        pass
