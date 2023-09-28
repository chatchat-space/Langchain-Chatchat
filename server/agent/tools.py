import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.agent.math import calculate
from server.agent.translator import translate
from server.agent.weather import weathercheck
from server.agent.shell import shell
from server.agent.google_search import google_search
from langchain.agents import Tool

tools = [
    Tool.from_function(
        func=calculate,
        name="计算器工具",
        description="进行简单的数学运算"
    ),
    Tool.from_function(
        func=translate,
        name="翻译工具",
        description="翻译各种语言"
    ),
    Tool.from_function(
        func=weathercheck,
        name="天气查询工具",
        description="查询天气",
    ),
    Tool.from_function(
        func=shell,
        name="shell工具",
        description="使用命令行工具输出",
    ),
    Tool.from_function(
        func=google_search,
        name="谷歌搜索工具",
        description="使用谷歌搜索",
    )
]
tool_names = [tool.name for tool in tools]
