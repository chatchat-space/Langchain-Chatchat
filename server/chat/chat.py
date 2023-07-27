from fastapi import Body
from fastapi.responses import StreamingResponse
from configs.model_config import llm_model_dict, LLM_MODEL
from .utils import wrap_done
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts import PromptTemplate


def chat(query: str = Body(..., description="用户输入", example="你好")):
    async def chat_iterator(message: str) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()

        model = ChatOpenAI(
            streaming=True,
            verbose=True,
            callbacks=[callback],
            openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
            openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
            model_name=LLM_MODEL
        )

        # llm = OpenAI(model_name=LLM_MODEL,
        #              openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
        #              openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
        #              streaming=True)

        prompt = PromptTemplate(input_variables=["input"], template="{input}")
        chain = LLMChain(prompt=prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall(message),
            callback.done),
        )

        async for token in callback.aiter():
            # Use server-sent-events to stream the response
            yield token
        await task
    return StreamingResponse(chat_iterator(query), media_type="text/event-stream")