# Langchain 自带的 YouTube 搜索工具封装
from langchain.tools import YouTubeSearchTool
def youtube_search(query: str):
    tool = YouTubeSearchTool()
    return tool.run(tool_input=query)