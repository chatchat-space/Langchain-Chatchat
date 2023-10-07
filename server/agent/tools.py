import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.agent.math import calculate
from server.agent.translator import translate
from server.agent.weather import weathercheck
from server.agent.shell import shell
from langchain.agents import Tool
from server.agent.search_knowledge import search_knowledge
from server.agent.search_internet import search_internet

tools = [
    Tool.from_function(
        func=calculate,
        name="计算器工具",
        description="进行简单的数学运算"
    ),
    Tool.from_function(
        func=translate,
        name="翻译工具",
        description="如果你无法访问互联网，并且需要翻译各种语言，应该使用这个工具"
    ),
    Tool.from_function(
        func=weathercheck,
        name="天气查询工具",
        description="如果你无法访问互联网，并需要查询中国各地未来24小时的天气，你应该使用这个工具,每轮对话仅能使用一次",
    ),
    Tool.from_function(
        func=shell,
        name="shell工具",
        description="使用命令行工具输出",
    ),
    Tool.from_function(
        func=search_knowledge,
        name="知识库查询工具",
        description="访问知识库来获取答案",
    ),
    Tool.from_function(
        func=search_internet,
        name="互联网查询工具",
        description="如果你无法访问互联网，这个工具可以帮助你访问Bing互联网来解答问题",
    ),

]
tool_names = [tool.name for tool in tools]
