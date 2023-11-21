from fastapi import Body
from fastapi.responses import StreamingResponse
from configs import LLM_MODELS, TEMPERATURE
from server.utils import wrap_done, get_ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
import json
from langchain.prompts.chat import ChatPromptTemplate
from typing import List, Optional, Union
from server.chat.utils import History
from langchain.prompts import PromptTemplate
from server.utils import get_prompt_template
from server.memory.conversation_db_buffer_memory import ConversationBufferDBMemory
from server.db.repository import add_message_to_db
from server.callback_handler.conversation_callback_handler import ConversationCallbackHandler


async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               conversation_id: str = Body(None, description="对话框ID"),
               history: Union[int, List[History]] = Body(None,
                                                    description="历史对话，设为一个整数可以从数据库中读取历史消息",
                                                    examples=[[
                                                        {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                        {"role": "assistant", "content": "虎头虎脑"}]]
                                                    ),
               stream: bool = Body(False, description="流式输出"),
               model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
               max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
               prompt_name: str = Body("defalut", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
               ):

    async def chat_iterator() -> AsyncIterable[str]:
        nonlocal history
        callback = AsyncIteratorCallbackHandler()
        callbacks = [callback]
        memory = None

        if conversation_id is not None:
            message_id = add_message_to_db(chat_type="llm_chat", query=query, conversation_id=conversation_id)
            conversation_callback = ConversationCallbackHandler(conversation_id=conversation_id, message_id=message_id,
                                                                chat_type="llm_chat",
                                                                query=query)
            callbacks.append(conversation_callback)

        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=callbacks,
        )

        if conversation_id is None:
            history = [History.from_data(h) for h in history]
            prompt_template = get_prompt_template("llm_chat", prompt_name)
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages(
                [i.to_msg_template() for i in history] + [input_msg])
        else:
            prompt = get_prompt_template("llm_chat", prompt_name)
            chat_prompt = PromptTemplate.from_template(prompt)
            memory = ConversationBufferDBMemory(conversation_id=conversation_id, llm=model)

        chain = LLMChain(prompt=chat_prompt, llm=model, memory=memory)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"input": query}),
            callback.done),
        )

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps(
                    {"text": token, "message_id": message_id},
                    ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps(
                {"text": answer, "message_id": message_id},
                ensure_ascii=False)

        await task

    return StreamingResponse(chat_iterator(), media_type="text/event-stream")