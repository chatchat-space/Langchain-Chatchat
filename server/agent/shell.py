from langchain.tools import ShellTool
def shell(query: str):
    tool = ShellTool()
    return tool.run(tool_input=query)

