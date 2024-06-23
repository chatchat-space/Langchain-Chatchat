from urllib.parse import urlencode

from chatchat.configs import KB_INFO
from chatchat.server.agent.tools_factory.tools_registry import (
    BaseToolOutput,
    regist_tool,
)
from chatchat.server.knowledge_base.kb_api import list_kbs
from chatchat.server.knowledge_base.kb_doc_api import DocumentWithVSId, search_docs
from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

template = (
    "Use local knowledgebase from one or more of these:\n{KB_info}\n to get information，Only local data on "
    "this knowledge use this tool. The 'database' should be one of the above [{key}]."
)
KB_info_str = "\n".join([f"{key}: {value}" for key, value in KB_INFO.items()])
template_knowledge = template.format(KB_info=KB_info_str, key="samples")


class KBToolOutput(BaseToolOutput):
    def __str__(self) -> str:
        context = ""
        docs = self.data["docs"]
        source_documents = []

        for inum, doc in enumerate(docs):
            doc = DocumentWithVSId.parse_obj(doc)
            source_documents.append(doc.page_content)

        if len(source_documents) == 0:
            context = "没有找到相关文档,请更换关键词重试"
        else:
            for doc in source_documents:
                context += doc + "\n\n"

        return context


def search_knowledgebase(query: str, database: str, config: dict):
    docs = search_docs(
        query=query,
        knowledge_base_name=database,
        top_k=config["top_k"],
        score_threshold=config["score_threshold"],
    )
    return {"knowledge_base": database, "docs": docs}


@regist_tool(description=template_knowledge, title="本地知识库")
def search_local_knowledgebase(
    database: str = Field(
        description="Database for Knowledge Search",
        choices=[kb.kb_name for kb in list_kbs().data],
    ),
    query: str = Field(description="Query for Knowledge Search"),
):
    """"""
    tool_config = get_tool_config("search_local_knowledgebase")
    ret = search_knowledgebase(query=query, database=database, config=tool_config)
    return KBToolOutput(ret, database=database)
