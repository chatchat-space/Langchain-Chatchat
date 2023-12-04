from langchain_core.tools import StructuredTool
from server.agent.tools_factory import *
from configs import KB_INFO

template = "Use local knowledgebase from one or more of these:\n{KB_info}\n to get information，Only local data on this knowledge use this tool."
KB_info_str = '\n'.join([f"{key}: {value}" for key, value in KB_INFO.items()])
template_knowledge = template.format(KB_info=KB_info_str)

all_tools = [
    StructuredTool.from_function(
        func=calculate,
        name="calculate",
        description="Useful for when you need to answer questions about simple calculations",
        args_schema=CalculatorInput,
    ),
    StructuredTool.from_function(
        func=arxiv,
        name="arxiv",
        description="A wrapper around Arxiv.org for searching and retrieving scientific articles in various fields.",
        args_schema=ArxivInput,
    ),
    StructuredTool.from_function(
        func=shell,
        name="shell",
        description="Use Shell to execute Linux commands",
        args_schema=ShellInput,
    ),
    StructuredTool.from_function(
        func=wolfram,
        name="wolfram",
        description="Useful for when you need to calculate difficult formulas",
        args_schema=WolframInput,
    ),
    StructuredTool.from_function(
        func=search_youtube,
        name="search_youtube",
        description="use this tools_factory to search youtube videos",
        args_schema=YoutubeInput,
    ),
    StructuredTool.from_function(
        func=weather_check,
        name="weather_check",
        description="Use this tool to check the weather at a specific location",
        args_schema=WeatherInput,
    ),
    StructuredTool.from_function(
        func=search_internet,
        name="search_internet",
        description="Use this tool to use bing search engine to search the internet and get information",
        args_schema=SearchInternetInput,
    ),
    StructuredTool.from_function(
        func=search_local_knowledgebase,
        name="search_local_knowledgebase",
        description=template_knowledge,
        args_schema=SearchKnowledgeInput,
    ),
]

