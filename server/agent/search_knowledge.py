## 单独运行的时候需要添加
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from server.chat.knowledge_base_chat import knowledge_base_chat
from configs import LLM_MODEL, TEMPERATURE, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD

import asyncio


async def search_knowledge_base_iter(query: str):
    response = await knowledge_base_chat(query=query,
                                         knowledge_base_name="tcqa",
                                         model_name=LLM_MODEL,
                                         temperature=TEMPERATURE,
                                         history=[],
                                         top_k = VECTOR_SEARCH_TOP_K,
                                         prompt_name = "knowledge_base_chat",
                                         score_threshold = SCORE_THRESHOLD,
                                         stream=False)

    contents = ""
    async for data in response.body_iterator: # 这里的data是一个json字符串
        data = json.loads(data)
        contents = data["answer"]
        docs = data["docs"]
    return contents

def search_knowledge(query: str):
    return asyncio.run(search_knowledge_base_iter(query))


if __name__ == "__main__":
    result = search_knowledge("大数据男女比例")
    print("答案:",result)
