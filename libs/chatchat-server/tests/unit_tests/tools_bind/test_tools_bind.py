# -*- coding: utf-8 -*-
from langchain.agents import tool as register_tool
from langchain_community.tools import ShellTool
from langchain_core.runnables import RunnableBinding
from pydantic.v1 import Extra, Field

from langchain_chatchat.agent_toolkits import BaseToolOutput
from langchain_chatchat.agents.platform_tools.base import _get_assistants_tool
from langchain_chatchat.chat_models import ChatPlatformAI


class TestToolsBind:
    def test_tools_bind(self):
        @register_tool
        def shell(query: str = Field(description="The command to execute")):
            """Use Shell to execute system shell commands"""
            tool = ShellTool()
            return BaseToolOutput(tool.run(tool_input=query))

        llm = ChatPlatformAI(
            api_key="abc"
        )  # Create a new instance of the ChatZhipuAI class

        tools = [
            shell,
            {"type": "code_interpreter", "code_interpreter": {"sandbox": "none"}},
            {"type": "web_browser"},
            {"type": "drawing_tool"},
        ]
        dict_tools = [_get_assistants_tool(tool) for tool in tools]
        assert isinstance(dict_tools, list)
        assert isinstance(dict_tools[0], dict)
        assert isinstance(dict_tools[1], dict)
        assert isinstance(dict_tools[2], dict)
        assert isinstance(dict_tools[3], dict)
        llm_with_all_tools = llm.bind(tools=dict_tools)

        assert llm_with_all_tools is not None
        assert isinstance(llm_with_all_tools, RunnableBinding)
        self.llm_with_all_tools = llm_with_all_tools
