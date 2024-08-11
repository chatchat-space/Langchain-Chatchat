import asyncio
import json
import uuid
from typing import AsyncIterable, List

from fastapi import Body
from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, convert_to_messages
from sse_starlette.sse import EventSourceResponse

from chatchat.settings import Settings
from chatchat.server.agent.agent_factory.agents_registry import agents_registry
from chatchat.server.api_server.api_schemas import OpenAIChatOutput
from chatchat.server.callback_handler.agent_callback_handler import (
    AgentExecutorAsyncIteratorCallbackHandler,
    AgentStatus,
)
from chatchat.server.chat.utils import History
from chatchat.server.memory.conversation_db_buffer_memory import (
    ConversationBufferDBMemory,
)
from chatchat.server.utils import (
    MsgType,
    get_ChatOpenAI,
    get_prompt_template,
    get_tool,
    wrap_done,
    get_default_llm,
    get_default_graph,
    build_logger,
    get_graph,
    get_history_len,
)

from langchain_openai.chat_models import ChatOpenAI

logger = build_logger()


# def create_models_from_config(configs, callbacks, stream, max_tokens):
#     configs = configs or Settings.model_settings.LLM_MODEL_CONFIG
#     models = {}
#     prompts = {}
#     for model_type, params in configs.items():
#         model_name = params.get("model", "").strip() or get_default_llm()
#         callbacks = callbacks if params.get("callbacks", False) else None
#         # 判断是否传入 max_tokens 的值, 如果传入就按传入的赋值(api 调用且赋值), 如果没有传入则按照初始化配置赋值(ui 调用或 api 调用未赋值)
#         max_tokens_value = max_tokens if max_tokens is not None else params.get("max_tokens", 1000)
#         model_instance = get_ChatOpenAI(
#             model_name=model_name,
#             temperature=params.get("temperature", 0.5),
#             max_tokens=max_tokens_value,
#             callbacks=callbacks,
#             streaming=stream,
#             local_wrap=True,
#         )
#         models[model_type] = model_instance
#         prompt_name = params.get("prompt_name", "default")
#         prompt_template = get_prompt_template(type=model_type, name=prompt_name)
#         prompts[model_type] = prompt_template
#     return models, prompts


# def create_models_chains(
#     history, history_len, prompts, models, tools, callbacks, conversation_id, metadata
# ):
#     memory = None
#     chat_prompt = None
#
#     if history:
#         history = [History.from_data(h) for h in history]
#         input_msg = History(role="user", content=prompts["llm_model"]).to_msg_template(
#             False
#         )
#         chat_prompt = ChatPromptTemplate.from_messages(
#             [i.to_msg_template() for i in history] + [input_msg]
#         )
#     elif conversation_id and history_len > 0:
#         memory = ConversationBufferDBMemory(
#             conversation_id=conversation_id,
#             llm=models["llm_model"],
#             message_limit=history_len,
#         )
#     else:
#         input_msg = History(role="user", content=prompts["llm_model"]).to_msg_template(
#             False
#         )
#         chat_prompt = ChatPromptTemplate.from_messages([input_msg])
#
#     if "action_model" in models and tools:
#         llm = models["action_model"]
#         llm.callbacks = callbacks
#         agent_executor = agents_registry(
#             llm=llm, callbacks=callbacks, tools=tools, prompt=None, verbose=True
#         )
#         full_chain = {"input": lambda x: x["input"]} | agent_executor
#     else:
#         llm = models["llm_model"]
#         llm.callbacks = callbacks
#         chain = LLMChain(prompt=chat_prompt, llm=llm, memory=memory)
#         full_chain = {"input": lambda x: x["input"]} | chain
#     return full_chain


