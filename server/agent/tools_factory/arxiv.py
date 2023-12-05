# LangChain 的 ArxivQueryRun 工具
from pydantic import BaseModel, Field
from langchain.tools.arxiv.tool import ArxivQueryRun
def arxiv(query: str):
    tool = ArxivQueryRun()
    return tool.run(tool_input=query)

class ArxivInput(BaseModel):
    query: str = Field(description="The search query title")