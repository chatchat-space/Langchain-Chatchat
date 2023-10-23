# Langchain 自带的 Wolfram Alpha API 封装
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
wolfram_alpha_appid = "your key"
def wolfram(query: str):
    wolfram = WolframAlphaAPIWrapper(wolfram_alpha_appid=wolfram_alpha_appid)
    ans = wolfram.run(query)
    return ans