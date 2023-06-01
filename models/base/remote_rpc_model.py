from abc import ABC, abstractmethod
import torch

from models.base import (BaseAnswer,
                         AnswerResult)


class MultimodalAnswerResult(AnswerResult):
    image: str = None


class RemoteRpcModel(BaseAnswer, ABC):

    @property
    @abstractmethod
    def _api_key(self) -> str:
        """Return _api_key of client."""

    @property
    @abstractmethod
    def _api_base_url(self) -> str:
        """Return _api_base of client host bash url."""

    @abstractmethod
    def set_api_key(self, api_key: str):
        """set set_api_key"""

    @abstractmethod
    def set_api_base_url(self, api_base_url: str):
        """set api_base_url"""
    @abstractmethod
    def call_model_name(self, model_name):
        """call model name of client"""
