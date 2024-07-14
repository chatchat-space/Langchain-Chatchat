from typing import Any, Union

from pydantic import AnyUrl

from chatchat.server.api_server.api_schemas import OpenAIImageVariationsInput


class OpenAIImageEditsInput(OpenAIImageVariationsInput):
    prompt: str
    mask: Union[Any, AnyUrl]