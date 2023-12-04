from configs import MAX_TOKENS, DEFAULT_SEARCH_ENGINE
from server.agent import model_container
from pydantic import BaseModel, Field
from langchain.utilities.bing_search import BingSearchAPIWrapper
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from configs import (BING_SEARCH_URL, BING_SUBSCRIPTION_KEY, METAPHOR_API_KEY,
                     LLM_MODELS, SEARCH_ENGINE_TOP_K, OVERLAP_SIZE)
from server.utils import get_ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Literal
from server.chat.utils import History
from langchain.docstore.document import Document
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from markdownify import markdownify

prompt_template = """
<指令>这是我搜索到的互联网信息，请你根据这些信息进行提取并有调理，简洁的回答问题。
如果无法从中得到答案，请说 “无法搜索到能回答问题的内容”。 </指令>\n
<已知信息>{{ context }}</已知信息>\n
<问题>{{ question }}</问题>\n
"""


def bing_search(text, result_len=SEARCH_ENGINE_TOP_K, **kwargs):
    if not (BING_SEARCH_URL and BING_SUBSCRIPTION_KEY):
        return "Key and BING_SEARCH_URL Error!"
    search = BingSearchAPIWrapper(bing_subscription_key=BING_SUBSCRIPTION_KEY,
                                  bing_search_url=BING_SEARCH_URL)
    return search.results(text, result_len)


def duckduckgo_search(text, result_len=SEARCH_ENGINE_TOP_K, **kwargs):
    search = DuckDuckGoSearchAPIWrapper()
    return search.results(text, result_len)


def metaphor_search(
        text: str,
        result_len: int = SEARCH_ENGINE_TOP_K,
        split_result: bool = False,
        chunk_size: int = 500,
        chunk_overlap: int = OVERLAP_SIZE,
) -> List[Dict]:
    from metaphor_python import Metaphor

    if not METAPHOR_API_KEY:
        return []

    client = Metaphor(METAPHOR_API_KEY)
    search = client.search(text, num_results=result_len, use_autoprompt=True)
    contents = search.get_contents().contents
    for x in contents:
        x.extract = markdownify(x.extract)
    if split_result:
        docs = [Document(page_content=x.extract,
                         metadata={"link": x.url, "title": x.title})
                for x in contents]
        text_splitter = RecursiveCharacterTextSplitter(["\n\n", "\n", ".", " "],
                                                       chunk_size=chunk_size,
                                                       chunk_overlap=chunk_overlap)
        splitted_docs = text_splitter.split_documents(docs)
        if len(splitted_docs) > result_len:
            normal = NormalizedLevenshtein()
            for x in splitted_docs:
                x.metadata["score"] = normal.similarity(text, x.page_content)
            splitted_docs.sort(key=lambda x: x.metadata["score"], reverse=True)
            splitted_docs = splitted_docs[:result_len]

        docs = [{"snippet": x.page_content,
                 "link": x.metadata["link"],
                 "title": x.metadata["title"]}
                for x in splitted_docs]
    else:
        docs = [{"snippet": x.extract,
                 "link": x.url,
                 "title": x.title}
                for x in contents]

    return docs


SEARCH_ENGINES = {"bing": bing_search,
                  "duckduckgo": duckduckgo_search,
                  "metaphor": metaphor_search,
                  }


def search_result2docs(search_results):
    docs = []
    for result in search_results:
        doc = Document(page_content=result["snippet"] if "snippet" in result.keys() else "",
                       metadata={"source": result["link"] if "link" in result.keys() else "",
                                 "filename": result["title"] if "title" in result.keys() else ""})
        docs.append(doc)
    return docs


def lookup_search_engine(
        query: str,
        search_engine_name: str,
        top_k: int = SEARCH_ENGINE_TOP_K,
        split_result: bool = False,
):
    search_engine = SEARCH_ENGINES[search_engine_name]
    results = search_engine(query, result_len=top_k, split_result=split_result)
    docs = search_result2docs(results)
    return docs


def search_engine(query: str,
                  search_engine_name: str,
                  top_k: int,
                  max_tokens: int,
                  model_name: str = LLM_MODELS[0],
                  verbose: Literal["Origin", "Conclude", "All"] = "Origin"):
    model = get_ChatOpenAI(
        model_name=model_name,
        temperature=0.01,
        max_tokens=max_tokens,
    )

    docs = lookup_search_engine(query, search_engine_name, top_k, split_result=True)
    context = "\n".join([doc.page_content for doc in docs])

    docs = [
        f"""出处 [{inum + 1}] [{doc.metadata["source"]}]({doc.metadata["source"]}) \n\n{doc.page_content}\n\n"""
        for inum, doc in enumerate(docs)
    ]

    if verbose != "Origin":

        # Use embed and LLM to conclude

        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages([input_msg])
        chain = LLMChain(prompt=chat_prompt, llm=model)
        contents = "联网大模型总结内容: \n\n"
        contents += chain.run({"context": context, "question": query})

        if verbose == "All":
            contents += "\n\n原文信息:"
            for doc in docs:
                contents += doc + "\n"
    else:
        contents = docs
    return contents


def search_internet(query: str):
    return search_engine(query=query, search_engine_name=DEFAULT_SEARCH_ENGINE, top_k=SEARCH_ENGINE_TOP_K,
                         model_name=model_container.MODEL.model_name,
                         max_tokens=MAX_TOKENS, verbose="Origin")


class SearchInternetInput(BaseModel):
    query: str = Field(description="Query for Internet search")
