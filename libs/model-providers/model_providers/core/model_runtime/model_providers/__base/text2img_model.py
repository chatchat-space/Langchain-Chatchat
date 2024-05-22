from abc import abstractmethod
from typing import IO, List, Optional

from model_providers.core.model_runtime.entities.model_entities import ModelType
from model_providers.core.model_runtime.model_providers.__base.ai_model import AIModel


class Text2ImageModel(AIModel):
    """
    Model class for text2img model.
    """

    model_type: ModelType = ModelType.TEXT2IMG

    def invoke(
        self,
        model: str,
        credentials: dict,
        prompt: str,
        model_parameters: dict,
        user: Optional[str] = None,
    ) -> List[IO[bytes]]:
        """
        Invoke Text2Image model

        :param model: model name
        :param credentials: model credentials
        :param prompt: prompt for image generation
        :param model_parameters: model parameters
        :param user: unique user id

        :return: image bytes
        """
        try:
            return self._invoke(model, credentials, prompt, model_parameters, user)
        except Exception as e:
            raise self._transform_invoke_error(e)

    @abstractmethod
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt: str,
        model_parameters: dict,
        user: Optional[str] = None,
    ) -> List[IO[bytes]]:
        """
        Invoke Text2Image model

        :param model: model name
        :param credentials: model credentials
        :param prompt: prompt for image generation
        :param model_parameters: model parameters
        :param user: unique user id

        :return: image bytes
        """
        raise NotImplementedError
