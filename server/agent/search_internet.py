## 单独运行的时候需要添加
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
from server.chat import search_engine_chat
from configs import LLM_MODEL, TEMPERATURE, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD

import asyncio


async def search_engine_iter(query: str):
    response = await search_engine_chat(query=query,
                                         search_engine_name="bing",
                                         model_name=LLM_MODEL,
                                         temperature=TEMPERATURE,
                                         history=[],
                                         top_k = VECTOR_SEARCH_TOP_K,
                                         prompt_name = "knowledge_base_chat",
                                         stream=False)

    contents = ""
    async for data in response.body_iterator: # 这里的data是一个json字符串
        data = json.loads(data)
        contents = data["answer"]
        docs = data["docs"]
    return contents

def search_internet(query: str):
    return asyncio.run(search_engine_iter(query))


if __name__ == "__main__":
    result = search_internet("大数据男女比例")
    print("答案:",result)
