from langchain.tools import Tool
from server.agent.tools import *

## 请注意，如果你是为了使用AgentLM，在这里，你应该使用英文版本，下面的内容是英文版本。
# tools = [
#     Tool.from_function(
#         func=calculate,
#         name="Simple Calculator Tool",
#         description="Perform simple mathematical operations, Just simple, Use Wolfram Math Tool for more complex operations"
#     ),
#     Tool.from_function(
#         func=translate,
#         name="Translation Tool",
#         description="Use this tool if you can't access the internet and need to translate various languages"
#     ),
#     Tool.from_function(
#         func=weathercheck,
#         name="Weather Checking Tool",
#         description="Check the weather for various places in China for the next 24 hours without needing internet access"
#     ),
#     Tool.from_function(
#         func=shell,
#         name="Shell Tool",
#         description="Use command line tool output"
#     ),
#     Tool.from_function(
#         func=knowledge_search_more,
#         name="Knowledge Base Tool",
#         description="Prioritize accessing the knowledge base to get answers"
#     ),
#     Tool.from_function(
#         func=search_internet,
#         name="Internet Tool",
#         description="If you can't access the internet, this tool can help you access Bing to answer questions"
#     ),
#     Tool.from_function(
#         func=wolfram,
#         name="Wolfram Math Tool",
#         description="Use this tool to perform more complex mathematical operations"
#     ),
#     Tool.from_function(
#         func=youtube_search,
#         name="Youtube Search Tool",
#         description="Use this tool to search for videos on Youtube"
#     )
# ]

tools = [
    Tool.from_function(
        func=calculate,
        name="计算器工具",
        description="进行简单的数学运算, 只是简单的, 使用Wolfram数学工具进行更复杂的运算",
    ),
    Tool.from_function(
        func=translate,
        name="翻译工具",
        description="如果你无法访问互联网，并且需要翻译各种语言，应该使用这个工具"
    ),
    Tool.from_function(
        func=weathercheck,
        name="天气查询工具",
        description="无需访问互联网，使用这个工具查询中国各地未来24小时的天气",
    ),
    Tool.from_function(
        func=shell,
        name="shell工具",
        description="使用命令行工具输出",
    ),
    Tool.from_function(
        func=knowledge_search_more,
        name="知识库查询工具",
        description="优先访问知识库来获取答案",
    ),
    Tool.from_function(
        func=search_internet,
        name="互联网查询工具",
        description="如果你无法访问互联网，这个工具可以帮助你访问Bing互联网来解答问题",
    ),
    Tool.from_function(
        func=wolfram,
        name="Wolfram数学工具",
        description="高级的数学运算工具，能够完成非常复杂的数学问题"
    ),
    Tool.from_function(
        func=youtube_search,
        name="Youtube搜索工具",
        description="使用这个工具在Youtube上搜索视频"
    )
]

tool_names = [tool.name for tool in tools]
