from langchain_community.tools import YouTubeSearchTool
from server.pydantic_v1 import BaseModel, Field


def search_youtube(query: str):
    tool = YouTubeSearchTool()
    return tool.run(tool_input=query)

class YoutubeInput(BaseModel):
    query: str = Field(description="Query for Videos search")
