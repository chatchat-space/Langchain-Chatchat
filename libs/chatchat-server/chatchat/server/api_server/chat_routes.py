from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Request
from langchain.prompts.prompt import PromptTemplate

from chatchat.server.api_server.api_schemas import AgentStatus, MsgType, OpenAIChatInput
from chatchat.server.chat.chat import chat
from chatchat.server.chat.feedback import chat_feedback
from chatchat.server.chat.file_chat import file_chat
from chatchat.server.db.repository import add_message_to_db
from chatchat.server.utils import (
    get_OpenAIClient,
    get_prompt_template,
    get_tool,
    get_tool_config,
)

from .openai_routes import openai_request

chat_router = APIRouter(prefix="/chat", tags=["ChatChat 对话"])

chat_router.post(
    "/chat",
    summary="与llm模型对话(通过LLMChain)",
)(chat)

chat_router.post(
    "/feedback",
    summary="返回llm模型对话评分",
)(chat_feedback)

chat_router.post("/file_chat", summary="文件对话")(file_chat)

# 定义全局model信息，用于给Text2Sql中的get_ChatOpenAI提供model_name
global_model_name = None


@chat_router.post("/chat/completions", summary="兼容 openai 的统一 chat 接口")
async def chat_completions(
    request: Request,
    body: OpenAIChatInput,
) -> Dict:
    """
    请求参数与 openai.chat.completions.create 一致，可以通过 extra_body 传入额外参数
    tools 和 tool_choice 可以直接传工具名称，会根据项目里包含的 tools 进行转换
    通过不同的参数组合调用不同的 chat 功能：
    - tool_choice
        - extra_body 中包含 tool_input: 直接调用 tool_choice(tool_input)
        - extra_body 中不包含 tool_input: 通过 agent 调用 tool_choice
    - tools: agent 对话
    - 其它：LLM 对话
    以后还要考虑其它的组合（如文件对话）
    返回与 openai 兼容的 Dict
    """
    client = get_OpenAIClient(model_name=body.model, is_async=True)
    extra = {**body.model_extra} or {}
    for key in list(extra):
        delattr(body, key)

    global global_model_name
    global_model_name = body.model
    # check tools & tool_choice in request body
    if isinstance(body.tool_choice, str):
        if t := get_tool(body.tool_choice):
            body.tool_choice = {"function": {"name": t.name}, "type": "function"}
    if isinstance(body.tools, list):
        for i in range(len(body.tools)):
            if isinstance(body.tools[i], str):
                if t := get_tool(body.tools[i]):
                    body.tools[i] = {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.args,
                        },
                    }

    conversation_id = extra.get("conversation_id")

    # chat based on result from one choiced tool
    if body.tool_choice:
        tool = get_tool(body.tool_choice["function"]["name"])
        if not body.tools:
            body.tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.args,
                    },
                }
            ]
        if tool_input := extra.get("tool_input"):
            message_id = (
                add_message_to_db(
                    chat_type="tool_call",
                    query=body.messages[-1]["content"],
                    conversation_id=conversation_id,
                )
                if conversation_id
                else None
            )

            tool_result = await tool.ainvoke(tool_input)
            prompt_template = PromptTemplate.from_template(
                get_prompt_template("llm_model", "rag"), template_format="jinja2"
            )
            body.messages[-1]["content"] = prompt_template.format(
                context=tool_result, question=body.messages[-1]["content"]
            )
            del body.tools
            del body.tool_choice
            extra_json = {
                "message_id": message_id,
                "status": None,
            }
            header = [
                {
                    **extra_json,
                    "content": f"{tool_result}",
                    "tool_output": tool_result.data,
                    "is_ref": True,
                }
            ]
            return await openai_request(
                client.chat.completions.create,
                body,
                extra_json=extra_json,
                header=header,
            )

    # agent chat with tool calls
    if body.tools:
        message_id = (
            add_message_to_db(
                chat_type="agent_chat",
                query=body.messages[-1]["content"],
                conversation_id=conversation_id,
            )
            if conversation_id
            else None
        )

        chat_model_config = {}  # TODO: 前端支持配置模型
        tool_names = [x["function"]["name"] for x in body.tools]
        tool_config = {name: get_tool_config(name) for name in tool_names}
        result = await chat(
            query=body.messages[-1]["content"],
            metadata=extra.get("metadata", {}),
            conversation_id=extra.get("conversation_id", ""),
            message_id=message_id,
            history_len=-1,
            history=body.messages[:-1],
            stream=body.stream,
            chat_model_config=extra.get("chat_model_config", chat_model_config),
            tool_config=extra.get("tool_config", tool_config),
        )
        return result
    else:  # LLM chat directly
        message_id = (
            add_message_to_db(
                chat_type="llm_chat",
                query=body.messages[-1]["content"],
                conversation_id=conversation_id,
            )
            if conversation_id
            else None
        )
        extra_json = {
            "message_id": message_id,
            "status": None,
        }
        return await openai_request(
            client.chat.completions.create, body, extra_json=extra_json
        )
