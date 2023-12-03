from server.chat.knowledge_base_chat import knowledge_base_chat
import json
from configs import VECTOR_SEARCH_TOP_K, MAX_TOKENS, SCORE_THRESHOLD
import asyncio
from server.agent import model_container
from pydantic import BaseModel, Field


async def search_knowledge_base_iter(database: str, query: str) -> str:
    response = await knowledge_base_chat(query=query,
                                         knowledge_base_name=database,
                                         model_name=model_container.MODEL.model_name,
                                         temperature=0.01,
                                         history=[],
                                         top_k=VECTOR_SEARCH_TOP_K,
                                         max_tokens=MAX_TOKENS,
                                         prompt_name="default",
                                         score_threshold=SCORE_THRESHOLD,
                                         stream=False)

    contents = ""
    async for data in response.body_iterator:
        data = json.loads(data)
        contents = data["answer"] + "\n出处:\n"
        docs = data["docs"]
        for doc in docs:
            contents += doc + "\n"
    return contents


class SearchKnowledgeInput(BaseModel):
    database: str = Field(description="Database for Knowledge Search")
    query: str = Field(description="Query for Knowledge Search")


def search_local_knowledgebase(database: str, query: str):
    return asyncio.run(search_knowledge_base_iter(database, query))