# async def chat(
#     query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
#     metadata: dict = Body({}, description="附件，可能是图像或者其他功能", examples=[]),
#     conversation_id: str = Body("", description="对话框ID"),
#     message_id: str = Body(None, description="数据库消息ID"),
#     history_len: int = Body(-1, description="从数据库中取历史消息的数量"),
#     history: List[History] = Body(
#         [],
#         description="历史对话，设为一个整数可以从数据库中读取历史消息",
#         examples=[
#             [
#                 {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
#                 {"role": "assistant", "content": "虎头虎脑"},
#             ]
#         ],
#     ),
#     stream: bool = Body(True, description="流式输出"),
#     chat_model_config: dict = Body({}, description="LLM 模型配置", examples=[]),
#     tool_config: dict = Body({}, description="工具配置", examples=[]),
#     max_tokens: int = Body(None, description="LLM最大token数配置", example=4096),
# ):
#     """Agent 对话"""
#
#     async def chat_iterator() -> AsyncIterable[OpenAIChatOutput]:
#         try:
#             callback = AgentExecutorAsyncIteratorCallbackHandler()
#             callbacks = [callback]
#
#             # Enable langchain-chatchat to support langfuse
#             import os
#
#             langfuse_secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
#             langfuse_public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
#             langfuse_host = os.environ.get("LANGFUSE_HOST")
#             if langfuse_secret_key and langfuse_public_key and langfuse_host:
#                 from langfuse import Langfuse
#                 from langfuse.callback import CallbackHandler
#
#                 langfuse_handler = CallbackHandler()
#                 callbacks.append(langfuse_handler)
#
#             models, prompts = create_models_from_config(
#                 callbacks=callbacks, configs=chat_model_config, stream=stream, max_tokens=max_tokens
#             )
#
#             all_tools = get_tool().values()
#
#             tools = [tool for tool in all_tools if tool.name in tool_config]
#             tools = [t.copy(update={"callbacks": callbacks}) for t in tools]
#
#             full_chain = create_models_chains(
#                 prompts=prompts,
#                 models=models,
#                 conversation_id=conversation_id,
#                 tools=tools,
#                 callbacks=callbacks,
#                 history=history,
#                 history_len=history_len,
#                 metadata=metadata,
#             )
#
#             _history = [History.from_data(h) for h in history]
#             chat_history = [h.to_msg_tuple() for h in _history]
#             history_message = convert_to_messages(chat_history)
#             task = asyncio.create_task(
#                 wrap_done(
#                     full_chain.ainvoke(
#                         {
#                             "input": query,
#                             "chat_history": history_message,
#                         }
#                     ),
#                     callback.done,
#                 )
#             )
#
#             last_tool = {}
#             async for chunk in callback.aiter():
#                 data = json.loads(chunk)
#                 data["tool_calls"] = []
#                 data["message_type"] = MsgType.TEXT
#
#                 if data["status"] == AgentStatus.tool_start:
#                     last_tool = {
#                         "index": 0,
#                         "id": data["run_id"],
#                         "type": "function",
#                         "function": {
#                             "name": data["tool"],
#                             "arguments": data["tool_input"],
#                         },
#                         "tool_output": None,
#                         "is_error": False,
#                     }
#                     data["tool_calls"].append(last_tool)
#                 if data["status"] in [AgentStatus.tool_end]:
#                     last_tool.update(
#                         tool_output=data["tool_output"],
#                         is_error=data.get("is_error", False),
#                     )
#                     data["tool_calls"] = [last_tool]
#                     last_tool = {}
#                     try:
#                         tool_output = json.loads(data["tool_output"])
#                         if message_type := tool_output.get("message_type"):
#                             data["message_type"] = message_type
#                     except:
#                         ...
#                 elif data["status"] == AgentStatus.agent_finish:
#                     try:
#                         tool_output = json.loads(data["text"])
#                         if message_type := tool_output.get("message_type"):
#                             data["message_type"] = message_type
#                     except:
#                         ...
#
#                 ret = OpenAIChatOutput(
#                     id=f"chat{uuid.uuid4()}",
#                     object="chat.completion.chunk",
#                     content=data.get("text", ""),
#                     role="assistant",
#                     tool_calls=data["tool_calls"],
#                     model=models["llm_model"].model_name,
#                     status=data["status"],
#                     message_type=data["message_type"],
#                     message_id=message_id,
#                 )
#                 yield ret.model_dump_json()
#             # yield OpenAIChatOutput( # return blank text lastly
#             #         id=f"chat{uuid.uuid4()}",
#             #         object="chat.completion.chunk",
#             #         content="",
#             #         role="assistant",
#             #         model=models["llm_model"].model_name,
#             #         status = data["status"],
#             #         message_type = data["message_type"],
#             #         message_id=message_id,
#             # )
#             await task
#         except asyncio.exceptions.CancelledError:
#             logger.warning("streaming progress has been interrupted by user.")
#             return
#         except Exception as e:
#             logger.error(f"error in chat: {e}")
#             yield {"data": json.dumps({"error": str(e)})}
#             return
#
#     if stream:
#         return EventSourceResponse(chat_iterator())
#     else:
#         ret = OpenAIChatOutput(
#             id=f"chat{uuid.uuid4()}",
#             object="chat.completion",
#             content="",
#             role="assistant",
#             finish_reason="stop",
#             tool_calls=[],
#             status=AgentStatus.agent_finish,
#             message_type=MsgType.TEXT,
#             message_id=message_id,
#         )
#
#         async for chunk in chat_iterator():
#             data = json.loads(chunk)
#             if text := data["choices"][0]["delta"]["content"]:
#                 ret.content += text
#             if data["status"] == AgentStatus.tool_end:
#                 ret.tool_calls += data["choices"][0]["delta"]["tool_calls"]
#             ret.model = data["model"]
#             ret.created = data["created"]
#
#         return ret.model_dump()


