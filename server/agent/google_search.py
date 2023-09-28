import os
os.environ["GOOGLE_CSE_ID"] = ""
os.environ["GOOGLE_API_KEY"] = ""

from  langchain.tools import GoogleSearchResults
def google_search(query: str):
    tool = GoogleSearchResults()
    return tool.run(tool_input=query)