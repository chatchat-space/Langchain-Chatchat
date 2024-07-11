"""
This file is a modified version for ChatGLM3-6B the original glm3_agent.py file from the langchain repo.
"""

import json
import logging
from typing import Optional, Sequence, Union

import langchain_core.messages
import langchain_core.prompts
from langchain.agents.agent import AgentOutputParser
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain_core.runnables import Runnable, RunnablePassthrough

from chatchat.server.pydantic_v1 import Field, model_schema, typing
from chatchat.utils import build_logger


logger = build_logger()

SYSTEM_PROMPT = "Answer the following questions as best as you can. You have access to the following tools:\n{tools}"
HUMAN_MESSAGE = "Let's start! Human:{input}\n\n{agent_scratchpad}"


class StructuredGLM3ChatOutputParser(AgentOutputParser):
    """
    Output parser with retries for the structured chat agent.
    """

    base_parser: AgentOutputParser = Field(default_factory=StructuredChatOutputParser)
    output_fixing_parser: Optional[OutputFixingParser] = None

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        print(text)

        special_tokens = ["Action:", "<|observation|>"]
        first_index = min(
            [
                text.find(token) if token in text else len(text)
                for token in special_tokens
            ]
        )
        text = text[:first_index]

        if "tool_call" in text:
            action_end = text.find("```")
            action = text[:action_end].strip()
            params_str_start = text.find("(") + 1
            params_str_end = text.rfind(")")
            params_str = text[params_str_start:params_str_end]

            params_pairs = [
                param.split("=") for param in params_str.split(",") if "=" in param
            ]
            params = {
                pair[0].strip(): pair[1].strip().strip("'\"") for pair in params_pairs
            }

            action_json = {"action": action, "action_input": params}
        else:
            action_json = {"action": "Final Answer", "action_input": text}
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
        return "StructuredGLM3ChatOutputParser"


def create_structured_glm3_chat_agent(
    llm: BaseLanguageModel, tools: Sequence[BaseTool]
) -> Runnable:
    tools_json = []
    for tool in tools:
        tool_schema = model_schema(tool.args_schema) if tool.args_schema else {}
        description = (
            tool.description.split(" - ")[1].strip()
            if tool.description and " - " in tool.description
            else tool.description
        )
        parameters = {
            k: {sub_k: sub_v for sub_k, sub_v in v.items() if sub_k != "title"}
            for k, v in tool_schema.get("properties", {}).items()
        }
        simplified_config_langchain = {
            "name": tool.name,
            "description": description,
            "parameters": parameters,
        }
        tools_json.append(simplified_config_langchain)
    tools = "\n".join(
        [json.dumps(tool, indent=4, ensure_ascii=False) for tool in tools_json]
    )

    prompt = ChatPromptTemplate(
        input_variables=["input", "agent_scratchpad"],
        input_types={
            "chat_history": typing.List[
                typing.Union[
                    langchain_core.messages.ai.AIMessage,
                    langchain_core.messages.human.HumanMessage,
                    langchain_core.messages.chat.ChatMessage,
                    langchain_core.messages.system.SystemMessage,
                    langchain_core.messages.function.FunctionMessage,
                    langchain_core.messages.tool.ToolMessage,
                ]
            ]
        },
        messages=[
            langchain_core.prompts.SystemMessagePromptTemplate(
                prompt=langchain_core.prompts.PromptTemplate(
                    input_variables=["tools"], template=SYSTEM_PROMPT
                )
            ),
            langchain_core.prompts.MessagesPlaceholder(
                variable_name="chat_history", optional=True
            ),
            langchain_core.prompts.HumanMessagePromptTemplate(
                prompt=langchain_core.prompts.PromptTemplate(
                    input_variables=["agent_scratchpad", "input"],
                    template=HUMAN_MESSAGE,
                )
            ),
        ],
    ).partial(tools=tools)

    llm_with_stop = llm.bind(stop=["<|observation|>"])
    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: x["intermediate_steps"],
        )
        | prompt
        | llm_with_stop
        | StructuredGLM3ChatOutputParser()
    )
    return agent
