# -*- coding: utf-8 -*-
import logging
import logging.config

import pytest
from langchain.agents import tool

from chatchat.server.agents_registry.agents_registry import agents_registry
from chatchat.server.utils import get_ChatPlatformAIParams
from langchain_chatchat import ChatPlatformAI
from langchain_chatchat.agents import PlatformToolsRunnable
from langchain_chatchat.agents.platform_tools import PlatformToolsAction, PlatformToolsFinish, \
    PlatformToolsActionToolStart, \
    PlatformToolsActionToolEnd, PlatformToolsLLMStatus
from langchain_chatchat.callbacks.agent_callback_handler import AgentStatus
from humanlayer import HumanLayer

hl = HumanLayer(verbose=True)


@tool
# @hl.require_approval()
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int


@tool
def add(first_int: int, second_int: int) -> int:
    "Add two integers."
    return first_int + second_int


@tool
def exp(exponent_num: int, base: int) -> int:
    "Exponentiate the base to the exponent power."
    return base ** exponent_num


@pytest.mark.asyncio
async def test_openai_functions_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore

    llm_params = get_ChatPlatformAIParams(
        model_name="glm-4-plus",
        temperature=0.01,
        max_tokens=100,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="openai-functions",
        agents_registry=agents_registry,
        llm=llm,
        tools=[multiply, exp, add],
    )

    chat_iterator = agent_executor.invoke(chat_input="计算下 2 乘以 5")
    async for item in chat_iterator:
        if isinstance(item, PlatformToolsAction):
            print("PlatformToolsAction:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsFinish):
            print("PlatformToolsFinish:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolStart):
            print("PlatformToolsActionToolStart:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolEnd):
            print("PlatformToolsActionToolEnd:" + str(item.to_json()))
        elif isinstance(item, PlatformToolsLLMStatus):
            if item.status == AgentStatus.llm_end:
                print("llm_end:" + item.text)


@pytest.mark.asyncio
async def test_platform_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore

    llm_params = get_ChatPlatformAIParams(
        model_name="glm-4-plus",
        temperature=0.01,
        max_tokens=100,
    )
    llm = ChatPlatformAI(**llm_params)

    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="platform-agent",
        agents_registry=agents_registry,
        llm=llm,
        tools=[multiply, exp, add],
    )

    chat_iterator = agent_executor.invoke(chat_input="计算下 2 乘以 5")
    async for item in chat_iterator:
        if isinstance(item, PlatformToolsAction):
            print("PlatformToolsAction:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsFinish):
            print("PlatformToolsFinish:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolStart):
            print("PlatformToolsActionToolStart:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolEnd):
            print("PlatformToolsActionToolEnd:" + str(item.to_json()))
        elif isinstance(item, PlatformToolsLLMStatus):
            if item.status == AgentStatus.llm_end:
                print("llm_end:" + item.text)


@pytest.mark.asyncio
async def test_chatglm3_chat_agent_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore

    llm_params = get_ChatPlatformAIParams(
        model_name="tmp-chatglm3-6b",
        temperature=0.01,
        max_tokens=100,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="glm3",
        agents_registry=agents_registry,
        llm=llm,
        tools=[multiply, exp, add],
    )

    chat_iterator = agent_executor.invoke(chat_input="计算下 2 乘以 5")
    async for item in chat_iterator:
        if isinstance(item, PlatformToolsAction):
            print("PlatformToolsAction:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsFinish):
            print("PlatformToolsFinish:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolStart):
            print("PlatformToolsActionToolStart:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolEnd):
            print("PlatformToolsActionToolEnd:" + str(item.to_json()))
        elif isinstance(item, PlatformToolsLLMStatus):
            if item.status == AgentStatus.llm_end:
                print("llm_end:" + item.text)


@pytest.mark.asyncio
async def test_qwen_chat_agent_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore

    llm_params = get_ChatPlatformAIParams(
        model_name="tmp_Qwen1.5-1.8B-Chat",
        temperature=0.01,
        max_tokens=100,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="qwen",
        agents_registry=agents_registry,
        llm=llm,
        tools=[multiply, exp, add],
    )

    chat_iterator = agent_executor.invoke(chat_input="2 add 5")
    async for item in chat_iterator:
        if isinstance(item, PlatformToolsAction):
            print("PlatformToolsAction:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsFinish):
            print("PlatformToolsFinish:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolStart):
            print("PlatformToolsActionToolStart:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolEnd):
            print("PlatformToolsActionToolEnd:" + str(item.to_json()))
        elif isinstance(item, PlatformToolsLLMStatus):
            if item.status == AgentStatus.llm_end:
                print("llm_end:" + item.text)


@pytest.mark.asyncio
async def test_qwen_structured_chat_agent_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore

    llm_params = get_ChatPlatformAIParams(
        model_name="tmp_Qwen1.5-1.8B-Chat",
        temperature=0.01,
        max_tokens=100,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="structured-chat-agent",
        agents_registry=agents_registry,
        llm=llm,
        tools=[multiply, exp, add],
    )

    chat_iterator = agent_executor.invoke(chat_input="2 add 5")
    async for item in chat_iterator:
        if isinstance(item, PlatformToolsAction):
            print("PlatformToolsAction:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsFinish):
            print("PlatformToolsFinish:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolStart):
            print("PlatformToolsActionToolStart:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolEnd):
            print("PlatformToolsActionToolEnd:" + str(item.to_json()))
        elif isinstance(item, PlatformToolsLLMStatus):
            if item.status == AgentStatus.llm_end:
                print("llm_end:" + item.text)


@pytest.mark.asyncio
async def test_human_platform_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore

    llm_params = get_ChatPlatformAIParams(
        model_name="glm-4-plus",
        temperature=0.01,
        max_tokens=100,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="platform-agent",
        agents_registry=agents_registry,
        llm=llm,
        tools=[multiply, exp, add],
        callbacks=[],
    )

    chat_iterator = agent_executor.invoke(chat_input="计算下 2 乘以 5")
    async for item in chat_iterator:
        if isinstance(item, PlatformToolsAction):
            print("PlatformToolsAction:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsFinish):
            print("PlatformToolsFinish:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolStart):
            print("PlatformToolsActionToolStart:" + str(item.to_json()))

        elif isinstance(item, PlatformToolsActionToolEnd):
            print("PlatformToolsActionToolEnd:" + str(item.to_json()))
        elif isinstance(item, PlatformToolsLLMStatus):
            if item.status == AgentStatus.llm_end:
                print("llm_end:" + item.text)

