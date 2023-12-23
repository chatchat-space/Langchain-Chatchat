from __future__ import annotations

from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.memory import ConversationBufferWindowMemory
from typing import Any, List, Sequence, Tuple, Optional, Union
import re
from langchain.agents import Tool
from langchain.agents.agent import LLMSingleActionAgent, AgentOutputParser
from langchain.chains.llm import LLMChain
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, BaseChatPromptTemplate
import json
import logging
from langchain.pydantic_v1 import Field
from langchain.schema import (AgentAction, AgentFinish, OutputParserException,
                              HumanMessage, SystemMessage, AIMessage)
from langchain.agents.agent import AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain.tools.render import format_tool_to_openai_function
from server.utils import get_prompt_template

HUMAN_MESSAGE_TEMPLATE = "{input}\n\n{agent_scratchpad}"
logger = logging.getLogger(__name__)


class QwenChatAgentPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

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


class QwenChatAgentOutputParser(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent."""

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
        return "structured_chat_qwen_with_retries"


class QwenChatAgent(LLMSingleActionAgent):
    """Structured Chat Agent."""

    output_parser: AgentOutputParser = Field(
        default_factory=QwenChatAgentOutputParser
    )
    """Output parser for the agent."""

    @property
    def observation_prefix(self) -> str:
        """Prefix to append the qwen observation with."""
        return "\nObservation:"

    @property
    def llm_prefix(self) -> str:
        """Prefix to append the llm call with."""
        return "\nThought:"

    @classmethod
    def _validate_tools(cls, tools: Sequence[BaseTool]) -> None:
        pass

    @classmethod
    def create_prompt(
            cls,
            tools: Sequence[BaseTool],
            prompt: str = None,
            input_variables: Optional[List[str]] = None,
            memory_prompts: Optional[List[QwenChatAgentPromptTemplate]] = None,
    ) -> QwenChatAgentPromptTemplate:
        template = get_prompt_template("action_model", "qwen")
        return QwenChatAgentPromptTemplate(input_variables=["input", "intermediate_steps"],
                                           template=template,
                                           tools=tools)

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool],
        prompt: str = None,
        callbacks: List[BaseCallbackHandler] = [],
        output_parser: Optional[AgentOutputParser] = None,
        human_message_template: str = HUMAN_MESSAGE_TEMPLATE,
        input_variables: Optional[List[str]] = None,
        memory_prompts: Optional[List[BaseChatPromptTemplate]] = None,
        **kwargs: Any,
    ) -> QwenChatAgent:
        """Construct an agent from an LLM and tools."""
        cls._validate_tools(tools)
        prompt = cls.create_prompt(
            tools,
            prompt=prompt,
            input_variables=input_variables,
            memory_prompts=memory_prompts,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callbacks=callbacks,
        )
        tool_names = [tool.name for tool in tools]
        output_parser = output_parser or QwenChatAgentOutputParser()
        return cls(
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            output_parser=output_parser,
            stop=["\nObservation:"],
            **kwargs,
        )

    @property
    def _agent_type(self) -> str:
        return "qwen_chat_agent"


def initialize_qwen_agent(
    tools: Sequence[BaseTool],
    llm: BaseLanguageModel,
    prompt: str = None,
    callbacks: List[BaseCallbackHandler] = [],
    memory: Optional[ConversationBufferWindowMemory] = None,
    agent_kwargs: Optional[dict] = None,
    *,
    tags: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> AgentExecutor:
    tags_ = list(tags) if tags else []
    agent_kwargs = agent_kwargs or {}
    llm.callbacks=callbacks
    agent_obj = QwenChatAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        prompt=prompt,
        **agent_kwargs,
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent_obj,
        tools=tools,
        callbacks=callbacks,
        memory=memory,
        tags=tags_,
        intermediate_steps=[],
        **kwargs,
    )
