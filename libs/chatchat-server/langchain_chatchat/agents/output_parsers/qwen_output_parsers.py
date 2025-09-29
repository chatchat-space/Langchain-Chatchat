from __future__ import annotations

import json
import logging
import re
from functools import partial
from operator import itemgetter
from typing import Any, List, Sequence, Tuple, Union

from langchain.agents.agent import AgentExecutor, RunnableAgent
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema import (
    AgentAction,
    AgentFinish,
)

from langchain_chatchat.utils.try_parse_json_object import try_parse_json_object


def validate_json(json_data: str):
    try:
        json.loads(json_data)
        return True
    except ValueError:
        return False


class QwenChatAgentOutputParserCustom(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent with custom qwen prompt."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if s := re.findall(
                r"\nAction:\s*(.+)\nAction\sInput:\s*(.+)", text, flags=re.DOTALL
        ):
            s = s[-1]
            json_string: str = s[1]

            _, json_input = try_parse_json_object(json_string)

            # TODO Annotate this code “有概率key为command而非query，需修改”
            # if "command" in json_input:
            #     json_input["query"] = json_input.pop("command")

            return AgentAction(tool=s[0].strip(), tool_input=json_input, log=text)
        elif s := re.findall(r"\nFinal\sAnswer:\s*(.+)", text, flags=re.DOTALL):
            s = s[-1]
            return AgentFinish({"output": s}, log=text)
        else:
            return AgentFinish({"output": text}, log=text)
            # raise OutputParserException(f"Could not parse LLM output: {text}")

    @property
    def _type(self) -> str:
        return "StructuredQWenChatOutputParserCustom"
