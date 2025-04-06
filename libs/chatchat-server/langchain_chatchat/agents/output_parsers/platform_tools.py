# -*- coding: utf-8 -*-
from typing import List, Union

from langchain.agents.agent import MultiActionAgentOutputParser, AgentOutputParser
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGeneration, Generation

from chatchat.server.pydantic_v1 import Field, model_schema, typing
from typing_extensions import Literal

from langchain_chatchat.agents.output_parsers import StructuredGLM3ChatOutputParser, QwenChatAgentOutputParserCustom
from langchain_chatchat.agents.output_parsers.platform_knowledge_output_parsers import \
    PlatformKnowledgeOutputParserCustom
from langchain_chatchat.agents.output_parsers.structured_chat_output_parsers import StructuredChatOutputParserLC
from langchain_chatchat.agents.output_parsers.tools_output.code_interpreter import (
    CodeInterpreterAgentAction,
)
from langchain_chatchat.agents.output_parsers.tools_output.drawing_tool import DrawingToolAgentAction
from langchain_chatchat.agents.output_parsers.tools_output.tools import (
    parse_ai_message_to_tool_action,
)
from langchain_chatchat.agents.output_parsers.tools_output.web_browser import WebBrowserAgentAction

ZhipuAiALLToolAgentAction = ToolAgentAction


def parse_ai_message_to_platform_tool_action(
        message: BaseMessage,
) -> Union[List[AgentAction], AgentFinish]:
    """Parse an AI message potentially containing tool_calls."""
    tool_actions = parse_ai_message_to_tool_action(message)
    if isinstance(tool_actions, AgentFinish):
        return tool_actions
    final_actions: List[AgentAction] = []
    for action in tool_actions:
        if isinstance(action, CodeInterpreterAgentAction):
            final_actions.append(action)
        elif isinstance(action, DrawingToolAgentAction):
            final_actions.append(action)
        elif isinstance(action, WebBrowserAgentAction):
            final_actions.append(action)
        elif isinstance(action, ToolAgentAction):
            final_actions.append(
                ZhipuAiALLToolAgentAction(
                    tool=action.tool,
                    tool_input=action.tool_input,
                    log=action.log,
                    message_log=action.message_log,
                    tool_call_id=action.tool_call_id,
                )
            )
        else:
            final_actions.append(action)
    return final_actions


class PlatformToolsAgentOutputParser(MultiActionAgentOutputParser):
    """Parses a message into agent actions/finish.

    Is meant to be used with models, as it relies on the specific
    tool_calls parameter from Platform to convey what tools to use.

    If a tool_calls parameter is passed, then that is used to get
    the tool names and tool inputs.

    If one is not passed, then the AIMessage is assumed to be the final output.
    """
    instance_type: Literal["GPT-4", "glm3", "qwen", "platform-agent", "platform-knowledge-mode", "base"] = "platform-agent"
    """
    instance type of the agent， parser platform return chunk to agent action
    """

    gpt_base_parser: AgentOutputParser = Field(default_factory=StructuredChatOutputParser)
    glm3_base_parser: AgentOutputParser = Field(default_factory=StructuredGLM3ChatOutputParser)
    qwen_base_parser: AgentOutputParser = Field(default_factory=QwenChatAgentOutputParserCustom)
    knowledge_parser: AgentOutputParser = Field(default_factory=PlatformKnowledgeOutputParserCustom)
    base_parser: AgentOutputParser = Field(default_factory=StructuredChatOutputParserLC)

    @property
    def _type(self) -> str:
        return "platform-tools-agent-output-parser"

    def parse_result(
            self, result: List[Generation], *, partial: bool = False
    ) -> Union[List[AgentAction], AgentFinish]:
        if not isinstance(result[0], ChatGeneration):
            raise ValueError("This output parser only works on ChatGeneration output")

        if self.instance_type == "GPT-4":
            return self.gpt_base_parser.parse(result[0].text)
        elif self.instance_type == "glm3":
            return self.glm3_base_parser.parse(result[0].text)
        elif self.instance_type == "qwen":
            return self.qwen_base_parser.parse(result[0].text)
        elif self.instance_type == "platform-agent":
            message = result[0].message
            return parse_ai_message_to_platform_tool_action(message)
        elif self.instance_type == "platform-knowledge-mode":
            return self.knowledge_parser.parse_result(result, partial=partial)
        else:
            return self.base_parser.parse(result[0].text)

    def parse(self, text: str) -> Union[List[AgentAction], AgentFinish]:
        raise ValueError("Can only parse messages")
