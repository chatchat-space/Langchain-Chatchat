from typing import Dict, List

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.utilities.bing_search import BingSearchAPIWrapper
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from markdownify import markdownify
from strsimpy.normalized_levenshtein import NormalizedLevenshtein

from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

from .tools_registry import BaseToolOutput, regist_tool


def bing_search(text, config):
    search = BingSearchAPIWrapper(
        bing_subscription_key=config["bing_key"],
        bing_search_url=config["bing_search_url"],
    )
    return search.results(text, config["result_len"])


def duckduckgo_search(text, config):
    search = DuckDuckGoSearchAPIWrapper()
    return search.results(text, config["result_len"])


def metaphor_search(
    text: str,
    config: dict,
) -> List[Dict]:
    from metaphor_python import Metaphor

    client = Metaphor(config["metaphor_api_key"])
    search = client.search(text, num_results=config["result_len"], use_autoprompt=True)
    contents = search.get_contents().contents
    for x in contents:
        x.extract = markdownify(x.extract)
    if config["split_result"]:
        docs = [
            Document(page_content=x.extract, metadata={"link": x.url, "title": x.title})
            for x in contents
        ]
        text_splitter = RecursiveCharacterTextSplitter(
            ["\n\n", "\n", ".", " "],
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
        )
        splitted_docs = text_splitter.split_documents(docs)
        if len(splitted_docs) > config["result_len"]:
            normal = NormalizedLevenshtein()
            for x in splitted_docs:
                x.metadata["score"] = normal.similarity(text, x.page_content)
            splitted_docs.sort(key=lambda x: x.metadata["score"], reverse=True)
            splitted_docs = splitted_docs[: config["result_len"]]

        docs = [
            {
                "snippet": x.page_content,
                "link": x.metadata["link"],
                "title": x.metadata["title"],
            }
            for x in splitted_docs
        ]
    else:
        docs = [
            {"snippet": x.extract, "link": x.url, "title": x.title} for x in contents
        ]

    return docs


SEARCH_ENGINES = {
    "bing": bing_search,
    "duckduckgo": duckduckgo_search,
    "metaphor": metaphor_search,
}


def search_result2docs(search_results):
    docs = []
    for result in search_results:
        doc = Document(
            page_content=result["snippet"] if "snippet" in result.keys() else "",
            metadata={
                "source": result["link"] if "link" in result.keys() else "",
                "filename": result["title"] if "title" in result.keys() else "",
            },
        )
        docs.append(doc)
    return docs


def search_engine(query: str, config: dict):
    search_engine_use = SEARCH_ENGINES[config["search_engine_name"]]
    results = search_engine_use(
        text=query, config=config["search_engine_config"][config["search_engine_name"]]
    )
    docs = search_result2docs(results)
    context = ""
    docs = [
        f"""出处 [{inum + 1}] [{doc.metadata["source"]}]({doc.metadata["source"]}) \n\n{doc.page_content}\n\n"""
        for inum, doc in enumerate(docs)
    ]

    for doc in docs:
        context += doc + "\n"
    return context


@regist_tool(title="互联网搜索")
def search_internet(query: str = Field(description="query for Internet search")):
    """Use this tool to use bing search engine to search the internet and get information."""
    tool_config = get_tool_config("search_internet")
    return BaseToolOutput(search_engine(query=query, config=tool_config))
