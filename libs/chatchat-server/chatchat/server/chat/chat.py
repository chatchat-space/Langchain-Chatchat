import asyncio
import json
import time
from typing import AsyncIterable, List
import uuid

from fastapi import Body
from sse_starlette.sse import EventSourceResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, convert_to_messages

from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts import PromptTemplate

from chatchat.configs import LLM_MODEL_CONFIG
from chatchat.server.agent.agent_factory.agents_registry import agents_registry
from chatchat.server.agent.container import container
from chatchat.server.api_server.api_schemas import OpenAIChatOutput
from chatchat.server.utils import wrap_done, get_ChatOpenAI, get_prompt_template, MsgType, get_tool
from chatchat.server.chat.utils import History
from chatchat.server.memory.conversation_db_buffer_memory import ConversationBufferDBMemory
from chatchat.server.callback_handler.agent_callback_handler import AgentExecutorAsyncIteratorCallbackHandler, AgentStatus


def create_models_from_config(configs, callbacks, stream):
    configs = configs or LLM_MODEL_CONFIG
    models = {}
    prompts = {}
    for model_type, model_configs in configs.items():
        for model_name, params in model_configs.items():
            callbacks = callbacks if params.get('callbacks', False) else None
            model_instance = get_ChatOpenAI(
                model_name=model_name,
                temperature=params.get('temperature', 0.5),
                max_tokens=params.get('max_tokens', 1000),
                callbacks=callbacks,
                streaming=stream,
                local_wrap=True,
            )
            models[model_type] = model_instance
            prompt_name = params.get('prompt_name', 'default')
            prompt_template = get_prompt_template(type=model_type, name=prompt_name)
            prompts[model_type] = prompt_template
    return models, prompts


def create_models_chains(history, history_len, prompts, models, tools, callbacks, conversation_id, metadata):
    memory = None
    chat_prompt = None
    container.metadata = metadata

    if history:
        history = [History.from_data(h) for h in history]
        input_msg = History(role="user", content=prompts["llm_model"]).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
    elif conversation_id and history_len > 0:
        memory = ConversationBufferDBMemory(
            conversation_id=conversation_id,
            llm=models["llm_model"],
            message_limit=history_len
        )
    else:
        input_msg = History(role="user", content=prompts["llm_model"]).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages([input_msg])

    llm=models["llm_model"]
    llm.callbacks = callbacks
    chain = LLMChain(
        prompt=chat_prompt,
        llm=llm,
        memory=memory
    )

    if "action_model" in models and tools is not None:
        agent_executor = agents_registry(
            llm=llm,
            callbacks=callbacks,
            tools=tools,
            prompt=None,
            verbose=True
        )
        full_chain = ({"input": lambda x: x["input"]} | agent_executor)
    else:
        chain.llm.callbacks = callbacks
        full_chain = ({"input": lambda x: x["input"]} | chain)
    return full_chain


