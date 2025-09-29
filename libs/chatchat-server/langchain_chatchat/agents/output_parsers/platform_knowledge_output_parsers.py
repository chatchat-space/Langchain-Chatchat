from __future__ import annotations

import json
import logging
import re
from functools import partial
from operator import itemgetter
from typing import Any, List, Sequence, Tuple, Union

from langchain.agents.agent import AgentExecutor, RunnableAgent
from langchain.agents.output_parsers import ToolsAgentOutputParser
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema import (
    AgentAction,
    AgentFinish
)
from langchain_chatchat.utils.try_parse_json_object import try_parse_json_object

logger = logging.getLogger()
import xml.etree.ElementTree as ET

from langchain_core.outputs import Generation

class MCPToolAction(AgentAction):
    server_name: str  

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether or not the class is serializable."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain_chatchat", "agents", "output_parsers", "platform_knowledge_output_parsers"]
        
def collect_plain_text(root):
    texts = []
    if root.text and root.text.strip():
        texts.append(root.text.strip())
    for elem in root.iter():
        if elem.tail and elem.tail.strip():
            texts.append(elem.tail.strip())
    return "".join(texts)

class PlatformKnowledgeOutputParserCustom(ToolsAgentOutputParser):
    """Output parser with retries for the structured chat agent with custom Knowledge prompt."""

    def parse_result(
            self, result: List[Generation], *, partial: bool = False
    ) -> Union[List[Union[AgentAction, MCPToolAction]], AgentFinish]:

        """Parse a list of candidate model Generations into a specific format."""
        tools = super().parse_result(result, partial=partial)
        message = result[0].message
        temp_tools = []
        try:
            cleaned_content = str(message.content).replace("</think>", "")

            wrapped_xml = f"<root>{cleaned_content}</root>"
            # 解析mcp_use标签
            root = ET.fromstring(wrapped_xml)
            
            log_text = collect_plain_text(root)
            # 遍历所有顶层标签
            for elem in root:  
                if elem.tag == 'use_mcp_tool':
                    # 处理use_mcp_tool标签
                    server_name = elem.find("server_name").text.strip()
                    tool_name = elem.find("tool_name").text.strip()

                    # 提取并解析 arguments 中的 JSON 字符串
                    arguments_raw = elem.find("arguments").text.strip()

                    _, json_input = try_parse_json_object(arguments_raw)
                    act = MCPToolAction(
                        server_name=server_name,
                        tool=tool_name,
                        tool_input=json_input,
                        log=str(log_text)
                    )
                    temp_tools.append(act)
                elif elem.tag == 'thinking':
                    # 忽略thinking标签，这是用于内部思考过程的标签
                    continue
                elif elem.tag in ['use_mcp_resource']:
                    # 处理use_mcp_resource标签，暂时跳过
                    continue
                else:
                    # 处理其他工具标签（如calculate等）
                    tool_name = elem.tag
                    tool_input = {}
                    
                    # 遍历标签内的所有子标签，作为工具参数
                    for child in elem:
                        if child.text and child.text.strip():
                            tool_input[child.tag] = child.text.strip()
                    
                    # 创建通用的AgentAction
                    act = AgentAction(
                        tool=tool_name,
                        tool_input=tool_input,
                        log=str(log_text)
                    )
                    temp_tools.append(act)

            if isinstance(tools, AgentFinish) and len(temp_tools) == 0:
                return tools 

            elif not isinstance(tools, AgentFinish):
                temp_tools.extend(tools)
        except Exception as e:
            logger.error(e)
            return AgentFinish(return_values={"output": str(message.content)}, log=str(message.content))
        return temp_tools

    @property
    def _type(self) -> str:
        return "PlatformKnowledgeOutputParserCustom"
