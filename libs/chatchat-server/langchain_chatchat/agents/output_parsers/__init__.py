# -*- coding: utf-8 -*-
"""Parsing utils to go from string to AgentAction or Agent Finish.

AgentAction means that an action should be taken.
This contains the name of the tool to use, the input to pass to that tool,
and a `log` variable (which contains a log of the agent's thinking).

AgentFinish means that a response should be given.
This contains a `return_values` dictionary. This usually contains a
single `output` key, but can be extended to contain more.
This also contains a `log` variable (which contains a log of the agent's thinking).
"""
from langchain_chatchat.agents.output_parsers.glm3_output_parsers import StructuredGLM3ChatOutputParser
from langchain_chatchat.agents.output_parsers.qwen_output_parsers import QwenChatAgentOutputParserCustom
from langchain_chatchat.agents.output_parsers.structured_chat_output_parsers import StructuredChatOutputParserLC
from langchain_chatchat.agents.output_parsers.platform_tools import (
    PlatformToolsAgentOutputParser,
)

from langchain_chatchat.agents.output_parsers.platform_knowledge_output_parsers import (
    PlatformKnowledgeOutputParserCustom, MCPToolAction
)
__all__ = [
    "MCPToolAction",
    "PlatformKnowledgeOutputParserCustom",
    "PlatformToolsAgentOutputParser",
    "QwenChatAgentOutputParserCustom",
    "StructuredGLM3ChatOutputParser",
    "StructuredChatOutputParserLC",
]
