
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.agent.math import calculate
from server.agent.translator import translate
from server.agent.weather import weathercheck
from langchain.agents import Tool

tools = [
    Tool.from_function(
        func=calculate,
        name="计算器工具",
        description=""
    ),
    Tool.from_function(
        func=translate,
        name="翻译工具",
        description=""
    ),
    Tool.from_function(
        func=weathercheck,
        name="天气查询工具",
        description="",
    )
]
tool_names = [tool.name for tool in tools]
