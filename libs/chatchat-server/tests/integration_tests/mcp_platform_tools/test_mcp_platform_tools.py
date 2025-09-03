# -*- coding: utf-8 -*-
from mcp import ClientSession, StdioServerParameters, stdio_client

from chatchat.server.agents_registry.agents_registry import agents_registry
from chatchat.server.utils import get_ChatPlatformAIParams
from langchain_chatchat import ChatPlatformAI
from langchain_chatchat.agent_toolkits.mcp_kit.client import MultiServerMCPClient
from langchain_chatchat.agents import PlatformToolsRunnable
from langchain_chatchat.agents.platform_tools import PlatformToolsAction, PlatformToolsFinish, \
    PlatformToolsActionToolStart, \
    PlatformToolsActionToolEnd, PlatformToolsLLMStatus
from langchain_chatchat.callbacks.agent_callback_handler import AgentStatus
import os
import logging
import logging.config

import pytest

from langchain_chatchat.agent_toolkits.mcp_kit.tools import load_mcp_tools
from langchain_chatchat.utils import History


@pytest.mark.asyncio
async def test_mcp_stdio_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore
    # Create and run the agent
    llm_params = get_ChatPlatformAIParams(
        model_name="glm-4.5",
        temperature=0.01,
        max_tokens=12000,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="platform-knowledge-mode",
        agents_registry=agents_registry,
        llm=llm,
        mcp_connections={
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": [f"{os.path.dirname(__file__)}/math_server.py"],
                "transport": "stdio"
            }
        },
    )
    chat_iterator = agent_executor.invoke(chat_input="计算下 2 乘以 5,之后计算 100*2")
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
async def test_mcp_multi_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore

    # Create and run the agent
    llm_params = get_ChatPlatformAIParams(
        model_name="glm-4.5",
        temperature=0.01,
        max_tokens=12000,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="platform-knowledge-mode",
        agents_registry=agents_registry,
        llm=llm,
        mcp_connections={
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": [f"{os.path.dirname(__file__)}/math_server.py"],
                "transport": "stdio",
                "env": {
                    **os.environ,
                    "PYTHONHASHSEED": "0",
                },
            },
            "playwright": {
                "command": "npx",
                "args": [
                    "@playwright/mcp@latest"
                ],
                "transport": "stdio",
            },
        }
    )
    chat_iterator = agent_executor.invoke(chat_input="使用浏览器下载项目到本地 https://github.com/microsoft/playwright-mcp")
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
async def test_mcp_tools(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore 
    from chatchat.settings import Settings
    llm_params = get_ChatPlatformAIParams(
        model_name="glm-4.5",
        temperature=0.01,
        max_tokens=12000,
    )
    llm = ChatPlatformAI(**llm_params)
    agent_executor = PlatformToolsRunnable.create_agent_executor(
        agent_type="platform-knowledge-mode",
        agents_registry=agents_registry,
        llm=llm,
        mcp_connections={
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": [f"{os.path.dirname(__file__)}/math_server.py"],
                "transport": "stdio"
            },
            "playwright": {
                        
                "command": "npx",
                "args": [
                    "@playwright/mcp@latest"
                ],
                "transport": "stdio",
            },
        },
    )
    chat_iterator = agent_executor.invoke(chat_input="计算下 2 乘以 5,之后计算 100*2,然后获取这个链接https://mp.weixin.qq.com/s/YCHHY6mA8-1o7hbXlyEyEQ 的文本,接着 使用浏览器下载项目到本地 https://github.com/microsoft/playwright-mcp")
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
