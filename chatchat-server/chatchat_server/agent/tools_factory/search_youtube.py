from langchain_community.tools import YouTubeSearchTool
from chatchat_server.pydantic_types import BaseModel, Field


def search_youtube(query: str):
    tool = YouTubeSearchTool()
    return tool.run(tool_input=query)

class YoutubeInput(BaseModel):
    query: str = Field(description="Query for Videos search")
