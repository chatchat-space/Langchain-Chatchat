from pydantic import BaseModel, Field

def calculate(a: float, b: float, operator: str) -> float:
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        if b != 0:
            return a / b
        else:
            return float('inf')
    elif operator == "^":
        return a ** b
    else:
        raise ValueError("Unsupported operator")

class CalculatorInput(BaseModel):
    a: float = Field(description="first number")
    b: float = Field(description="second number")
    operator: str = Field(description="operator to use (e.g., +, -, *, /, ^)")
