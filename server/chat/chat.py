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
from typing import List, Optional
from server.chat.utils import History
from langchain.prompts import PromptTemplate
from server.utils import get_prompt_template
from server.memory.conversation_db_buffer_memory import ConversationBufferDBMemory
from server.db.repository import add_message_to_db
from server.callback_handler.conversation_callback_handler import ConversationCallbackHandler

async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               conversation_id: str = Body(..., description="对话框ID"),
               stream: bool = Body(False, description="流式输出"),
               model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
               max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
               prompt_name: str = Body("with_history", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
               ):

    async def chat_iterator(query: str,
                            conversation_id: str = "",
                            model_name: str = LLM_MODELS[0],
                            prompt_name: str = prompt_name,
                            ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()

        message_id = add_message_to_db(chat_type="llm_chat", query=query, conversation_id=conversation_id)
        conversation_callback = ConversationCallbackHandler(conversation_id=conversation_id, message_id=message_id,
                                                            chat_type="chat2",
                                                            query=query)

        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback,conversation_callback],
        )
        memory = ConversationBufferDBMemory(conversation_id=conversation_id, llm=model)

        prompt = get_prompt_template("llm_chat", prompt_name)
        prompt_template = PromptTemplate.from_template(prompt)

        chain = LLMChain(prompt=prompt_template, llm=model, memory=memory)

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

    return StreamingResponse(chat_iterator(query=query,
                                           conversation_id=conversation_id,
                                           model_name=model_name,
                                           prompt_name=prompt_name),
                             media_type="text/event-stream")