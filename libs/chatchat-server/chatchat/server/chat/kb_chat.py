from __future__ import annotations

import asyncio, json
import uuid
from typing import AsyncIterable, List, Optional, Literal

from fastapi import Body, Request
from fastapi.concurrency import run_in_threadpool
from sse_starlette.sse import EventSourceResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.prompts.chat import ChatPromptTemplate

from langchain_openai.chat_models import ChatOpenAI
from chatchat.settings import Settings
from chatchat.server.agent.tools_factory.search_internet import search_engine
from chatchat.server.api_server.api_schemas import OpenAIChatOutput
from chatchat.server.chat.utils import History
from chatchat.server.knowledge_base.kb_service.base import KBServiceFactory
from chatchat.server.knowledge_base.kb_doc_api import search_docs, search_temp_docs
from chatchat.server.knowledge_base.utils import format_reference
from chatchat.server.utils import (wrap_done, get_ChatOpenAI, get_default_llm,
                                   BaseResponse, get_prompt_template, build_logger,
                                   check_embed_model, api_address
                                )


logger = build_logger()


async def adaptive_docs(
        docs:List[str],
        model:str,
        temperature:float,
        max_tokens:int,
        query:str,
        lang="zh",
                  ):
    """
    select related documents to send to LLM by self-criticize
    source_documents: list of documents
    llm: LLM model
    query: user query
    lang: language, "zh" or "en"

    """
    llm = get_ChatOpenAI(
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens,

            )
    prompt_en = (
                "You’ll be provided with an instruction, along with evidence and possibly some preceding"
                "sentences. When there are preceding sentences, your focus should be on the sentence that"
                "comes after them. Your job is to determine if the evidence is relevant to the initial instruction"
                "and the preceding context, and provides useful information to complete the task described in"
                "the instruction. If the evidence meets this requirement, respond with [Relevant]; otherwise,"
                "generate [Irrelevant]. Here's two examples to help you understand the task better:\n\n"
                "Example 1:\n\n"
                "Instruction: Given four answer options, A, B, C, and D, choose the best answer."
                "Input Earth’s rotating causes"
                "A: the cycling of AM and PM"
                "B: the creation of volcanic eruptions"
                "C: the cycling of the tides"
                "D: the creation of gravity"
                "Evidence: Rotation causes the day-night cycle which also creates a corresponding cycle of"
                "temperature and humidity creates a corresponding cycle of temperature and humidity. Sea"
                "level rises and falls twice a day as the earth rotates."
                "**Rating** [Relevant]"
                "Explanation: The evidence explicitly mentions that the rotation causes a day-night cycle, as"
                "described in the answer option A."
                "Example 2:\n\n"
                "Instruction: age to run for US House of Representatives"
                "Evidence: The Constitution sets three qualifications for service in the U.S. Senate: age (at"
                "least thirty years of age); U.S. citizenship (at least nine years); and residency in the state a"
                "senator represents at the time of election."
                "**Rating** [Irrelevant]"
                "Explanation: The evidence only discusses the ages to run for the US Senate, not for the"
                "House of Representatives."
                "Examples completed.\n\n"
                "Please provide your response to the evidence in the following format: [Relevant] or [Irrelevant]."
                "Instruction: {}"
                "Evidence: {}"
                "Rating: "
                )
    prompt_zh = (
                "你将会收到一个指令，以及证据和可能的一些前述句子。当有前述句子时，你的重点应该放在它们之后的句子上。"
                "你的任务是判断证据是否与最初的指令和前述的上下文相关，并提供有用的信息来完成指令中描述的任务。"
                "如果证据符合这个要求，请回复[相关]；否则，请生成[不相关]。以下是两个示例，帮助你更好地理解任务："
                "示例1："
                "指令：在四个答案选项A、B、C和D中，选择最佳答案。"
                "输入：地球的旋转导致"
                "A: AM和PM的循环"
                "B: 火山喷发的形成"
                "C: 潮汐的循环"
                "D: 重力的形成"
                "证据：旋转导致昼夜循环，这也会产生相应的温度和湿度循环。随着地球的旋转，海平面每天上升和下降两次。"
                "**评级** [相关]"
                "解释：证据明确提到旋转导致昼夜循环，如答案选项A所述。"
                "示例2："
                "指令：竞选美国众议院的年龄"
                "证据：宪法为在美国参议院服务设定了三个资格：年龄（至少三十岁）；美国公民身份（至少九年）；以及在选举时参议员代表的州的居住权。"
                "**评级** [不相关]"
                "解释：证据只讨论了竞选美国参议院的年龄，而不是众议院。"
                "示例完成。"
                "请按照以下格式提供你对证据的回应：[相关]或[不相关]。直接输出评级，不要添加任何内容！"
                "指令：{}"
                "证据：{}"
                "评级："
                )
    prompt = prompt_zh if lang == "zh" else prompt_en
    prompts = [prompt.format(query, doc['page_content']) for doc in docs]
    # parallel generation with async
    messages = [[("human",prompt)] for prompt in prompts]

    results = await llm.abatch(messages)
    results_key = [result.content for result in results]

    filter_word = "不相关" if lang == "zh" else "Irrelevant"
    relevance = [0 if result.endswith(filter_word) else 1 for result in results_key]
    relevance_idx = [i for i, r in enumerate(relevance) if r == 1]
    docs_adaptive = [docs[i] for i in relevance_idx]
    return docs_adaptive
    

