from langchain.utilities import BingSearchAPIWrapper
from configs.model_config import BING_SEARCH_URL, BING_SUBSCRIPTION_KEY
from fastapi import Body
from fastapi.responses import StreamingResponse
from configs.model_config import (llm_model_dict, LLM_MODEL, PROMPT_TEMPLATE)
from server.chat.utils import wrap_done
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

def bing_search(text, result_len=3):
    if not (BING_SEARCH_URL and BING_SUBSCRIPTION_KEY):
        return [{"snippet": "please set BING_SUBSCRIPTION_KEY and BING_SEARCH_URL in os ENV",
                 "title": "env info is not found",
                 "link": "https://python.langchain.com/en/latest/modules/agents/tools/examples/bing_search.html"}]
    search = BingSearchAPIWrapper(bing_subscription_key=BING_SUBSCRIPTION_KEY,
                                  bing_search_url=BING_SEARCH_URL)
    return search.results(text, result_len)


def search_result2docs(search_results):
    docs = []
    for result in search_results:
        doc = Document(page_content=result["snippet"] if "snippet" in result.keys() else "",
                       metadata={"source": result["link"] if "link" in result.keys() else "",
                                 "filename": result["title"] if "title" in result.keys() else ""})
        docs.append(doc)
    return docs


def bing_search_chat(query: str = Body(..., description="用户输入", example="你好"),
              ):
    async def bing_search_chat_iterator(query: str,
                                 ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        model = ChatOpenAI(
            streaming=True,
            verbose=True,
            callbacks=[callback],
            openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
            openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
            model_name=LLM_MODEL
        )

        results = bing_search(query, result_len=3)
        docs = search_result2docs(results)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])

        chain = LLMChain(prompt=prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )

        async for token in callback.aiter():
            # Use server-sent-events to stream the response
            yield token
        await task

    return StreamingResponse(bing_search_chat_iterator(query), media_type="text/event-stream")
