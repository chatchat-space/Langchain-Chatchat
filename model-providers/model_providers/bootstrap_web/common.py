import typing
from subprocess import Popen
from typing import Optional

from model_providers.core.bootstrap.openai_protocol import ChatCompletionStreamResponseChoice, \
    ChatCompletionStreamResponse, Finish
from model_providers.core.utils.generic import jsonify

if typing.TYPE_CHECKING:
    from model_providers.core.bootstrap.openai_protocol import ChatCompletionMessage


def create_stream_chunk(
        request_id: str,
        model: str,
        delta: "ChatCompletionMessage",
        index: Optional[int] = 0,
        finish_reason: Optional[Finish] = None,
) -> str:
    choice = ChatCompletionStreamResponseChoice(index=index, delta=delta, finish_reason=finish_reason)
    chunk = ChatCompletionStreamResponse(id=request_id, model=model, choices=[choice])
    return jsonify(chunk)
