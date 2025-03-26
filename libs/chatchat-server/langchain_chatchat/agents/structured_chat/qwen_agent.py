import json
import logging
import re
from typing import Optional, Sequence, Union, List, Dict, Any

from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import ToolsRenderer

from chatchat.utils import build_logger
from langchain_chatchat.agents.format_scratchpad.all_tools import format_to_platform_tool_messages
from langchain_chatchat.agents.output_parsers import QwenChatAgentOutputParserCustom, PlatformToolsAgentOutputParser

logger = build_logger()


def render_qwen_json(tools: List[BaseTool]) -> str:
    # Create a tools variable from the list of tools provided

    tools_json = []
    for t in tools:
        desc = re.sub(r"\n+", " ", t.description)
        text = (
            f"{t.name}: Call this tool to interact with the {t.name} API. What is the {t.name} API useful for?"
            f" {desc}"
            f" Parameters: {t.args}"
        )
        tools_json.append(text)
    return "\n".join(tools_json)


def create_qwen_chat_agent(
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        prompt: ChatPromptTemplate,
        tools_renderer: ToolsRenderer = render_qwen_json,
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
    missing_vars = {"tools", "tool_names", "agent_scratchpad"}.difference(
        prompt.input_variables + list(prompt.partial_variables)
    )
    if missing_vars:
        raise ValueError(f"Prompt missing required variables: {missing_vars}")

    prompt = prompt.partial(
        tools=tools_renderer(list(tools)),
        tool_names=", ".join([t.name for t in tools]),
    )
    if stop_sequence:
        stop = ["<|endoftext|>", "<|im_start|>", "<|im_end|>", "\nObservation:"] if stop_sequence is True else stop_sequence
        llm_with_stop = llm.bind(stop=stop)
    else:
        llm_with_stop = llm

    agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_platform_tool_messages(x["intermediate_steps"]),
            )
            | prompt
            | llm_with_stop
            | PlatformToolsAgentOutputParser(instance_type="qwen")
    )
    return agent
