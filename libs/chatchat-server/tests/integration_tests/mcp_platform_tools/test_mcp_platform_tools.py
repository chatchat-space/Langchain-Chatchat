# -*- coding: utf-8 -*-
from mcp import ClientSession, StdioServerParameters, stdio_client

from chatchat.server.agents_registry.agents_registry import agents_registry
from chatchat.server.utils import get_ChatPlatformAIParams
from langchain_chatchat import ChatPlatformAI
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


@pytest.mark.asyncio
async def test_mcp_stdio_tools(logging_conf):
    server_params = StdioServerParameters(
        command="python",
        # Make sure to update to the full absolute path to your math_server.py file
        args=[f"{os.path.dirname(__file__)}/math_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            llm_params = get_ChatPlatformAIParams(
                model_name="fun-lora",
                temperature=0.01,
                max_tokens=100,
            )
            llm = ChatPlatformAI(**llm_params)
            agent_executor = PlatformToolsRunnable.create_agent_executor(
                agent_type="openai-functions",
                agents_registry=agents_registry,
                llm=llm,
                tools=tools,
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
async def test_mcp_multi_tools(logging_conf):
    async with MultiServerMCPClient(
            {
                "math": {
                    "command": "python",
                    # Make sure to update to the full absolute path to your math_server.py file
                    "args": [f"D:/project/Langchain-Chatchat/libs/chatchat-server/tests/integration_tests/mcp_platform_tools/math_server.py"],
                    "transport": "stdio",
                    "env": {
                        **os.environ,
                        "PYTHONHASHSEED": "0",
                    },
                },
                # "playwright": {
                #     # make sure you start your weather server on port 8000
                #     "url": "http://localhost:8931/sse",
                #     "transport": "sse",
                # },
            }
    ) as client:

        # Get tools
        tools = client.get_tools()

        # Create and run the agent
        llm_params = get_ChatPlatformAIParams(
            model_name="glm-4-plus",
            temperature=0.01,
            max_tokens=1280000,
        )
        llm = ChatPlatformAI(**llm_params)
        agent_executor = PlatformToolsRunnable.create_agent_executor(
            agent_type="openai-functions",
            agents_registry=agents_registry,
            llm=llm,
            tools=tools,
        )
        chat_iterator = agent_executor.invoke(chat_input="下载项目到本地 https://github.com/microsoft/playwright-mcp")
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
                print(item.text)
                if item.status == AgentStatus.llm_end:
                    print("llm_end:" + item.text)
