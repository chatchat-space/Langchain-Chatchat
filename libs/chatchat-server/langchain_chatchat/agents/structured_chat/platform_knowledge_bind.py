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
        text = (
            f"- {t.name}: {desc}  \n"
            f"  Input Schema: {t.args}"
        )
        grouped_tools[t.server_name].append(text)

    # 构建最终输出字符串
    output = []
    for server_name, tool_texts in grouped_tools.items():
        section = f"## {server_name}\n### Available Tools\n" + "\n".join(tool_texts)
        output.append(section)

    return "\n\n".join(output)


def create_platform_knowledge_agent(
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        mcp_tools: Sequence[MCPStructuredTool],
        prompt: ChatPromptTemplate,
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
        datetime=datetime.now().isoformat(),
        mcp_tools=render_knowledge_mcp_tools(list(mcp_tools)),
    )
    llm_with_stop = llm.bind(
        tools=tools
    )
    agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_platform_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm_with_stop
            | PlatformToolsAgentOutputParser(instance_type="platform-knowledge-mode")

    )

    return agent
