# Langchain 自带的 Wolfram Alpha API 封装
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.pydantic_v1 import BaseModel, Field
wolfram_alpha_appid = "your key"
def wolfram(query: str):
    wolfram = WolframAlphaAPIWrapper(wolfram_alpha_appid=wolfram_alpha_appid)
    ans = wolfram.run(query)
    return ans

class WolframInput(BaseModel):
    formula: str = Field(description="The formula to be calculated")
