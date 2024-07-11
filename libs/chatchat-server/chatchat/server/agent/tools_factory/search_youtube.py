from chatchat.server.pydantic_v1 import Field

from .tools_registry import BaseToolOutput, regist_tool


@regist_tool(title="油管视频")
def search_youtube(query: str = Field(description="Query for Videos search")):
    """use this tools_factory to search youtube videos"""
    from langchain_community.tools import YouTubeSearchTool

    tool = YouTubeSearchTool()
    return BaseToolOutput(tool.run(tool_input=query))
