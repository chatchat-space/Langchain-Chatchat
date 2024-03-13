from langchain.agents import tool


@tool
def calculate(text: str) -> float:
    '''
    Useful to answer questions about simple calculations.
    translate user question to a math expression that can be evaluated by numexpr.
    '''
    import numexpr

    try:
        return str(numexpr.evaluate(text))
    except Exception as e:
        return f"wrong: {e}"
