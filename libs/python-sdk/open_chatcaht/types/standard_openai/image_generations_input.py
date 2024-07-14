from typing import Literal, Optional

from chatchat.server.api_server.api_schemas import OpenAIImageBaseInput


class OpenAIImageGenerationsInput(OpenAIImageBaseInput):
    prompt: str
    quality: Literal["standard", "hd"] = None
    style: Optional[Literal["vivid", "natural"]] = None