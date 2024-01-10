from __future__ import annotations

import json
import logging
from operator import itemgetter
import re
from typing import List, Sequence, Union

from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema import (AgentAction, AgentFinish, OutputParserException,
                              HumanMessage, SystemMessage, AIMessage)
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain.tools.render import format_tool_to_openai_function

from server.utils import get_prompt_template


logger = logging.getLogger(__name__)


class QwenChatAgentPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[BaseTool]

    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps", [])
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        if thoughts:
            kwargs["agent_scratchpad"] = f"These were previous tasks you completed:\n{thoughts}\n\n"
        else:
            kwargs["agent_scratchpad"] = ""
        # Create a tools variable from the list of tools provided
        # kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}. Parameters: {tool.args_schema.dict()}" for tool in self.tools])
        kwargs["tools"] = "\n".join([str(format_tool_to_openai_function(tool)) for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]


class QwenChatAgentOutputParserCustom(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent with custom qwen prompt."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if s := re.findall(r"\nAction:\s*(.+)\nAction\sInput:\s*(.+)", text, flags=re.DOTALL):
            s = s[-1]
            return AgentAction(tool=s[0].strip(), tool_input=json.loads(s[1]), log=text)
        elif s := re.findall(r"\nFinal\sAnswer:\s*(.+)", text, flags=re.DOTALL):
            s = s[-1]
            return AgentFinish({"output": s}, log=text)
        else:
            raise OutputParserException(f"Could not parse LLM output: {text}")

    @property
    def _type(self) -> str:
        return "StructuredQWenChatOutputParserCustom"


class QwenChatAgentOutputParserLC(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent with standard lc prompt."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if s := re.findall(r"\nAction:\s*```(.+)```", text, flags=re.DOTALL):
            action = json.loads(s[0])
            tool = action.get("action")
            if tool == "Final Answer":
                return AgentFinish({"output": action.get("action_input", "")}, log=text)
            else:
                return AgentAction(tool=tool, tool_input=action.get("action_input", {}), log=text)
        else:
            raise OutputParserException(f"Could not parse LLM output: {text}")

    @property
    def _type(self) -> str:
        return "StructuredQWenChatOutputParserLC"


def create_structured_qwen_chat_agent(
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        use_custom_prompt: bool = True,
) -> Runnable:
    if use_custom_prompt:
        prompt = "qwen"
        output_parser = QwenChatAgentOutputParserCustom()
    else:
        prompt = "structured-chat-agent"
        output_parser = QwenChatAgentOutputParserLC()

    template = get_prompt_template("action_model", prompt)
    prompt = QwenChatAgentPromptTemplate(input_variables=["input", "intermediate_steps"],
                                        template=template,
                                        tools=tools)

    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=itemgetter("intermediate_steps")
        )
        | prompt
        | llm.bind(stop="\nObservation:")
        | output_parser
    )
    return agent
