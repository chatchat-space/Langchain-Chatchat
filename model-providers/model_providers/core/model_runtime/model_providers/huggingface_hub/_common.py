from typing import Dict, Type, List

from huggingface_hub.utils import BadRequestError, HfHubHTTPError

from model_providers.core.model_runtime.errors.invoke import (
    InvokeBadRequestError,
    InvokeError,
)


class _CommonHuggingfaceHub:
    @property
    def _invoke_error_mapping(self) -> Dict[Type[InvokeError], List[Type[Exception]]]:
        return {InvokeBadRequestError: [HfHubHTTPError, BadRequestError]}
