from fastapi.responses import StreamingResponse
from typing import List
import openai
from configs.model_config import llm_model_dict, LLM_MODEL, logger
from pydantic import BaseModel


class OpenAiMessage(BaseModel):
    role: str = "user"
    content: str = "hello"


class OpenAiChatMsgIn(BaseModel):
    model: str = LLM_MODEL
    messages: List[OpenAiMessage]
    temperature: float = 0.7
    n: int = 1
    max_tokens: int = 1024
    stop: List[str] = []
    stream: bool = False
    presence_penalty: int = 0
    frequency_penalty: int = 0


async def openai_chat(msg: OpenAiChatMsgIn):
    openai.api_key = llm_model_dict[LLM_MODEL]["api_key"]
    print(f"{openai.api_key=}")
    openai.api_base = llm_model_dict[LLM_MODEL]["api_base_url"]
    print(f"{openai.api_base=}")
    print(msg)

    def get_response(msg):
        data = msg.dict()

        try:
            response = openai.ChatCompletion.create(**data)
            if msg.stream:
                for data in response:
                    if choices := data.choices:
                        if chunk := choices[0].get("delta", {}).get("content"):
                            print(chunk, end="", flush=True)
                            yield chunk
            else:
                if response.choices:
                    answer = response.choices[0].message.content
                    print(answer)
                    yield(answer)
        except Exception as e:
            print(type(e))
            logger.error(e)

    return StreamingResponse(
        get_response(msg),
        media_type='text/event-stream',
    )
