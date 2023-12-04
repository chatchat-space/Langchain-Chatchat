from fastapi import Body
from fastapi.responses import StreamingResponse
from langchain.agents import initialize_agent, AgentType
from langchain_core.callbacks import AsyncCallbackManager
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch
from server.agent.agent_factory import initialize_glm3_agent
from server.agent.tools_factory.tools_registry import all_tools
from server.utils import wrap_done, get_ChatOpenAI
from langchain.chains import LLMChain
from typing import AsyncIterable, Dict
import asyncio
import json
from langchain.prompts.chat import ChatPromptTemplate
from typing import List, Union
from server.chat.utils import History
from langchain.prompts import PromptTemplate
from server.utils import get_prompt_template
from server.memory.conversation_db_buffer_memory import ConversationBufferDBMemory
from server.db.repository import add_message_to_db
from server.callback_handler.conversation_callback_handler import ConversationCallbackHandler
from server.callback_handler.agent_callback_handler import Status, CustomAsyncIteratorCallbackHandler


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
               model_config: Dict = Body({}, description="LLM 模型配置。"),
               tool_config: Dict = Body({}, description="工具配置"),
               ):
    async def chat_iterator() -> AsyncIterable[str]:
        nonlocal history
        callback = CustomAsyncIteratorCallbackHandler()
        callbacks = [callback]
        memory = None
        message_id = None

        model_llm_name = next(iter(model_config['llm_model']))
        model_llm_config = model_config['llm_model'][model_llm_name]
        model_agent_name = next(iter(model_config['agent_model']))
        model_agent_config = model_config['agent_model'][model_agent_name]

        if conversation_id:
            message_id = add_message_to_db(chat_type="llm_chat", query=query, conversation_id=conversation_id)
            conversation_callback = ConversationCallbackHandler(conversation_id=conversation_id, message_id=message_id,
                                                                chat_type="llm_chat",
                                                                query=query)
            callbacks.append(conversation_callback)

        tools = [tool for tool in all_tools if tool.name in tool_config]

        model_llm = get_ChatOpenAI(
            model_name=model_llm_name,
            temperature=model_llm_config['temperature'],
            max_tokens=model_llm_config['max_tokens'],
            callbacks=callbacks,
        )
        model_agent = get_ChatOpenAI(
            model_name=model_agent_name,
            temperature=model_agent_config['temperature'],
            max_tokens=model_agent_config['max_tokens'],
            callbacks=callbacks,
        )

        if history:
            history = [History.from_data(h) for h in history]
            prompt_template = get_prompt_template("llm_chain", model_llm_config["prompt_name"])
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages(
                [i.to_msg_template() for i in history] + [input_msg])
        elif conversation_id and history_len > 0:
            prompt = get_prompt_template("llm_chain", "with_history")
            chat_prompt = PromptTemplate.from_template(prompt)
            memory = ConversationBufferDBMemory(conversation_id=conversation_id,
                                                llm=model_llm,
                                                message_limit=history_len)
        else:
            prompt_template = get_prompt_template("llm_chain", model_llm_config["prompt_name"])
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages([input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model_llm, memory=memory)

        prompt_template_agent = get_prompt_template("agent_chain", model_agent_config["prompt_name"])
        prompt_template_classifier = get_prompt_template("classifier_chain", "default")
        classifier_chain = (
                PromptTemplate.from_template(prompt_template_classifier)
                | model_llm
                | StrOutputParser()
        )
        if "chatglm3" in model_agent_name.lower():
            # callback_manager1 = AsyncCallbackManager(),
            agent_executor = initialize_glm3_agent(
                llm=model_agent,
                tools=tools,
                prompt=prompt_template_agent,
                input_variables=["input", "intermediate_steps", "history"],
                memory=memory,
                callback_manager=AsyncCallbackManager(handlers=callbacks),
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
