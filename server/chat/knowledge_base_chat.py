from fastapi import Body, Request
from fastapi.responses import StreamingResponse
from configs.model_config import (llm_model_dict, LLM_MODEL, PROMPT_TEMPLATE,
                                  VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, summarization_config, SUMMARIZATION_MODEL,
                                  SUMMARIZATION_TYPE)
from server.chat.utils import wrap_done
from server.utils import BaseResponse
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable, List, Optional
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from server.chat.utils import History
from server.knowledge_base.kb_service.base import KBService, KBServiceFactory
import json
import os
from urllib.parse import urlencode
from server.knowledge_base.kb_doc_api import search_docs
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate


def knowledge_base_chat(query: str = Body(..., description="用户输入", examples=["你好"]),
                        knowledge_base_name: str = Body(..., description="知识库名称", examples=["samples"]),
                        top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                        score_threshold: float = Body(SCORE_THRESHOLD,
                                                      description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
                                                      ge=0, le=1),
                        history: List[History] = Body([],
                                                      description="历史对话",
                                                      examples=[[
                                                          {"role": "user",
                                                           "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                          {"role": "assistant",
                                                           "content": "虎头虎脑"}]]
                                                      ),
                        stream: bool = Body(False, description="流式输出"),
                        local_doc_url: bool = Body(False, description="知识文件返回本地路径(true)或URL(false)"),
                        request: Request = None,
                        ):
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    history = [History.from_data(h) for h in history]

    async def knowledge_base_chat_iterator(query: str,
                                           kb: KBService,
                                           top_k: int,
                                           history: Optional[List[History]],
                                           ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        if LLM_MODEL == "Azure-OpenAI":
            model = AzureChatOpenAI(
                streaming=True,
                verbose=True,
                callbacks=[callback],
                openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
                openai_api_version=llm_model_dict[LLM_MODEL]["api_version"],
                deployment_name=llm_model_dict[LLM_MODEL]["deployment_name"],
                openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
                openai_api_type="azure",
            )
        elif LLM_MODEL == "OpenAI":
            model = ChatOpenAI(
                streaming=True,
                verbose=True,
                callbacks=[callback],
                openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
                openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
                model_name=llm_model_dict[LLM_MODEL]["model_name"]
            )
        else:
            model = ChatOpenAI(
                streaming=True,
                verbose=True,
                callbacks=[callback],
                openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
                openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
                model_name=LLM_MODEL
            )
        docs = search_docs(query, knowledge_base_name, top_k, score_threshold)

        if SUMMARIZATION_TYPE:
            if SUMMARIZATION_MODEL == "Azure-openai":
                model_summary = AzureChatOpenAI(
                    streaming=True,
                    verbose=True,
                    callbacks=[callback],
                    openai_api_base=llm_model_dict[SUMMARIZATION_MODEL]["api_base_url"],
                    openai_api_version=llm_model_dict[SUMMARIZATION_MODEL]["api_version"],
                    deployment_name=llm_model_dict[SUMMARIZATION_MODEL]["deployment_name"],
                    openai_api_key=llm_model_dict[SUMMARIZATION_MODEL]["api_key"],
                    openai_api_type="azure",
                )
            elif SUMMARIZATION_MODEL == "OpenAI":
                model = ChatOpenAI(
                    streaming=True,
                    verbose=True,
                    callbacks=[callback],
                    openai_api_key=llm_model_dict[LLM_MODEL]["api_key"],
                    openai_api_base=llm_model_dict[LLM_MODEL]["api_base_url"],
                    model_name=llm_model_dict[LLM_MODEL]["model_name"]
                )
            else:
                model_summary = ChatOpenAI(
                    streaming=False,
                    verbose=True,
                    temperature=0,
                    openai_api_key=llm_model_dict[SUMMARIZATION_MODEL]["api_key"],
                    openai_api_base=llm_model_dict[SUMMARIZATION_MODEL]["api_base_url"],
                    model_name=SUMMARIZATION_MODEL
                )
            if SUMMARIZATION_TYPE == "Stuff":
                stuff_chain = StuffDocumentsChain(llm=model_summary,
                                                  document_variable_name=summarization_config[SUMMARIZATION_MODEL][
                                                      "map_document_variable_name"])
                context = stuff_chain.run(docs)
            elif SUMMARIZATION_TYPE == "Map_Reduce":
                # Map
                map_template = summarization_config[SUMMARIZATION_TYPE]["map_prompt_template"]
                map_prompt = PromptTemplate.from_template(map_template)
                map_chain = LLMChain(llm=model_summary, prompt=map_prompt)

                # Reduce
                reduce_template = summarization_config[SUMMARIZATION_TYPE]["reduce_prompt_template"]
                reduce_prompt = PromptTemplate.from_template(reduce_template)
                reduce_chain = LLMChain(llm=model_summary, prompt=reduce_prompt)

                # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
                combine_documents_chain = StuffDocumentsChain(llm_chain=reduce_chain, document_variable_name=
                summarization_config[SUMMARIZATION_TYPE]["reduce_document_variable_name"])

                reduce_documents_chain = ReduceDocumentsChain(
                    combine_documents_chain=combine_documents_chain,
                    collapse_documents_chain=combine_documents_chain,
                    token_max=summarization_config[SUMMARIZATION_TYPE]["token_max"],
                )

                # Combining documents by mapping a chain over them, then combining results
                map_reduce_chain = MapReduceDocumentsChain(
                    llm_chain=map_chain,
                    reduce_documents_chain=reduce_documents_chain,
                    document_variable_name=summarization_config[SUMMARIZATION_TYPE]["map_document_variable_name"],
                    return_intermediate_steps=False)
                context = map_reduce_chain.run(docs)
            elif SUMMARIZATION_TYPE == "Refine":
                refine_chain = load_summarize_chain(model_summary, chain_type="refine")
                context = refine_chain.run(docs)
        else:
            context = "\n".join([doc.page_content for doc in docs])

        input_msg = History(role="user", content=PROMPT_TEMPLATE).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )

        source_documents = []
        for inum, doc in enumerate(docs):
            filename = os.path.split(doc.metadata["source"])[-1]
            if local_doc_url:
                url = "file://" + doc.metadata["source"]
            else:
                parameters = urlencode({"knowledge_base_name": knowledge_base_name, "file_name": filename})
                url = f"{request.base_url}knowledge_base/download_doc?" + parameters
            text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
            source_documents.append(text)

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
            yield json.dumps({"answer": answer,
                              "docs": source_documents},
                             ensure_ascii=False)

        await task

    return StreamingResponse(knowledge_base_chat_iterator(query, kb, top_k, history),
                             media_type="text/event-stream")
