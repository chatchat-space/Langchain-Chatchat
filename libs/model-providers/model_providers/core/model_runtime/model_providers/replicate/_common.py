from typing import Dict, List, Type

from replicate.exceptions import ModelError, ReplicateError

from model_providers.core.model_runtime.errors.invoke import (
    InvokeBadRequestError,
    InvokeError,
)


class _CommonReplicate:
    @property
    def _invoke_error_mapping(self) -> Dict[Type[InvokeError], List[Type[Exception]]]:
        return {InvokeBadRequestError: [ReplicateError, ModelError]}
