from urllib.parse import urlencode
from pydantic import BaseModel, Field

from server.knowledge_base.kb_doc_api import search_docs
from configs import TOOL_CONFIG


def search_knowledgebase(query: str, database: str, config: dict):
    docs = search_docs(
        query=query,
        knowledge_base_name="samples",
        top_k=config["top_k"],
        score_threshold=config["score_threshold"])
    context = ""
    source_documents = []
    for inum, doc in enumerate(docs):
        filename = doc.metadata.get("source")
        parameters = urlencode({"knowledge_base_name": database, "file_name": filename})
        url = f"download_doc?" + parameters
        text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
        source_documents.append(text)

    if len(source_documents) == 0:
        context = "没有找到相关文档,请更换关键词重试"
    else:
        for doc in source_documents:
            context += doc + "\n"

    return context


class SearchKnowledgeInput(BaseModel):
    database: str = Field(description="Database for Knowledge Search")
    query: str = Field(description="Query for Knowledge Search")


def search_local_knowledgebase(database: str, query: str):
    tool_config = TOOL_CONFIG["search_local_knowledgebase"]
    return search_knowledgebase(query=query, database=database, config=tool_config)