from langchain.agents.agent_toolkits import NLAToolkit
from langchain.llms import OpenAI
from langchain.tools.plugin import AIPlugin
from langchain.schema import Document
from langchain.vectorstores import FAISS
from server.knowledge_base.kb_service.base import EmbeddingsFunAdapter
from server.agent.tool_retriever_agent_executor.core import RetrievalToolExecutor

__all__ = ["RetrievalToolExecutor", "define_tools_retriever"]

urls = [
    # 'https://openai.creaticode.com',
    'https://wolframalpha.com'
]

AI_PLUGINS = [AIPlugin.from_url(url + "/.well-known/ai-plugin.json") for url in urls]


async def define_tools_retriever():
    """Define tools with load retriever."""

    llm = OpenAI(temperature=0)
    embed_func = EmbeddingsFunAdapter()
    # embeddings = await embed_func.aembed_query(query)
    docs = [
        Document(
            page_content=plugin.description_for_model,
            metadata={"plugin_name": plugin.name_for_model},
        )
        for plugin in AI_PLUGINS
    ]
    vector_store = FAISS.from_documents(docs, embed_func)
    toolkits_dict = {
        plugin.name_for_model: NLAToolkit.from_llm_and_ai_plugin(llm, plugin)
        for plugin in AI_PLUGINS
    }

    retriever = vector_store.as_retriever()

    return retriever, toolkits_dict
