from langchain.document_loaders.github import GitHubIssuesLoader
from fastapi import Body
from fastapi.responses import StreamingResponse
from configs.model_config import (llm_model_dict, LLM_MODEL, SEARCH_ENGINE_TOP_K, PROMPT_TEMPLATE)
from server.chat.utils import wrap_done
from server.utils import BaseResponse
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List, Optional, Literal
from server.chat.utils import History
from langchain.docstore.document import Document
import json
import os
from functools import lru_cache
from datetime import datetime


GITHUB_PERSONAL_ACCESS_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")


@lru_cache(1)
def load_issues(tick: str):
    '''
    set tick to a periodic value to refresh cache
    '''
    loader = GitHubIssuesLoader(
        repo="chatchat-space/langchain-chatglm",
        access_token=GITHUB_PERSONAL_ACCESS_TOKEN,
        include_prs=True,
        state="all",
    )
    docs = loader.load()
    return docs


def 
def github_chat(query: str = Body(..., description="用户输入", examples=["本项目最新进展"]),
                top_k: int = Body(SEARCH_ENGINE_TOP_K, description="检索结果数量"),
                include_prs: bool = Body(True, description="是否包含PR"),
                state: Literal['open', 'closed', 'all'] = Body(None, description="Issue/PR状态"),
                creator: str = Body(None, description="创建者"),
                history: List[History] = Body([],
                                            description="历史对话",
                                            examples=[[
                                                {"role": "user",
                                                "content": "介绍一下本项目"},
                                                {"role": "assistant",
                                                "content": "LangChain-Chatchat (原 Langchain-ChatGLM): 基于 Langchain 与 ChatGLM 等大语言模型的本地知识库问答应用实现。"}]]
                                                ),
                stream: bool = Body(False, description="流式输出"),
                ):
    if GITHUB_PERSONAL_ACCESS_TOKEN is None:
        return BaseResponse(code=404, msg=f"使用本功能需要 GITHUB_PERSONAL_ACCESS_TOKEN")

    async def chat_iterator(query: str,
                            search_engine_name: str,
                            top_k: int,
                            history: Optional[List[History]],
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

        docs = lookup_search_engine(query, search_engine_name, top_k)
        context = "\n".join([doc.page_content for doc in docs])

        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_tuple() for i in history] + [("human", PROMPT_TEMPLATE)])

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
                yield json.dumps({"answer": token,
                                  "docs": source_documents},
                                 ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": token,
                              "docs": source_documents},
                             ensure_ascii=False)
        await task

    return StreamingResponse(search_engine_chat_iterator(query, search_engine_name, top_k, history),
                             media_type="text/event-stream")