async def chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
               metadata: dict = Body({}, description="附件，可能是图像或者其他功能", examples=[]),
               conversation_id: str = Body("", description="对话框ID"),
               message_id: str = Body(None, description="数据库消息ID"),
               history_len: int = Body(-1, description="从数据库中取历史消息的数量"),
               history: List[History] = Body(
                   [],
                   description="历史对话，设为一个整数可以从数据库中读取历史消息",
                   examples=[
                       [
                           {"role": "user",
                            "content": "我们来玩成语接龙，我先来，生龙活虎"},
                           {"role": "assistant", "content": "虎头虎脑"}
                       ]
                   ]
               ),
               stream: bool = Body(True, description="流式输出"),
               chat_model_config: dict = Body({}, description="LLM 模型配置", examples=[]),
               tool_config: dict = Body({}, description="工具配置", examples=[]),
               ):
    '''Agent 对话'''

    async def chat_iterator() -> AsyncIterable[OpenAIChatOutput]:
        callback = AgentExecutorAsyncIteratorCallbackHandler()
        callbacks = [callback]

        # Enable langchain-chatchat to support langfuse
        import os
        langfuse_secret_key = os.environ.get('LANGFUSE_SECRET_KEY')
        langfuse_public_key = os.environ.get('LANGFUSE_PUBLIC_KEY')
        langfuse_host = os.environ.get('LANGFUSE_HOST')
        if langfuse_secret_key and langfuse_public_key and langfuse_host :
            from langfuse import Langfuse
            from langfuse.callback import CallbackHandler
            langfuse_handler = CallbackHandler()
            callbacks.append(langfuse_handler)

        models, prompts = create_models_from_config(callbacks=callbacks, configs=chat_model_config,
                                                    stream=stream)
        all_tools = get_tool().values()
        tools = [tool for tool in all_tools if tool.name in tool_config]
        tools = [t.copy(update={"callbacks": callbacks}) for t in tools]
        full_chain = create_models_chains(prompts=prompts,
                                          models=models,
                                          conversation_id=conversation_id,
                                          tools=tools,
                                          callbacks=callbacks,
                                          history=history,
                                          history_len=history_len,
                                          metadata=metadata)

        _history = [History.from_data(h) for h in history]
        chat_history = [h.to_msg_tuple() for h in _history]

        history_message = convert_to_messages(chat_history)

        task = asyncio.create_task(wrap_done(
            full_chain.ainvoke(
                {
                    "input": query,
                    "chat_history": history_message,
                }
            ), callback.done))

        last_tool = {}
        async for chunk in callback.aiter():
            data = json.loads(chunk)
            data["tool_calls"] = []
            data["message_type"] = MsgType.TEXT

            if data["status"] == AgentStatus.tool_start:
                last_tool = {
                    "index": 0,
                    "id": data["run_id"],
                    "type": "function",
                    "function": {
                        "name": data["tool"],
                        "arguments": data["tool_input"],
                    },
                    "tool_output": None,
                    "is_error": False,
                }
                data["tool_calls"].append(last_tool)
            if data["status"] in [AgentStatus.tool_end]:
                last_tool.update(
                    tool_output=data["tool_output"],
                    is_error=data.get("is_error", False)
                )
                data["tool_calls"] = [last_tool]
                last_tool = {}
                try:
                    tool_output = json.loads(data["tool_output"])
                    if message_type := tool_output.get("message_type"):
                        data["message_type"] = message_type
                except:
                    ...
            elif data["status"] == AgentStatus.agent_finish:
                try:
                    tool_output = json.loads(data["text"])
                    if message_type := tool_output.get("message_type"):
                        data["message_type"] = message_type
                except:
                    ...

            ret = OpenAIChatOutput(
                id=f"chat{uuid.uuid4()}",
                object="chat.completion.chunk",
                content=data.get("text", ""),
                role="assistant",
                tool_calls=data["tool_calls"],
                model=models["llm_model"].model_name,
                status = data["status"],
                message_type = data["message_type"],
                message_id=message_id,
            )
            yield ret.model_dump_json()
        # yield OpenAIChatOutput( # return blank text lastly
        #         id=f"chat{uuid.uuid4()}",
        #         object="chat.completion.chunk",
        #         content="",
        #         role="assistant",
        #         model=models["llm_model"].model_name,
        #         status = data["status"],
        #         message_type = data["message_type"],
        #         message_id=message_id,            
        # )
        await task

    if stream:
        return EventSourceResponse(chat_iterator())
    else:
        ret = OpenAIChatOutput(
            id=f"chat{uuid.uuid4()}",
            object="chat.completion",
            content="",
            role="assistant",
            finish_reason="stop",
            tool_calls=[],
            status = AgentStatus.agent_finish,
            message_type = MsgType.TEXT,
            message_id=message_id,
        )

        async for chunk in chat_iterator():
            data = json.loads(chunk)
            if text := data["choices"][0]["delta"]["content"]:
                ret.content += text
            if data["status"] == AgentStatus.tool_end:
                ret.tool_calls += data["choices"][0]["delta"]["tool_calls"]
            ret.model = data["model"]
            ret.created = data["created"]

        return ret.model_dump()
