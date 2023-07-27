from fastapi import Body
from fastapi.responses import StreamingResponse
from typing import List, Dict
import openai
from configs.model_config import llm_model_dict, LLM_MODEL

async def openai_chat(messages: List[Dict] = Body(...,
                                                  description="用户输入",
                                                  example=[{"role": "user", "content": "你好"}])):
    openai.api_key = llm_model_dict[LLM_MODEL]["api_key"]
    print(f"{openai.api_key=}")
    openai.api_base = llm_model_dict[LLM_MODEL]["api_base_url"]
    print(f"{openai.api_base=}")
    print(messages)

    async def get_response(messages: List[Dict]):
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=messages,
        )
        for chunk in response.choices[0].message.content:
            print(chunk)
            yield chunk

    return StreamingResponse(
        get_response(messages),
        media_type='text/event-stream',
    )