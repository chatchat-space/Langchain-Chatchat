"""
This file is a modified version for ChatGLM3-6B the original glm3_agent.py file from the langchain repo.
"""
from __future__ import annotations

import json
import logging
from typing import Any, List, Sequence, Tuple, Optional, Union
from pydantic.schema import model_schema


from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents.agent import Agent
from langchain.chains.llm import LLMChain
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.agents.agent import AgentOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain.pydantic_v1 import Field
from langchain.schema import AgentAction, AgentFinish, OutputParserException, BasePromptTemplate
from langchain.agents.agent import AgentExecutor
from langchain.callbacks.base import BaseCallbackManager
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool

HUMAN_MESSAGE_TEMPLATE = "{input}\n\n{agent_scratchpad}"
logger = logging.getLogger(__name__)


class StructuredChatOutputParserWithRetries(AgentOutputParser):
    """Output parser with retries for the structured chat agent."""

    base_parser: AgentOutputParser = Field(default_factory=StructuredChatOutputParser)
    """The base parser to use."""
    output_fixing_parser: Optional[OutputFixingParser] = None
    """The output fixing parser to use."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        special_tokens = ["Action:", "<|observation|>"]
        first_index = min([text.find(token) if token in text else len(text) for token in special_tokens])
        text = text[:first_index]
        if "tool_call" in text:
            action_end = text.find("```")
            action = text[:action_end].strip()
            params_str_start = text.find("(") + 1
            params_str_end = text.rfind(")")
            params_str = text[params_str_start:params_str_end]

            params_pairs = [param.split("=") for param in params_str.split(",") if "=" in param]
            params = {pair[0].strip(): pair[1].strip().strip("'\"") for pair in params_pairs}

            action_json = {
                "action": action,
                "action_input": params
            }
        else:
            action_json = {
                "action": "Final Answer",
                "action_input": text
            }
        action_str = f"""
Action:
```
{json.dumps(action_json, ensure_ascii=False)}
```"""
        try:
            if self.output_fixing_parser is not None:
                parsed_obj: Union[
                    AgentAction, AgentFinish
                ] = self.output_fixing_parser.parse(action_str)
            else:
                parsed_obj = self.base_parser.parse(action_str)
            return parsed_obj
        except Exception as e:
            raise OutputParserException(f"Could not parse LLM output: {text}") from e

    @property
    def _type(self) -> str:
        return "structured_chat_ChatGLM3_6b_with_retries"


class StructuredGLM3ChatAgent(Agent):
    """Structured Chat Agent."""

    output_parser: AgentOutputParser = Field(
        default_factory=StructuredChatOutputParserWithRetries
    )
    """Output parser for the agent."""

    @property
    def observation_prefix(self) -> str:
        """Prefix to append the ChatGLM3-6B observation with."""
        return "Observation:"

    @property
    def llm_prefix(self) -> str:
        """Prefix to append the llm call with."""
        return "Thought:"

    def _construct_scratchpad(
            self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> str:
        agent_scratchpad = super()._construct_scratchpad(intermediate_steps)
        if not isinstance(agent_scratchpad, str):
            raise ValueError("agent_scratchpad should be of type string.")
        if agent_scratchpad:
            return (
                f"This was your previous work "
                f"(but I haven't seen any of it! I only see what "
                f"you return as final answer):\n{agent_scratchpad}"
            )
        else:
            return agent_scratchpad

    @classmethod
    def _get_default_output_parser(
            cls, llm: Optional[BaseLanguageModel] = None, **kwargs: Any
    ) -> AgentOutputParser:
        return StructuredChatOutputParserWithRetries(llm=llm)

    @property
    def _stop(self) -> List[str]:
        return ["<|observation|>"]

    @classmethod
    def create_prompt(
            cls,
            tools: Sequence[BaseTool],
            prompt: str = None,
            input_variables: Optional[List[str]] = None,
            memory_prompts: Optional[List[BasePromptTemplate]] = None,
    ) -> BasePromptTemplate:
        tools_json = []
        tool_names = []
        for tool in tools:
            tool_schema = model_schema(tool.args_schema) if tool.args_schema else {}
            simplified_config_langchain = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool_schema.get("properties", {})
            }
            tools_json.append(simplified_config_langchain)
            tool_names.append(tool.name)
        formatted_tools = "\n".join([
            f"{tool['name']}: {tool['description']}, args: {tool['parameters']}"
            for tool in tools_json
        ])
        formatted_tools = formatted_tools.replace("'", "\\'").replace("{", "{{").replace("}", "}}")
        template = prompt.format(tool_names=tool_names,
                                 tools=formatted_tools,
                                 history="None",
                                 input="{input}",
                                 agent_scratchpad="{agent_scratchpad}")

        if input_variables is None:
            input_variables = ["input", "agent_scratchpad"]
        _memory_prompts = memory_prompts or []
        messages = [
            SystemMessagePromptTemplate.from_template(template),
            *_memory_prompts,
        ]
        return ChatPromptTemplate(input_variables=input_variables, messages=messages)

    @classmethod
    def from_llm_and_tools(
            cls,
            llm: BaseLanguageModel,
            tools: Sequence[BaseTool],
            prompt: str = None,
            callback_manager: Optional[BaseCallbackManager] = None,
            output_parser: Optional[AgentOutputParser] = None,
            human_message_template: str = HUMAN_MESSAGE_TEMPLATE,
            input_variables: Optional[List[str]] = None,
            memory_prompts: Optional[List[BasePromptTemplate]] = None,
            **kwargs: Any,
    ) -> Agent:
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
            callback_manager=callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        _output_parser = output_parser or cls._get_default_output_parser(llm=llm)
        return cls(
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            output_parser=_output_parser,
            **kwargs,
        )

    @property
    def _agent_type(self) -> str:
        raise ValueError


def initialize_glm3_agent(
        tools: Sequence[BaseTool],
        llm: BaseLanguageModel,
        prompt: str = None,
        memory: Optional[ConversationBufferWindowMemory] = None,
        agent_kwargs: Optional[dict] = None,
        *,
        tags: Optional[Sequence[str]] = None,
        **kwargs: Any,
) -> AgentExecutor:
    tags_ = list(tags) if tags else []
    agent_kwargs = agent_kwargs or {}
    agent_obj = StructuredGLM3ChatAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        prompt=prompt,
        **agent_kwargs
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent_obj,
        tools=tools,
        memory=memory,
        tags=tags_,
        **kwargs,
    )