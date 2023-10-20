from langchain.utilities import BingSearchAPIWrapper, DuckDuckGoSearchAPIWrapper
from configs import (BING_SEARCH_URL, BING_SUBSCRIPTION_KEY, METAPHOR_API_KEY,
                     LLM_MODEL, SEARCH_ENGINE_TOP_K, TEMPERATURE,
                     TEXT_SPLITTER_NAME, OVERLAP_SIZE)
from fastapi import Body
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List, Optional, Dict
from server.chat.utils import History
from langchain.docstore.document import Document
import json


def bing_search(text, result_len=SEARCH_ENGINE_TOP_K):
    if not (BING_SEARCH_URL and BING_SUBSCRIPTION_KEY):
        return [{"snippet": "please set BING_SUBSCRIPTION_KEY and BING_SEARCH_URL in os ENV",
                 "title": "env info is not found",
                 "link": "https://python.langchain.com/en/latest/modules/agents/tools/examples/bing_search.html"}]
    search = BingSearchAPIWrapper(bing_subscription_key=BING_SUBSCRIPTION_KEY,
                                  bing_search_url=BING_SEARCH_URL)
    return search.results(text, result_len)


def duckduckgo_search(text, result_len=SEARCH_ENGINE_TOP_K):
    search = DuckDuckGoSearchAPIWrapper()
    return search.results(text, result_len)


def metaphor_search(
    text: str,
    result_len: int = SEARCH_ENGINE_TOP_K,
    splitter_name: str = "SpacyTextSplitter",
    chunk_size: int = 500,
    chunk_overlap: int = OVERLAP_SIZE,
) -> List[Dict]:
    from metaphor_python import Metaphor
    from server.knowledge_base.kb_cache.faiss_cache import memo_faiss_pool
    from server.knowledge_base.utils import make_text_splitter

    if not METAPHOR_API_KEY:
        return []
    
    client = Metaphor(METAPHOR_API_KEY)
    search = client.search(text, num_results=result_len, use_autoprompt=True)
    contents = search.get_contents().contents

    # metaphor 返回的内容都是长文本，需要分词再检索
    docs = [Document(page_content=x.extract,
                     metadata={"link": x.url, "title": x.title})
            for x in contents]
    text_splitter = make_text_splitter(splitter_name=splitter_name,
                                       chunk_size=chunk_size,
                                       chunk_overlap=chunk_overlap)
    splitted_docs = text_splitter.split_documents(docs)
    
    # 将切分好的文档放入临时向量库，重新筛选出TOP_K个文档
    if len(splitted_docs) > result_len:
        vs = memo_faiss_pool.new_vector_store()
        vs.add_documents(splitted_docs)
        splitted_docs = vs.similarity_search(text, k=result_len, score_threshold=1.0)

    docs = [{"snippet": x.page_content,
             "link": x.metadata["link"],
             "title": x.metadata["title"]}
             for x in splitted_docs]
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


async def lookup_search_engine(
        query: str,
        search_engine_name: str,
        top_k: int = SEARCH_ENGINE_TOP_K,
):
    search_engine = SEARCH_ENGINES[search_engine_name]
    results = await run_in_threadpool(search_engine, query, result_len=top_k)
    docs = search_result2docs(results)
    return docs


async def search_engine_chat(query: str = Body(..., description="用户输入", examples=["你好"]),
                            search_engine_name: str = Body(..., description="搜索引擎名称", examples=["duckduckgo"]),
                            top_k: int = Body(SEARCH_ENGINE_TOP_K, description="检索结果数量"),
                            history: List[History] = Body([],
                                                            description="历史对话",
                                                            examples=[[
                                                                {"role": "user",
                                                                "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                                {"role": "assistant",
                                                                "content": "虎头虎脑"}]]
                                                            ),
                            stream: bool = Body(False, description="流式输出"),
                            model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
                            temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                            max_tokens: int = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
                            prompt_name: str = Body("default",description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                       ):
    if search_engine_name not in SEARCH_ENGINES.keys():
        return BaseResponse(code=404, msg=f"未支持搜索引擎 {search_engine_name}")

    if search_engine_name == "bing" and not BING_SUBSCRIPTION_KEY:
        return BaseResponse(code=404, msg=f"要使用Bing搜索引擎，需要设置 `BING_SUBSCRIPTION_KEY`")

    history = [History.from_data(h) for h in history]

    async def search_engine_chat_iterator(query: str,
                                          search_engine_name: str,
                                          top_k: int,
                                          history: Optional[List[History]],
                                          model_name: str = LLM_MODEL,
                                          prompt_name: str = prompt_name,
                                          ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )

        docs = await lookup_search_engine(query, search_engine_name, top_k)
        context = "\n".join([doc.page_content for doc in docs])

        prompt_template = get_prompt_template("search_engine_chat", prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )

        source_documents = [
            f"""出处 [{inum + 1}] [{doc.metadata["source"]}]({doc.metadata["source"]}) \n\n{doc.page_content}\n\n"""
            for inum, doc in enumerate(docs)
        ]

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps({"answer": token}, ensure_ascii=False)
            yield json.dumps({"docs": source_documents}, ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer,
                              "docs": source_documents},
                             ensure_ascii=False)
        await task

    return StreamingResponse(search_engine_chat_iterator(query=query,
                                                         search_engine_name=search_engine_name,
                                                         top_k=top_k,
                                                         history=history,
                                                         model_name=model_name,
                                                         prompt_name=prompt_name),
                             media_type="text/event-stream")
