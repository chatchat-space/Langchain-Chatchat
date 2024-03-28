from chatchat.server.pydantic_v1 import Field
from .tools_registry import regist_tool


@regist_tool
def calculate(text: str = Field(description="a math expression")) -> float:
    '''
    Useful to answer questions about simple calculations.
    translate user question to a math expression that can be evaluated by numexpr.
    '''
    import numexpr

    try:
        return str(numexpr.evaluate(text))
    except Exception as e:
        return f"wrong: {e}"
