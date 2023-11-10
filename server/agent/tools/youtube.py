# Langchain 自带的 YouTube 搜索工具封装
from langchain.tools import YouTubeSearchTool
from pydantic import BaseModel, Field
def youtube_search(query: str):
    tool = YouTubeSearchTool()
    return tool.run(tool_input=query)

class YoutubeInput(BaseModel):
    location: str = Field(description="要搜索视频关键字")