from fastapi import Body
from sse_starlette.sse import EventSourceResponse
from configs import LLM_MODELS, TEMPERATURE
from server.utils import wrap_done, get_OpenAI
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable, Optional
import asyncio
from langchain.prompts import PromptTemplate

from server.utils import get_prompt_template


async def completion(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
                     stream: bool = Body(False, description="流式输出"),
                     echo: bool = Body(False, description="除了输出之外，还回显输入"),
                     model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
                     temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                     max_tokens: Optional[int] = Body(1024, description="限制LLM生成Token数量，默认None代表模型最大值"),
                     # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
                     prompt_name: str = Body("default",
                                             description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                     ):

    #todo 因ApiModelWorker 默认是按chat处理的，会对params["prompt"] 解析为messages，因此ApiModelWorker 使用时需要有相应处理
    async def completion_iterator(query: str,
                                  model_name: str = LLM_MODELS[0],
                                  prompt_name: str = prompt_name,
                                  echo: bool = echo,
                                  ) -> AsyncIterable[str]:
        nonlocal max_tokens
        callback = AsyncIteratorCallbackHandler()
        if isinstance(max_tokens, int) and max_tokens <= 0:
            max_tokens = None

        model = get_OpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
            echo=echo
        )

        prompt_template = get_prompt_template("completion", prompt_name)
        prompt = PromptTemplate.from_template(prompt_template)
        chain = LLMChain(prompt=prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"input": query}),
            callback.done),
        )

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield token
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield answer

        await task

    return EventSourceResponse(completion_iterator(query=query,
                                                 model_name=model_name,
                                                 prompt_name=prompt_name),
                             )
