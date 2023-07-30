from fastapi import Body
from fastapi.responses import StreamingResponse
from typing import List, Dict
import openai
from configs.model_config import llm_model_dict, LLM_MODEL
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
    stream: bool = True
    presence_penalty: int = 0
    frequency_penalty: int = 0


async def openai_chat(msg: OpenAiChatMsgIn):
    openai.api_key = llm_model_dict[LLM_MODEL]["api_key"]
    print(f"{openai.api_key=}")
    openai.api_base = llm_model_dict[LLM_MODEL]["api_base_url"]
    print(f"{openai.api_base=}")
    print(msg)

    async def get_response(msg):
        response = openai.ChatCompletion.create(**msg.dict())
        for chunk in response.choices[0].message.content:
            print(chunk)
            yield chunk

    return StreamingResponse(
        get_response(msg),
        media_type='text/event-stream',
    )
