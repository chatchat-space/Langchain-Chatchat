# -*- coding: utf-8 -*-
import json
from typing import List, Sequence, Tuple, Union

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.agents import AgentAction
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    BaseMessage,
    ToolMessage,
)
from langchain_chatchat.agent_toolkits import BaseToolOutput
from langchain_chatchat.agent_toolkits.all_tools.code_interpreter_tool import (
    CodeInterpreterToolOutput,
)
from langchain_chatchat.agent_toolkits.all_tools.drawing_tool import DrawingToolOutput
from langchain_chatchat.agent_toolkits.all_tools.web_browser_tool import (
    WebBrowserToolOutput,
)
from langchain_chatchat.agents.output_parsers.tools_output.code_interpreter import (
    CodeInterpreterAgentAction,
)
from langchain_chatchat.agents.output_parsers.tools_output.drawing_tool import DrawingToolAgentAction
from langchain_chatchat.agents.output_parsers.tools_output.web_browser import WebBrowserAgentAction


def _create_tool_message(
    agent_action: Union[ToolAgentAction, AgentAction], observation: Union[str, BaseToolOutput]
) -> ToolMessage:
    """Convert agent action and observation into a function message.
    Args:
        agent_action: the tool invocation request from the agent
        observation: the result of the tool invocation
    Returns:
        FunctionMessage that corresponds to the original tool invocation
    """
    if not isinstance(observation, str):
        try:
            content = json.dumps(observation, ensure_ascii=False)
        except Exception:
            content = str(observation)
    else:
        content = observation

    tool_call_id = "abc"
    if isinstance(agent_action, ToolAgentAction):
        tool_call_id = agent_action.tool_call_id

    return ToolMessage(
        tool_call_id=tool_call_id,
        content=content,
        additional_kwargs={"name": agent_action.tool},
    )

def format_to_platform_tool_messages(
    intermediate_steps: Sequence[Tuple[AgentAction, BaseToolOutput]],
) -> List[BaseMessage]:
    """Convert (AgentAction, tool output) tuples into FunctionMessages.

    Args:
        intermediate_steps: Steps the LLM has taken to date, along with observations

    Returns:
        list of messages to send to the LLM for the next prediction
    """
    messages = []

    for idx, (agent_action, observation) in enumerate(intermediate_steps):
        # === CodeInterpreter ===
        if isinstance(agent_action, CodeInterpreterAgentAction):
            if isinstance(observation, CodeInterpreterToolOutput):
                sandbox_type = observation.platform_params.get("sandbox", "auto")
                if sandbox_type == "auto":
                    new_messages = [
                        AIMessage(content=str(observation.code_input)),
                        _create_tool_message(agent_action, observation),
                    ]
                elif sandbox_type == "none":
                    new_messages = [
                        AIMessage(content=str(observation.code_input)),
                        _create_tool_message(agent_action, observation.code_output),
                    ]
                else:
                    raise ValueError(f"Unknown sandbox type: {sandbox_type}")
                messages.extend([m for m in new_messages if m not in messages])
            else:
                raise ValueError(f"Unknown observation type: {type(observation)}")

        # === DrawingTool ===
        elif isinstance(agent_action, DrawingToolAgentAction):
            if isinstance(observation, DrawingToolOutput):
                messages.append(AIMessage(content=str(observation)))
            else:
                raise ValueError(f"Unknown observation type: {type(observation)}")

        # === WebBrowser ===
        elif isinstance(agent_action, WebBrowserAgentAction):
            if isinstance(observation, WebBrowserToolOutput):
                messages.append(AIMessage(content=str(observation)))
            else:
                raise ValueError(f"Unknown observation type: {type(observation)}")

        # === ToolAgentAction ===
        elif isinstance(agent_action, ToolAgentAction):
            ai_msgs = AIMessage(
                content=f"arguments='{agent_action.tool_input}', name='{agent_action.tool}'",
                additional_kwargs={
                    "tool_calls": [
                        {
                            "index": idx,
                            "id": agent_action.tool_call_id,
                            "type": "function",
                            "function": {
                                "name": agent_action.tool,
                                "arguments": json.dumps(agent_action.tool_input, ensure_ascii=False),
                            },
                        }
                    ]
                },
            )
            messages.extend([ai_msgs, _create_tool_message(agent_action, observation)])

        # === Generic AgentAction ===
        elif isinstance(agent_action, AgentAction):
            # 这里假设 observation 是本项目自定义prompt tools，而不是 模型测tools
            ai_msgs = AIMessage(
                content=f"{agent_action.log}"
            )
            messages.extend([ai_msgs, HumanMessage(content=str(observation))])

        # === Fallback ===
        else:
            messages.append(AIMessage(content=getattr(agent_action, "log", str(agent_action))))

    return messages
