from chatchat.server.pydantic_v1 import Field

from .tools_registry import BaseToolOutput, regist_tool


@regist_tool(title="数学计算器")
def calculate(text: str = Field(description="a math expression")) -> float:
    """
    Useful to answer questions about simple calculations.
    translate user question to a math expression that can be evaluated by numexpr.
    """
    import numexpr

    try:
        ret = str(numexpr.evaluate(text))
    except Exception as e:
        ret = f"wrong: {e}"

    return BaseToolOutput(ret)
