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

import xml.etree.ElementTree as ET


class PlatformKnowledgeOutputParserCustom(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent with custom Knowledge prompt."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:

        try:
            wrapped_xml = f"<root>{text}</root>"
            # 解析mcp_use标签
            root = ET.fromstring(wrapped_xml)

            # 遍历所有顶层标签
            for elem in root:
                if elem.tag == 'use_mcp_tool':
                    # 处理use_mcp_tool标签
                    server_name = elem.find("server_name").text.strip()
                    tool_name = elem.find("tool_name").text.strip()

                    # 提取并解析 arguments 中的 JSON 字符串
                    arguments_raw = elem.find("arguments").text.strip()

                    return AgentAction(
                        f"{server_name}: {tool_name}",
                        arguments_raw,
                        log=text,
                    )
        except Exception as e:
            return AgentFinish(return_values={"output": text}, log=text)

    @property
    def _type(self) -> str:
        return "PlatformKnowledgeOutputParserCustom"
