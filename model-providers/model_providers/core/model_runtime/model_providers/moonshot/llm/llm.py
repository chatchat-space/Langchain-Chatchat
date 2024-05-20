from typing import Generator, List, Optional, Union

from model_providers.core.model_runtime.entities.llm_entities import LLMResult
from model_providers.core.model_runtime.entities.message_entities import (
    PromptMessage,
    PromptMessageTool,
)
from model_providers.core.model_runtime.model_providers.openai_api_compatible.llm.llm import (
    OAIAPICompatLargeLanguageModel,
)


class MoonshotLargeLanguageModel(OAIAPICompatLargeLanguageModel):
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: List[PromptMessage],
        model_parameters: dict,
        tools: Optional[List[PromptMessageTool]] = None,
        stop: Optional[List[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        self._add_custom_parameters(credentials)
        user = user[:32] if user else None
        return super()._invoke(
            model,
            credentials,
            prompt_messages,
            model_parameters,
            tools,
            stop,
            stream,
            user,
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)

    @staticmethod
    def _add_custom_parameters(credentials: dict) -> None:
        credentials["mode"] = "chat"
        credentials["endpoint_url"] = "https://api.moonshot.cn/v1"
