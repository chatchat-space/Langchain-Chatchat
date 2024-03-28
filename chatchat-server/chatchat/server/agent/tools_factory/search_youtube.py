from chatchat.server.pydantic_v1 import Field
from .tools_registry import regist_tool


@regist_tool
def search_youtube(query: str = Field(description="Query for Videos search")):
    '''use this tools_factory to search youtube videos'''
    from langchain_community.tools import YouTubeSearchTool
    tool = YouTubeSearchTool()
    return tool.run(tool_input=query)
