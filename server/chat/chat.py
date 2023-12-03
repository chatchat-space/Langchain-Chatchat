from operator import itemgetter

from fastapi import Body
from fastapi.responses import StreamingResponse
from langchain.agents import initialize_agent, AgentType
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough

from configs import LLM_MODELS, TEMPERATURE, Agent_MODEL
from server.agent.agent_factory import initialize_glm3_agent
from server.agent.tools_select import tools
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
from server.agent import model_container, Status, CustomAsyncIteratorCallbackHandler


async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               conversation_id: str = Body("", description="对话框ID"),
               history_len: int = Body(-1, description="从数据库中取历史消息的数量"),
               history: Union[int, List[History]] = Body([],
                                                         description="历史对话，设为一个整数可以从数据库中读取历史消息",
                                                         examples=[[
                                                             {"role": "user",
                                                              "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                             {"role": "assistant", "content": "虎头虎脑"}]]
                                                         ),
               stream: bool = Body(False, description="流式输出"),
               model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
               max_tokens: Optional[int] = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
               prompt_name: str = Body("default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
               ):
    async def chat_iterator() -> AsyncIterable[str]:
        nonlocal history, max_tokens
        callback = CustomAsyncIteratorCallbackHandler()
        callbacks = [callback]
        memory = None
        message_id = None
        if conversation_id:
            message_id = add_message_to_db(chat_type="llm_chat", query=query, conversation_id=conversation_id)
            conversation_callback = ConversationCallbackHandler(conversation_id=conversation_id, message_id=message_id,
                                                                chat_type="llm_chat",
                                                                query=query)
            callbacks.append(conversation_callback)
        if isinstance(max_tokens, int) and max_tokens <= 0:
            max_tokens = None

        model_llm = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=callbacks,
        )

        if Agent_MODEL:
            model_agent = get_ChatOpenAI(
                model_name=Agent_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=callbacks,
            )
            model_container.MODEL = model_agent
        else:
            model_container.MODEL = model_llm
            model_agent = model_llm

        if history:
            history = [History.from_data(h) for h in history]
            prompt_template = get_prompt_template("llm_chat", prompt_name)
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages(
                [i.to_msg_template() for i in history] + [input_msg])
        elif conversation_id and history_len > 0:  # 前端要求从数据库取历史消息
            prompt = get_prompt_template("llm_chat", "with_history")
            chat_prompt = PromptTemplate.from_template(prompt)
            memory = ConversationBufferDBMemory(conversation_id=conversation_id,
                                                llm=model_llm,
                                                message_limit=history_len)
        else:
            prompt_template = get_prompt_template("llm_chat", prompt_name)
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages([input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model_llm, memory=memory)

        prompt_template_agent = get_prompt_template("agent_chat", "ChatGLM3")
        prompt_template_classifier = get_prompt_template("llm_chat", "tool")
        classifier_chain = (
                PromptTemplate.from_template(
                    prompt_template_classifier
                )
                | model_llm
                | StrOutputParser()
        )


        if "chatglm3" in model_container.MODEL.model_name:
            agent_executor = initialize_glm3_agent(
                llm=model_agent,
                tools=tools,
                prompt=prompt_template_agent,
                input_variables=["input", "intermediate_steps", "history"],
                memory=memory,
                verbose=True,
            )
        else:
            agent_executor = initialize_agent(
                llm=model_agent,
                tools=tools,
                callbacks=callbacks,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                memory=memory,
                verbose=True,
            )

        branch = RunnableBranch(
            (lambda x: "1" in x["topic"].lower(), agent_executor),
            chain
        )
        full_chain = ({"topic": classifier_chain, "input": lambda x: x["input"]} | branch)
        task = asyncio.create_task(wrap_done(full_chain.ainvoke({"input": query}, callbacks=callbacks), callback.done))
        if stream:
            async for chunk in callback.aiter():
                data = json.loads(chunk)
                if data["status"] == Status.start:
                    continue
                elif data["status"] == Status.agent_action:
                    tool_info = {
                        "tool_name": data["tool_name"],
                        "tool_input": data["tool_input"]
                    }
                    yield json.dumps({"agent_action": tool_info, "message_id": message_id}, ensure_ascii=False)
                elif data["status"] == Status.agent_finish:
                    yield json.dumps({"agent_finish": data["agent_finish"], "message_id": message_id},
                                     ensure_ascii=False)
                else:
                    yield json.dumps({"text": data["llm_token"], "message_id": message_id}, ensure_ascii=False)
        else:
            text = ""
            agent_finish = ""
            tool_info = None
            async for chunk in callback.aiter():
                # Use server-sent-events to stream the response
                data = json.loads(chunk)
                if data["status"] == Status.agent_action:
                    tool_info = {
                        "tool_name": data["tool_name"],
                        "tool_input": data["tool_input"]
                    }
                if data["status"] == Status.agent_finish:
                    agent_finish = data["agent_finish"]
                else:
                    text += data["llm_token"]
            if tool_info:
                yield json.dumps(
                    {"text": text, "agent_action": tool_info, "agent_finish": agent_finish, "message_id": message_id},
                    ensure_ascii=False)
            else:
                yield json.dumps(
                    {"text": text, "message_id": message_id},
                    ensure_ascii=False)
        await task

    return StreamingResponse(chat_iterator(), media_type="text/event-stream")
