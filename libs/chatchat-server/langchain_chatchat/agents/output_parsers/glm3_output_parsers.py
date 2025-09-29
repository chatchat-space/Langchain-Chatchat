"""
This file is a modified version for ChatGLM3-6B the original glm3_agent.py file from the langchain repo.
"""

import json
import logging
from typing import Optional, Sequence, Union
import re
import langchain_core.messages
import langchain_core.prompts
from langchain.agents.agent import AgentOutputParser
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException

from chatchat.server.pydantic_v1 import Field, model_schema, typing
from langchain_chatchat.utils.try_parse_json_object import try_parse_json_object


class StructuredGLM3ChatOutputParser(AgentOutputParser):
    """
    Output parser with retries for the structured chat agent.
    """

    base_parser: AgentOutputParser = Field(default_factory=StructuredChatOutputParser)

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        exec_code = None
        if s := re.search(r'(\S+\s+```python\s+tool_call\(.*?\)\s+```)', text, re.DOTALL):
            exec_code = s[0]

        if exec_code:
            action = str(exec_code.split("```python")[0]).replace("\n", "").strip()

            code_str = str("```" + exec_code.split("```python")[1]).strip()

            _, params = try_parse_json_object(code_str)

            action_json = {"action": action, "action_input": params}
        else:
            action_json = {"action": "Final Answer", "action_input": text}

        action_str = f"""
Action:
```
{json.dumps(action_json, ensure_ascii=False)}
```"""
        try:
            parsed_obj = self.base_parser.parse(action_str)
            return parsed_obj
        except Exception as e:
            raise OutputParserException(f"Could not parse LLM output: {text}") from e

    @property
    def _type(self) -> str:
        return "StructuredGLM3ChatOutputParser"
