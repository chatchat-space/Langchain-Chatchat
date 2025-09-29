from __future__ import annotations

import json
import re
from typing import Any, List, Sequence, Tuple, Union

from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.schema import (
    AgentAction,
    AgentFinish,
    AIMessage,
    HumanMessage,
    OutputParserException,
    SystemMessage,
)

from langchain_chatchat.utils.try_parse_json_object import try_parse_json_object


class StructuredChatOutputParserLC(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent with standard lc prompt."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if s := re.findall(r"\nAction:\s*```(.+)```", text, flags=re.DOTALL):
            _, parsed_json = try_parse_json_object(s[0])
            action = parsed_json
        else:
            raise OutputParserException(f"Could not parse LLM output: {text}")
        tool = action.get("action")
        if tool == "Final Answer":
            return AgentFinish({"output": action.get("action_input", "")}, log=text)
        else:
            return AgentAction(
                tool=tool, tool_input=action.get("action_input", {}), log=text
            )

    @property
    def _type(self) -> str:
        return "StructuredChatOutputParserLC"
