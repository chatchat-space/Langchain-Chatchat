import asyncio
import json
import uuid
from typing import AsyncIterable

import rich
from fastapi import Body
from langgraph.graph.graph import CompiledGraph
from sse_starlette.sse import EventSourceResponse

from chatchat.server.api_server.api_schemas import OpenAIChatOutput
from chatchat.server.langgraph.node_factory.build_flow import build_flow
from chatchat.server.utils import (
    MsgType,
    build_logger,
)
from langchain_chatchat.callbacks.agent_callback_handler import AgentStatus

logger = build_logger()
async def flow_chat(
    query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
    model: str = Body(None, description="llm", example="gpt-4o-mini"),
    flow: dict = Body({}, description="流程编排数据", examples=[]),
    metadata: dict = Body({}, description="附件，可能是图像或者其他功能", examples=[]),
    conversation_id: str = Body("", description="对话框ID"),
    message_id: str = Body(None, description="消息ID"),
    flow_thread_id: str = Body(None, description="ThreadID"),
    node_id: str = Body("", description="节点ID"),
    max_tokens: int = Body(None, description="LLM 最大 token 数配置", example=4096),
    temperature: float = Body(None, description="LLM temperature 配置", example=0.01),
    stream: bool = Body(False, description="流式输出"),
):
    """Flow 对话"""
    async def flow_chat_iterator() -> AsyncIterable[str]:
        logger.info(f"开始执行flow:{flow}")
        langgraph_flow:CompiledGraph=build_flow(flow)
        inputs={"state":{"__start__":{"question":query}}}
        # 如果thread_id为空，则取message_id
        thread_id=""
        if not flow_thread_id:
            thread_id=message_id
        else:
            thread_id=flow_thread_id
            inputs=None
        thread = {"configurable": {"thread_id": thread_id}}
        if inputs==None:
            state=langgraph_flow.get_state(thread).values
            user_input_output_kwargs={
                "user_input":query
            }
            state["state"][node_id]=user_input_output_kwargs
            langgraph_flow.update_state(thread, state)
        try:
            async for event in langgraph_flow.astream(inputs, thread,stream_mode="debug"):
                # 只保留最后一个输出结果
                # 获取嵌套字典
                if event["type"]=="task_result":
                    nested_dict = event["payload"]["result"][0][1]
                    # 提取最后一个键值对
                    last_key_value_pair = list(nested_dict.items())[-1]
                    # 构建新字典
                    new_nested_dict = {last_key_value_pair[0]: last_key_value_pair[1]}
                    # 替换原有的嵌套字典
                    new_tuple = ('state', new_nested_dict)
                    event["payload"]["result"][0] = new_tuple

                if 'payload' in event:
                    if 'config' in event['payload']:
                        if 'metadata' in event['payload']['config']:
                            dict_data=dict(event['payload']['config']['metadata'])
                            event['payload']['config']['metadata'] = dict_data

                res_content = json.dumps(event, ensure_ascii=False)
                rich.print("执行结果："+res_content)
                graph_res = OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    object="chat.completion.chunk",
                    content=res_content,
                    role="assistant",
                    tool_calls=[],
                    model=model,
                    status=AgentStatus.agent_finish,
                    message_type=MsgType.TEXT,
                    message_id=message_id,
                )
                yield graph_res.model_dump_json()

            print("next----------",langgraph_flow.get_state(thread).next)
            if len(langgraph_flow.get_state(thread).next)>0:
                next_node=langgraph_flow.get_state(thread).next[0]
                for node in flow["nodes"]:
                    if node["type"] =="user_input_node" and node["id"]==next_node:
                        breakpoint={
                            "type":"breakpoint",
                            "thread_id":thread_id,
                            "breakpoint_node":node
                        }
                        res_content = json.dumps(breakpoint, ensure_ascii=False)
                        graph_res = OpenAIChatOutput(
                            id=f"chat{uuid.uuid4()}",
                            object="chat.completion.chunk",
                            content=res_content,
                            role="assistant",
                            tool_calls=[],
                            model=model,
                            status=AgentStatus.agent_finish,
                            message_type=MsgType.TEXT,
                        )
                        yield graph_res.model_dump_json()
                        break

            # langgraph_flow.update_state(thread, {"state": {"用户输入-1727772055377":{"user_input":"需要发送"}}},as_node="用户输入-1727772055377")
            # async for event in langgraph_flow.astream(None, thread,stream_mode="debug"):
            #     res_content = json.dumps(event, ensure_ascii=False)
            #     rich.print("执行结果："+res_content)
            #     graph_res = OpenAIChatOutput(
            #         id=f"chat{uuid.uuid4()}",
            #         object="chat.completion.chunk",
            #         content=res_content,
            #         role="assistant",
            #         tool_calls=[],
            #         model=model,
            #         status=AgentStatus.agent_finish,
            #         message_type=MsgType.TEXT,
            #         message_id=message_id,
            #     )
            #     yield graph_res.model_dump_json()



        except asyncio.exceptions.CancelledError:
            logger.warning("Streaming progress has been interrupted by user.")
            return
        except Exception as e:
            logger.error(f"Error in chatgraph: {e}")
            yield json.dumps({"error": str(e)})
            return


    if stream:
        return EventSourceResponse(flow_chat_iterator())
    else:
        ret = OpenAIChatOutput(
            id=f"chat{uuid.uuid4()}",
            object="chat.completion",
            content="",
            role="assistant",
            finish_reason="stop",
            tool_calls=[],
            model=model,
            status=AgentStatus.agent_finish,
            message_type=MsgType.TEXT,
            message_id=message_id,
        )

        async for chunk in flow_chat_iterator():
            ret.content +=chunk

        return ret.model_dump()