def _create_agent_models(configs, model, max_tokens, temperature, stream) -> ChatOpenAI:
    # Settings.model_settings.LLM_MODEL_CONFIG 数据结构 与 UI 传入 configs 数据结构不同, 故分开处理
    if not configs:
        configs = Settings.model_settings.LLM_MODEL_CONFIG
        agent_configs = configs.get("action_model", {})
        model = model or agent_configs["model"] or get_default_llm()
        max_tokens = max_tokens or agent_configs["max_tokens"]
        # 考虑到不同来源请求时 agent 的表现, temperature 默认最高优先级使用开发组推荐配置(LLM_MODEL_CONFIG.action_model.temperature).
        # 开发者们如有需要可以将此顺序交换.
        temperature = agent_configs["temperature"] or temperature
    else:
        agent_configs = configs.get("action_model", {})
        model = model or agent_configs["model"] or get_default_llm()
        for _, agent_model_config in agent_configs.items():
            max_tokens = max_tokens or agent_model_config.get("max_tokens")
            temperature = agent_model_config.get("temperature") or temperature

    return get_ChatOpenAI(model_name=model, temperature=temperature, max_tokens=max_tokens, callbacks=[],
                          streaming=stream, local_wrap=False)


async def chat(
    query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
    model: str = Body(None, description="llm", example="gpt-4o-mini"),
    graph: str = Body(None, description="使用的 graph 名称", example="base_graph"),
    metadata: dict = Body({}, description="附件，可能是图像或者其他功能", examples=[]),
    conversation_id: str = Body("", description="对话框ID"),
    message_id: str = Body(None, description="数据库消息ID"),
    chat_model_config: dict = Body({}, description="LLM 模型配置", examples=[]),
    tool_config: dict = Body({}, description="工具配置", examples=[]),
    max_tokens: int = Body(None, description="LLM 最大 token 数配置", example=4096),
    temperature: float = Body(None, description="LLM temperature 配置", example=0.01),
    stream: bool = Body(True, description="流式输出"),
):
    """Agent 对话"""
    async def graph_chat_iterator() -> AsyncIterable[str]:
        all_tools = get_tool().values()
        tools = [tool for tool in all_tools if tool.name in tool_config]
        try:
            llm = _create_agent_models(configs=chat_model_config,
                                       model=model,
                                       max_tokens=max_tokens,
                                       temperature=temperature,
                                       stream=stream)
            # 检查 llm 是否创建成功
            if llm is None:
                raise Exception(f"failed to create ChatOpenAI for model: {model}.")
        except Exception as e:
            logger.error(f"error in create ChatOpenAI: {e}")
            yield json.dumps({"error": str(e)})
            return

        logger.info(f"this agent conversation info:\n"
                    f"id: {conversation_id}\n"
                    f"query: {query}\n"
                    f"llm: {llm}\n"
                    f"tools: {tools}")

        graph_name = graph or get_default_graph() or "base_graph"
        history_len = get_history_len()
        graph_info = get_graph(name=graph_name, llm=llm, tools=tools, history_len=history_len)
        if not graph_info:
            raise ValueError(f"Graph '{graph_name}' is not registered.")

        graph_instance = graph_info["graph_instance"]
        input_handler = graph_info["input_handler"]
        event_handler = graph_info["event_handler"]

        inputs = input_handler.create_inputs(query, metadata)
        config = {"configurable": {"thread_id": conversation_id}}

        try:
            # 因 stream_log 输出处理太过复杂, 将来考虑是否支持, 目前暂时使用 stream
            events = graph_instance.stream(inputs, config, stream_mode="values")
            for event in events:
                res_content = event_handler.handle_event(event)
                logger.info(f"this agent conversation info:\n"
                            f"id: {conversation_id}\n"
                            f"result event:\n"
                            f"{res_content}\n")

                graph_res = OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    object="chat.completion.chunk",
                    content=res_content,
                    role="assistant",
                    tool_calls=[],
                    model=llm.model_name,
                    status=AgentStatus.agent_finish,
                    message_type=MsgType.TEXT,
                    message_id=message_id,
                )
                yield graph_res.model_dump_json()

        except asyncio.exceptions.CancelledError:
            logger.warning("Streaming progress has been interrupted by user.")
            return
        except Exception as e:
            logger.error(f"Error in chatgraph: {e}")
            yield json.dumps({"error": str(e)})
            return

        # snapshot = graph_instance.get_state(config)  # debug
        # print(f"snapshot: {snapshot}")

    if stream:
        return EventSourceResponse(graph_chat_iterator())
    else:
        ret = OpenAIChatOutput(
            id=f"chat{uuid.uuid4()}",
            object="chat.completion",
            content="",
            role="assistant",
            finish_reason="stop",
            tool_calls=[],
            status=AgentStatus.agent_finish,
            message_type=MsgType.TEXT,
            message_id=message_id,
        )

        async for chunk in graph_chat_iterator():
            data = json.loads(chunk)
            if text := data.get("content"):
                ret.content += text
            ret.model = data.get("model")
            ret.created = data.get("created")

        return ret.model_dump()
