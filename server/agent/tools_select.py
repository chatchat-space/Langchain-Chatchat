from langchain.tools import Tool
from server.agent.tools import *

tools = [
    Tool.from_function(
        func=calculate,
        name="calculate",
        description="Useful for when you need to answer questions about simple calculations",
        args_schema=CalculatorInput,
    ),
    Tool.from_function(
        func=arxiv,
        name="arxiv",
        description="A wrapper around Arxiv.org for searching and retrieving scientific articles in various fields.",
        args_schema=ArxivInput,
    ),
    Tool.from_function(
        func=weathercheck,
        name="weather_check",
        description="",
        args_schema=WeatherInput,
    ),
    Tool.from_function(
        func=shell,
        name="shell",
        description="Use Shell to execute Linux commands",
        args_schema=ShellInput,
    ),
    Tool.from_function(
        func=search_knowledgebase_complex,
        name="search_knowledgebase_complex",
        description="Use this tool to search local knowledgebase and get information",
        args_schema=KnowledgeSearchInput,
    ),
    Tool.from_function(
        func=search_internet,
        name="search_internet",
        description="Use this tool to use bing search engine to search the internet",
        args_schema=SearchInternetInput,
    ),
    Tool.from_function(
        func=wolfram,
        name="Wolfram",
        description="Useful for when you need to calculate difficult formulas",
        args_schema=WolframInput,
    ),
    Tool.from_function(
        func=search_youtube,
        name="search_youtube",
        description="use this tool to search youtube videos",
        args_schema=YoutubeInput,
    ),
]

tool_names = [tool.name for tool in tools]
