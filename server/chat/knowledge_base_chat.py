from fastapi import Body
from fastapi.responses import StreamingResponse
from configs.model_config import (llm_model_dict, LLM_MODEL, PROMPT_TEMPLATE,
                                  CACHED_VS_NUM, VECTOR_SEARCH_TOP_K,
                                  embedding_model_dict, EMBEDDING_MODEL, EMBEDDING_DEVICE)
from server.chat.utils import wrap_done
from server.utils import BaseResponse
import os
from server.knowledge_base.utils import get_kb_path
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from server.knowledge_base.utils import get_vs_path
from functools import lru_cache


@lru_cache(1)
def load_embeddings(model: str, device: str):
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[model],
                                       model_kwargs={'device': device})
    return embeddings


@lru_cache(CACHED_VS_NUM)
def load_vector_store(
        knowledge_base_name: str,
        embedding_model: str,
        embedding_device: str,
):
    embeddings = load_embeddings(embedding_model, embedding_device)
    vs_path = get_vs_path(knowledge_base_name)
    search_index = FAISS.load_local(vs_path, embeddings)
    return search_index


def lookup_vs(
        query: str,
        knowledge_base_name: str,
        top_k: int = VECTOR_SEARCH_TOP_K,
        embedding_model: str = EMBEDDING_MODEL,
        embedding_device: str = EMBEDDING_DEVICE,
):
    search_index = load_vector_store(knowledge_base_name, embedding_model, embedding_device)
    docs = search_index.similarity_search(query, k=top_k)
    return docs


def knowledge_base_chat(query: str = Body(..., description="用户输入", example="你好"),
                        knowledge_base_name: str = Body(..., description="知识库名称", example="samples"),
                        top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                        ):
    kb_path = get_kb_path(knowledge_base_name)
    if not os.path.exists(kb_path):
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    async def knowledge_base_chat_iterator(query: str,
                                           knowledge_base_name: str,
                                           top_k: int,
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
        docs = lookup_vs(query, knowledge_base_name, top_k)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])

        chain = LLMChain(prompt=prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )

        source_documents = [
            f"""出处 [{inum + 1}] [{doc.metadata["source"]}]({doc.metadata["source"]}) \n\n{doc.page_content}\n\n"""
            for inum, doc in enumerate(docs)
        ]

        async for token in callback.aiter():
            # Use server-sent-events to stream the response
            yield {"answer": token,
                   "docs": source_documents}
        await task

    return StreamingResponse(knowledge_base_chat_iterator(query, knowledge_base_name, top_k),
                             media_type="text/event-stream")
