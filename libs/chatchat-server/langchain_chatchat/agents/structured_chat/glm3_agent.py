"""
This file is a modified version for ChatGLM3-6B the original glm3_agent.py file from the langchain repo.
"""

import json
import logging
from typing import Optional, Sequence, Union, List, Dict, Any

from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import ToolsRenderer

from chatchat.server.pydantic_v1 import Field, model_schema, typing
from chatchat.utils import build_logger
from langchain_chatchat.agents.format_scratchpad.all_tools import format_to_platform_tool_messages
from langchain_chatchat.agents.output_parsers import StructuredGLM3ChatOutputParser, PlatformToolsAgentOutputParser

logger = build_logger()


def render_glm3_json(tools: List[BaseTool]) -> str:
    tools_json = []
    for tool in tools:
        tool_schema = model_schema(tool.args_schema) if tool.args_schema else {}
        description = (
            tool.description.split(" - ")[1].strip()
            if tool.description and " - " in tool.description
            else tool.description
        )
        parameters = {
            k: {sub_k: sub_v for sub_k, sub_v in v.items() if sub_k != "title"}
            for k, v in tool_schema.get("properties", {}).items()
        }
        simplified_config_langchain = {
            "name": tool.name,
            "description": description,
            "parameters": parameters,
        }
        tools_json.append(simplified_config_langchain)
    return "\n".join(
        [json.dumps(tool, indent=4, ensure_ascii=False) for tool in tools_json]
    )


def create_structured_glm3_chat_agent(
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        prompt: ChatPromptTemplate,
        tools_renderer: ToolsRenderer = render_glm3_json,
        *,
        stop_sequence: Union[bool, List[str]] = True,
        llm_with_platform_tools: List[Dict[str, Any]] = [],
) -> Runnable:
    """Create an agent that uses tools.

    Args:

        llm: LLM to use as the agent.
        tools: Tools this agent has access to.
        prompt: The prompt to use, must have input keys
            `tools`: contains descriptions for each tool.
            `agent_scratchpad`: contains previous agent actions and tool outputs.
        tools_renderer: This controls how the tools are converted into a string and
            then passed into the LLM. Default is `render_text_description`.
        stop_sequence: bool or list of str.
            If True, adds a stop token of "</tool_input>" to avoid hallucinates.
            If False, does not add a stop token.
            If a list of str, uses the provided list as the stop tokens.

            Default is True. You may to set this to False if the LLM you are using
            does not support stop sequences.
        llm_with_platform_tools: length ge 0 of dict tools for platform

    Returns:
        A Runnable sequence representing an agent. It takes as input all the same input
        variables as the prompt passed in does. It returns as output either an
        AgentAction or AgentFinish.

    """
    missing_vars = {"tools", "agent_scratchpad"}.difference(
        prompt.input_variables + list(prompt.partial_variables)
    )
    if missing_vars:
        raise ValueError(f"Prompt missing required variables: {missing_vars}")

    prompt = prompt.partial(
        tools=tools_renderer(list(tools)),
        tool_names=", ".join([t.name for t in tools]),
    )
    if stop_sequence:
        stop = ["<|observation|>"] if stop_sequence is True else stop_sequence
        llm_with_stop = llm.bind(stop=stop)
    else:
        llm_with_stop = llm

    agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_platform_tool_messages(x["intermediate_steps"]),
            )
            | prompt
            | llm_with_stop
            | PlatformToolsAgentOutputParser(instance_type="glm3")
    )
    return agent
