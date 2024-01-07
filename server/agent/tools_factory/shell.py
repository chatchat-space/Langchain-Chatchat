# LangChain 的 Shell 工具
from pydantic import BaseModel, Field
from langchain_community.tools import ShellTool
def shell(query: str):
    tool = ShellTool()
    return tool.run(tool_input=query)

class ShellInput(BaseModel):
    query: str = Field(description="The command to execute")