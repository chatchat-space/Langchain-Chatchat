# LangChain 的 Shell 工具
from langchain_community.tools import ShellTool

from chatchat.server.pydantic_v1 import Field

from .tools_registry import BaseToolOutput, regist_tool


@regist_tool(title="系统命令")
def shell(query: str = Field(description="The command to execute")):
    """Use Shell to execute system shell commands"""
    tool = ShellTool()
    return BaseToolOutput(tool.run(tool_input=query))
