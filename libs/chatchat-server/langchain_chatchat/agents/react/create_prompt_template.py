from __future__ import annotations

import langchain_core.messages
import langchain_core.prompts
from langchain.prompts.chat import ChatPromptTemplate

from chatchat.server.pydantic_v1 import Field, model_schema, typing


def create_prompt_glm3_template(model_name: str, template: dict):
    SYSTEM_PROMPT = template.get("SYSTEM_PROMPT")
    HUMAN_MESSAGE = template.get("HUMAN_MESSAGE")
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
    )
    return prompt


def create_prompt_platform_template(model_name: str, template: dict):
    SYSTEM_PROMPT = template.get("SYSTEM_PROMPT")
    HUMAN_MESSAGE = template.get("HUMAN_MESSAGE")
    prompt = ChatPromptTemplate(
        input_variables=["input"],
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
                    input_variables=[], template=SYSTEM_PROMPT
                )
            ),
            langchain_core.prompts.MessagesPlaceholder(
                variable_name="chat_history", optional=True
            ),
            langchain_core.prompts.HumanMessagePromptTemplate(
                prompt=langchain_core.prompts.PromptTemplate(
                    input_variables=["input"],
                    template=HUMAN_MESSAGE,
                )
            ),
            langchain_core.prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
        ],
    )
    return prompt


def create_prompt_structured_react_template(model_name: str, template: dict):
    SYSTEM_PROMPT = template.get("SYSTEM_PROMPT")
    HUMAN_MESSAGE = template.get("HUMAN_MESSAGE")
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
                    input_variables=["tools", "tool_names"], template=SYSTEM_PROMPT
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
            langchain_core.prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
        ],
    )
    return prompt


def create_prompt_gpt_tool_template(model_name: str, template: dict):
    SYSTEM_PROMPT = template.get("SYSTEM_PROMPT")
    HUMAN_MESSAGE = template.get("HUMAN_MESSAGE")
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
                    input_variables=["tool_names"], template=SYSTEM_PROMPT
                )
            ),
            langchain_core.prompts.MessagesPlaceholder(
                variable_name="chat_history", optional=True
            ),
            langchain_core.prompts.HumanMessagePromptTemplate(
                prompt=langchain_core.prompts.PromptTemplate(
                    input_variables=["input"],
                    template=HUMAN_MESSAGE,
                )
            ),

            langchain_core.prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
        ],
    )
    return prompt


def create_prompt_platform_knowledge_mode_template(model_name: str, template: dict):
    SYSTEM_PROMPT = template.get("SYSTEM_PROMPT")
    HUMAN_MESSAGE = template.get("HUMAN_MESSAGE")
    prompt = ChatPromptTemplate(
        input_variables=["input"],
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
                    input_variables=["current_working_directory", "tools", "mcp_tools"], template=SYSTEM_PROMPT
                )
            ),
            langchain_core.prompts.MessagesPlaceholder(
                variable_name="chat_history", optional=True
            ),
            langchain_core.prompts.HumanMessagePromptTemplate(
                prompt=langchain_core.prompts.PromptTemplate(
                    input_variables=["input", "datetime"],
                    template=HUMAN_MESSAGE,
                )
            ),
            langchain_core.prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
        ],
    )
    return prompt
