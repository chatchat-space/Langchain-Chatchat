# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Sequence, Union, List, Dict, Any

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import BaseTool, ToolsRenderer, render_text_description
from langchain_core.agents import AgentAction, AgentFinish

from langchain_chatchat.agent_toolkits.mcp_kit.tools import MCPStructuredTool
from langchain_chatchat.agents.format_scratchpad.all_tools import (
    format_to_platform_tool_messages,
)
from langchain_chatchat.agents.output_parsers import PlatformToolsAgentOutputParser
import re
from collections import defaultdict


def render_knowledge_mcp_tools(tools: List[MCPStructuredTool]) -> str:
    # 使用 defaultdict 将 tools 按 server_name 分组
    grouped_tools = defaultdict(list)

    for t in tools:
        desc = re.sub(r"\n+", " ", t.description)
        
        # 构建参数描述，强调 required=True 属性
        params = []
        if hasattr(t, "args") and t.args:
            for arg_name, arg_def in t.args.items():
                # 获取字段信息
                required = arg_def.get("required", True)
                required_str = "(required)" if required else "(optional)"
                arg_desc = arg_def.get("description", "").strip() 
                # 强调 required 属性
                if required:
                    params.append(f"- {arg_name}: {required_str} CRITICAL: Must provide actual content, empty/null forbidden. {arg_desc}")
                else:
                    params.append(f"- {arg_name}: {required_str} {arg_desc}")
        
        # 拼接工具描述
        params_text = "\n".join(params) if params else "- None"
        text = (
            f"- {t.name}: {desc}  \n"
            f"  Input Schema:\n"
            f"  {params_text}"
        )
        grouped_tools[t.server_name].append(text)

    # 构建最终输出字符串
    output = []
    for server_name, tool_texts in grouped_tools.items():
        section = f"## {server_name}\n### Available Tools\n" + "\n".join(tool_texts)
        output.append(section)

    return "\n\n".join(output)


def render_knowledge_tools(tools: List[BaseTool]) -> str:
 
    output = []
    for t in tools:
        # 处理描述，去掉多余换行
        desc = re.sub(r"\n+", " ", t.description)

        # 构建参数部分
        params = []
        if hasattr(t, "args") and t.args:  # 确保有参数定义
            for arg_name, arg_def in t.args.items():
                # 获取字段信息
                required = arg_def.get("required", True)
                required_str = "(required)" if required else "(optional)"
                arg_desc = arg_def.get("description", "").strip() 
                # 强调 required 属性
                if required:
                    params.append(f"- {arg_name}: {required_str} CRITICAL: Must provide actual content, empty/null forbidden. {arg_desc}")
                else:
                    params.append(f"- {arg_name}: {required_str} {arg_desc}")

        # 拼接最终文本
        text = (
            f"## {t.name}\n"
            f"Description: {desc}\n"
            f"Parameters:\n" +
            ("\n".join(params) if params else "- None")
        )
        output.append(text)

    return "\n\n".join(output)

def create_platform_knowledge_agent(
        llm: BaseLanguageModel,
        current_working_directory: str,
        tools: Sequence[BaseTool],
        mcp_tools: Sequence[MCPStructuredTool],
        prompt: ChatPromptTemplate,
        *,
        llm_with_platform_tools: List[Dict[str, Any]] = [],
) -> Runnable:
    """Create an agent that uses tools.

    Returns:
        A Runnable sequence representing an agent. It takes as input all the same input
        variables as the prompt passed in does. It returns as output either an
        AgentAction or AgentFinish.


    """
    missing_vars = {"agent_scratchpad"}.difference(
        prompt.input_variables + list(prompt.partial_variables)
    )
    if missing_vars:
        raise ValueError(f"Prompt missing required variables: {missing_vars}")

    prompt = prompt.partial(
        current_working_directory=current_working_directory,
        tools=render_knowledge_tools(list(tools)),
        datetime=datetime.now().isoformat(),
        mcp_tools=render_knowledge_mcp_tools(list(mcp_tools)),
    ) 
    
    agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_platform_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm
            | PlatformToolsAgentOutputParser(instance_type="platform-knowledge-mode")

    )

    return agent