async def kb_chat(query: str = Body(..., description="用户输入", examples=["你好"]),
                mode: Literal["local_kb", "temp_kb", "search_engine"] = Body("local_kb", description="知识来源"),
                kb_name: str = Body("", description="mode=local_kb时为知识库名称；temp_kb时为临时知识库ID，search_engine时为搜索引擎名称", examples=["samples"]),
                top_k: int = Body(Settings.kb_settings.VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                score_threshold: float = Body(
                    Settings.kb_settings.SCORE_THRESHOLD,
                    description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
                    ge=0,
                    le=2,
                ),
                history: List[History] = Body(
                    [],
                    description="历史对话",
                    examples=[[
                        {"role": "user",
                        "content": "我们来玩成语接龙，我先来，生龙活虎"},
                        {"role": "assistant",
                        "content": "虎头虎脑"}]]
                ),
                stream: bool = Body(True, description="流式输出"),
                model: str = Body(get_default_llm(), description="LLM 模型名称。"),
                temperature: float = Body(Settings.model_settings.TEMPERATURE, description="LLM 采样温度", ge=0.0, le=2.0),
                max_tokens: Optional[int] = Body(
                    Settings.model_settings.MAX_TOKENS,
                    description="限制LLM生成Token数量，默认None代表模型最大值"
                ),
                prompt_name: str = Body(
                    "default",
                    description="使用的prompt模板名称(在prompt_settings.yaml中配置)"
                ),
                return_direct: bool = Body(False, description="直接返回检索结果，不送入 LLM"),
                request: Request = None,
                ):
    if mode == "local_kb":
        kb = KBServiceFactory.get_service_by_name(kb_name)
        if kb is None:
            return BaseResponse(code=404, msg=f"未找到知识库 {kb_name}")
    
    async def knowledge_base_chat_iterator() -> AsyncIterable[str]:
        try:
            nonlocal history, prompt_name, max_tokens

            history = [History.from_data(h) for h in history]

            if mode == "local_kb":
                kb = KBServiceFactory.get_service_by_name(kb_name)
                ok, msg = kb.check_embed_model()
                if not ok:
                    raise ValueError(msg)
                docs = await run_in_threadpool(search_docs,
                                                query=query,
                                                knowledge_base_name=kb_name,
                                                top_k=top_k,
                                                score_threshold=score_threshold,
                                                file_name="",
                                                metadata={})
                # source_documents = format_reference(kb_name, docs, api_address(is_public=True))
                doc_source = "kb"
            elif mode == "temp_kb":
                ok, msg = check_embed_model()
                if not ok:
                    raise ValueError(msg)
                docs = await run_in_threadpool(search_temp_docs,
                                                kb_name,
                                                query=query,
                                                top_k=top_k,
                                                score_threshold=score_threshold)
                doc_source = "kb"
                # source_documents = format_reference(kb_name, docs, api_address(is_public=True))
            elif mode == "search_engine":
                result = await run_in_threadpool(search_engine, query, top_k, kb_name)
                docs = [x.dict() for x in result.get("docs", [])]
                # source_documents = [
                #         f"""出处 [{i + 1}] [{d['metadata']['filename']}]({d['metadata']['source']}) \n\n{d['page_content']}\n\n""" 
                #                         for i,d in enumerate(docs)
                #                         ]
                doc_source = "se"
            else:
                logger.warning(f"mode {mode} not supported")
                docs = []
                source_documents = []
            # import rich
            # rich.print(dict(
            #     mode=mode,
            #     query=query,
            #     knowledge_base_name=kb_name,
            #     top_k=top_k,
            #     score_threshold=score_threshold,
            # ))
            # rich.print(docs)
            if return_direct:
                yield OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    model=None,
                    object="chat.completion",
                    content="",
                    role="assistant",
                    finish_reason="stop",
                    docs=source_documents,
                ) .model_dump_json()
                return

            callback = AsyncIteratorCallbackHandler()
            callbacks = [callback]

            # Enable langchain-chatchat to support langfuse
            import os
            langfuse_secret_key = os.environ.get('LANGFUSE_SECRET_KEY')
            langfuse_public_key = os.environ.get('LANGFUSE_PUBLIC_KEY')
            langfuse_host = os.environ.get('LANGFUSE_HOST')
            if langfuse_secret_key and langfuse_public_key and langfuse_host :
                from langfuse import Langfuse
                from langfuse.callback import CallbackHandler
                langfuse_handler = CallbackHandler()
                callbacks.append(langfuse_handler)

            if max_tokens in [None, 0]:
                max_tokens = Settings.model_settings.MAX_TOKENS


            # TODO： 视情况使用 API
            # # 加入reranker
            # * -----------------add reranker---------------------------- 
            if Settings.model_settings.USE_RERANKER:
                from chatchat.server.reranker.reranker import reranker_docs
                docs = await reranker_docs(query, docs, top_k)
            if Settings.kb_settings.ADAPTIVE_DOCUMENTS:
                docs = await adaptive_docs(
                                        docs, 
                                        model=model,
                                        temperature=temperature,
                                        max_tokens=max_tokens,
                                        query=query,
                                        lang='zh'
                                        )

            source_documents = format_reference(kb_name, 
                                                docs, 
                                                api_address(is_public=True), 
                                                doc_source=doc_source)
            context = "\n\n".join([doc["page_content"] for doc in docs])

            if len(docs) == 0:  # 如果没有找到相关文档，使用empty模板
                prompt_name = "empty"
            prompt_template = get_prompt_template("rag", prompt_name)
            input_msg = History(role="user", content=prompt_template).to_msg_template(False)
            chat_prompt = ChatPromptTemplate.from_messages(
                [i.to_msg_template() for i in history] + [input_msg])
            llm = get_ChatOpenAI(
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=callbacks,
            )
            chain = chat_prompt | llm

            # Begin a task that runs in the background.
            task = asyncio.create_task(wrap_done(
                chain.ainvoke({"context": context, "question": query}),
                callback.done),
            )

            if len(source_documents) == 0:  # 没有找到相关文档
                source_documents.append(f"<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>")

            if stream:
                # yield documents first
                ret = OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    object="chat.completion.chunk",
                    content="",
                    role="assistant",
                    model=model,
                    docs=source_documents,
                )
                yield ret.model_dump_json()

                async for token in callback.aiter():
                    ret = OpenAIChatOutput(
                        id=f"chat{uuid.uuid4()}",
                        object="chat.completion.chunk",
                        content=token,
                        role="assistant",
                        model=model,
                    )
                    yield ret.model_dump_json()
            else:
                answer = ""
                async for token in callback.aiter():
                    answer += token
                ret = OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    object="chat.completion",
                    content=answer,
                    role="assistant",
                    model=model,
                )
                yield ret.model_dump_json()
            await task
        except asyncio.exceptions.CancelledError:
            logger.warning("streaming progress has been interrupted by user.")
            return
        except Exception as e:
            logger.error(f"error in knowledge chat: {e}")
            yield {"data": json.dumps({"error": str(e)})}
            return

    if stream:
        return EventSourceResponse(knowledge_base_chat_iterator())
    else:
        return await knowledge_base_chat_iterator().__anext__()
