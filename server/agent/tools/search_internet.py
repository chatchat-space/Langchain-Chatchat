import json
from server.chat.search_engine_chat import search_engine_chat
from configs import VECTOR_SEARCH_TOP_K, MAX_TOKENS
import asyncio
from server.agent import model_container
from pydantic import BaseModel, Field

async def search_engine_iter(query: str):
    response = await search_engine_chat(query=query,
                                         search_engine_name="bing", # 这里切换搜索引擎
                                         model_name=model_container.MODEL.model_name,
                                         temperature=0.01, # Agent 搜索互联网的时候，温度设置为0.01
                                         history=[],
                                         top_k = VECTOR_SEARCH_TOP_K,
                                         max_tokens= MAX_TOKENS,
                                         prompt_name = "default",
                                         stream=False)

    contents = ""

    async for data in response.body_iterator: # 这里的data是一个json字符串
        data = json.loads(data)
        contents = data["answer"]
        docs = data["docs"]

    return contents

def search_internet(query: str):
    return asyncio.run(search_engine_iter(query))

class SearchInternetInput(BaseModel):
    location: str = Field(description="Query for Internet search")


if __name__ == "__main__":
    result = search_internet("今天星期几")
    print("答案:",result)
