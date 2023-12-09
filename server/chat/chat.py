from fastapi import Body
from fastapi.responses import StreamingResponse
from langchain.agents import initialize_agent, AgentType
from langchain_core.callbacks import AsyncCallbackManager, BaseCallbackManager
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
from server.callback_handler.agent_callback_handler import Status, CustomAsyncIteratorCallbackHandler


def create_models_from_config(configs, callbacks):
    if configs is None:
        configs = {}
    models = {}
    prompts = {}
    for model_type, model_configs in configs.items():
        for model_name, params in model_configs.items():
            callback = callbacks if params.get('callbacks', False) else None
            model_instance = get_ChatOpenAI(
                model_name=model_name,
                temperature=params.get('temperature', 0.5),
                max_tokens=params.get('max_tokens', 1000),
                callbacks=callback
            )
            models[model_type] = model_instance
            prompt_name = params.get('prompt_name', 'default')
            prompt_template = get_prompt_template(type=model_type, name=prompt_name)
            prompts[model_type] = prompt_template
    return models, prompts


# 在这里写构建逻辑
def create_models_chains(history, history_len, prompts, models, tools, callbacks, conversation_id, metadata):
    memory = None
    chat_prompt = None
    if history:
        history = [History.from_data(h) for h in history]
        input_msg = History(role="user", content=prompts["llm_model"]).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
    elif conversation_id and history_len > 0:
        memory = ConversationBufferDBMemory(conversation_id=conversation_id, llm=models["llm_model"],
                                            message_limit=history_len)
    else:
        input_msg = History(role="user", content=prompts["llm_model"]).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages([input_msg])

    chain = LLMChain(prompt=chat_prompt, llm=models["llm_model"], memory=memory)
    classifier_chain = (
            PromptTemplate.from_template(prompts["preprocess_model"])
            | models["preprocess_model"]
            | StrOutputParser()
    )
    if "chatglm3" in models["action_model"].model_name.lower():
        agent_executor = initialize_glm3_agent(
            llm=models["action_model"],
            tools=tools,
            prompt=prompts["action_model"],
            input_variables=["input", "intermediate_steps", "history"],
            memory=memory,
            callback_manager=BaseCallbackManager(handlers=callbacks),
            verbose=True,
        )
    else:
        agent_executor = initialize_agent(
            llm=models["action_model"],
            tools=tools,
            callbacks=callbacks,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
        )
    agent_use = False
    if agent_use:
        branch = RunnableBranch(
            (lambda x: "1" in x["topic"].lower(), agent_executor),
            chain
        )
        full_chain = ({"topic": classifier_chain, "input": lambda x: x["input"]} | branch)
    else:
        full_chain = ({"input": lambda x: x["input"]} | chain)
    return full_chain


async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               metadata: dict = Body({}, description="附件，可能是图像或者其他功能", examples=[]),
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
        message_id = add_message_to_db(chat_type="llm_chat", query=query, conversation_id=conversation_id) if conversation_id else  None
        callback = CustomAsyncIteratorCallbackHandler()
        callbacks = [callback]
        models, prompts = create_models_from_config(callbacks=callbacks, configs=model_config)
        tools = [tool for tool in all_tools if tool.name in tool_config]
        # 构建完整的Chain
        full_chain = create_models_chains(prompts=prompts,
                                          models=models,
                                          conversation_id=conversation_id,
                                          tools=tools,
                                          callbacks=callbacks,
                                          history=history,
                                          history_len=history_len,
                                          metadata=metadata)

        # 执行完整的Chain
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

    return EventSourceResponse(chat_iterator())
