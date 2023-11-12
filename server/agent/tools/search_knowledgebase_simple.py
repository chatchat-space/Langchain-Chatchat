from server.chat.knowledge_base_chat import knowledge_base_chat
from configs import VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, MAX_TOKENS
import json
import asyncio
from server.agent import model_container

async def search_knowledge_base_iter(database: str, query: str) -> str:
    response = await knowledge_base_chat(query=query,
                                         knowledge_base_name=database,
                                         model_name=model_container.MODEL.model_name,
                                         temperature=0.01,
                                         history=[],
                                         top_k=VECTOR_SEARCH_TOP_K,
                                         max_tokens=MAX_TOKENS,
                                         prompt_name="knowledge_base_chat",
                                         score_threshold=SCORE_THRESHOLD,
                                         stream=False)

    contents = ""
    async for data in response.body_iterator: # 这里的data是一个json字符串
        data = json.loads(data)
        contents = data["answer"]
        docs = data["docs"]
    return contents

def search_knowledgebase_simple(query: str):
    return asyncio.run(search_knowledge_base_iter(query))


if __name__ == "__main__":
    result = search_knowledgebase_simple("大数据男女比例")
    print("答案:",result)