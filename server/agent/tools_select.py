from langchain.tools import Tool
from server.agent.tools import *

## 请注意，如果你是为了使用AgentLM，在这里，你应该使用英文版本。

tools = [
    Tool.from_function(
        func=calculate,
        name="计算器工具",
        description="进行简单的数学运算, 只是简单的, 使用Wolfram数学工具进行更复杂的运算",
        args_schema=CalculatorInput,
    ),
    Tool.from_function(
        func=translate,
        name="翻译工具",
        description="如果你无法访问互联网，并且需要翻译各种语言，应该使用这个工具",
        args_schema=TranslateInput,
    ),
    Tool.from_function(
        func=weathercheck,
        name="天气查询工具",
        description="无需访问互联网，使用这个工具查询中国各地未来24小时的天气",
        args_schema=WhetherSchema,
    ),
    Tool.from_function(
        func=shell,
        name="shell工具",
        description="使用命令行工具输出",
        args_schema=ShellInput,
    ),
    Tool.from_function(
        func=knowledge_search_more,
        name="知识库查询工具",
        description="优先访问知识库来获取答案",
        args_schema=KnowledgeSearchInput,
    ),
    Tool.from_function(
        func=search_internet,
        name="互联网查询工具",
        description="如果你无法访问互联网，这个工具可以帮助你访问Bing互联网来解答问题",
        args_schema=SearchInternetInput,
    ),
    Tool.from_function(
        func=wolfram,
        name="Wolfram数学工具",
        description="高级的数学运算工具，能够完成非常复杂的数学问题",
        args_schema=WolframInput,
    ),
    Tool.from_function(
        func=youtube_search,
        name="Youtube搜索工具",
        description="使用这个工具在Youtube上搜索视频",
        args_schema=YoutubeInput,
    ),
]

tool_names = [tool.name for tool in tools]
