from abc import ABC, abstractmethod
import torch

from models.base import (BaseAnswer,
                         AnswerResult)


class MultimodalAnswerResult(AnswerResult):
    image: str = None


class LavisBlip2Multimodal(BaseAnswer, ABC):

    @property
    @abstractmethod
    def _blip2_instruct(self) -> any:
        """Return _blip2_instruct of blip2."""

    @property
    @abstractmethod
    def _image_blip2_vis_processors(self) -> dict:
        """Return _image_blip2_vis_processors of blip2 image processors."""

    @abstractmethod
    def set_image_path(self, image_path: str):
        """set set_image_path"""
