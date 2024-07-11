# LangChain 的 WikipediaQueryRun 工具
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from chatchat.server.pydantic_v1 import Field



from .tools_registry import BaseToolOutput, regist_tool


@regist_tool(title="维基百科搜索")
def wikipedia_search(query: str = Field(description="The search query")):
    """ A wrapper that uses Wikipedia to search."""
    api_wrapper = WikipediaAPIWrapper(lang="zh")
    tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    return BaseToolOutput(tool.run(tool_input=query))
                          
                          
                          
