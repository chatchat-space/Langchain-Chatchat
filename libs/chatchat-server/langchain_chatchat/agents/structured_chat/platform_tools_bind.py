# -*- coding: utf-8 -*-
from typing import Sequence, Union, List, Dict, Any

from langchain.agents.agent import NextStepOutput
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import BaseTool, ToolsRenderer, render_text_description
from langchain_core.agents import AgentAction, AgentFinish

from langchain_chatchat.agents.format_scratchpad.all_tools import (
    format_to_platform_tool_messages,
)
from langchain_chatchat.agents.output_parsers import PlatformToolsAgentOutputParser


def create_platform_tools_agent(
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        prompt: ChatPromptTemplate,
        tools_renderer: ToolsRenderer = render_text_description,
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
    missing_vars = {"agent_scratchpad"}.difference(
        prompt.input_variables + list(prompt.partial_variables)
    )
    if missing_vars:
        raise ValueError(f"Prompt missing required variables: {missing_vars}")

    prompt = prompt.partial(
        tools=tools_renderer(list(tools)),
        tool_names=", ".join([t.name for t in tools]),
    )

    if stop_sequence and len(llm_with_platform_tools) == 0:
        stop = ["\nObservation:"] if stop_sequence is True else stop_sequence
        llm_with_stop = llm.bind(stop=stop)
    elif stop_sequence is False and len(llm_with_platform_tools) > 0:
        llm_with_stop = llm.bind(tools=llm_with_platform_tools)
    elif stop_sequence and len(llm_with_platform_tools) > 0:

        stop = ["\nObservation:"] if stop_sequence is True else stop_sequence
        llm_with_stop = llm.bind(
            stop=stop,
            tools=llm_with_platform_tools
        )
    else:
        llm_with_stop = llm

    def human_approval(values: NextStepOutput) -> NextStepOutput:
        if isinstance(values, AgentFinish):
            values = [values]
        else:
            values = values
        if isinstance(values[-1], AgentFinish):
            assert len(values) == 1
            return values[-1]
        tool_strs = "\n\n".join(
            tool_call.tool for tool_call in values
        )
        input_msg = (
            f"Do you approve of the following tool invocations\n\n{tool_strs}\n\n"
            "Anything except 'Y'/'Yes' (case-insensitive) will be treated as a no."
        )
        resp = input(input_msg)
        if resp.lower() not in ("yes", "y"):
            return [AgentAction(tool="approved", tool_input=resp, log= f"Tool invocations not approved:\n\n{tool_strs}")]
        return values

    agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_platform_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm_with_stop
            | PlatformToolsAgentOutputParser(instance_type="platform-agent")
            # | human_approval
    )

    return agent
