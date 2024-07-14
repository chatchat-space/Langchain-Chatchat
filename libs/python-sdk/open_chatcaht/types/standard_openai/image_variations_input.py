from typing import Union, Any

from pydantic import AnyUrl

from chatchat.server.api_server.api_schemas import OpenAIImageBaseInput


class OpenAIImageVariationsInput(OpenAIImageBaseInput):
    image: Union[Any, AnyUrl]
