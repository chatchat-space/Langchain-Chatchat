from fastapi import Body
from fastapi.responses import StreamingResponse
from configs import LLM_MODEL, TEMPERATURE, SAVE_CHAT_HISTORY
from server.utils import wrap_done, get_ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List, Optional
from server.chat.utils import History
from server.utils import get_prompt_template
from server.db.repository.chat_history_repository import add_chat_history_to_db


async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               history: List[History] = Body([],
                                             description="历史对话",
                                             examples=[[
                                                 {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                 {"role": "assistant", "content": "虎头虎脑"}]]
                                             ),
               stream: bool = Body(False, description="流式输出"),
               model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
               max_tokens: int = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
               prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
               chat_history_id: str = Body("", max_length=20, description="聊天记录id"),
               ):
    history = [History.from_data(h) for h in history]

    async def chat_iterator(query: str,
                            history: List[History] = [],
                            model_name: str = LLM_MODEL,
                            prompt_name: str = prompt_name,
                            chat_history_id: str = chat_history_id
                            ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )

        prompt_template = get_prompt_template("llm_chat", prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"input": query}),
            callback.done),
        )

        answer = ""
        if stream:
            async for token in callback.aiter():
                answer += token
                # Use server-sent-events to stream the response
                yield token
        else:
            async for token in callback.aiter():
                answer += token
            yield answer
        if SAVE_CHAT_HISTORY and len(chat_history_id) > 0:
            # 后续可以加入一些其他信息，比如真实的prompt等
            add_chat_history_to_db(chat_history_id, "chat", query, answer)
        await task

    return StreamingResponse(chat_iterator(query=query,
                                           history=history,
                                           model_name=model_name,
                                           prompt_name=prompt_name,
                                           chat_history_id=chat_history_id),
                             media_type="text/event-stream")
