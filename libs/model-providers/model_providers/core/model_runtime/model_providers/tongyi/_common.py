from typing import Dict, List, Type

from model_providers.core.model_runtime.errors.invoke import InvokeError


class _CommonTongyi:
    @staticmethod
    def _to_credential_kwargs(credentials: dict) -> dict:
        credentials_kwargs = {
            "dashscope_api_key": credentials["dashscope_api_key"],
        }

        return credentials_kwargs

    @property
    def _invoke_error_mapping(self) -> Dict[Type[InvokeError], List[Type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the error type thrown to the caller
        The value is the error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke error mapping
        """
        pass
