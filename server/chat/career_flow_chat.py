from fastapi import Body, Request
from sse_starlette.sse import EventSourceResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from configs import (LLM_MODELS, 
                     VECTOR_SEARCH_TOP_K, 
                     SCORE_THRESHOLD, 
                     TEMPERATURE,
                     USE_RERANKER,
                     RERANKER_MODEL,
                     RERANKER_MAX_LENGTH,
                     MODEL_PATH,
                     MERGED_MAX_DOCS_NUM)
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
from langchain.chains import LLMChain
# from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable, List, Optional
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from server.chat.utils import History
from server.knowledge_base.kb_service.base import KBServiceFactory
import json
from urllib.parse import urlencode
from server.knowledge_base.kb_doc_api import search_docs
from server.reranker.reranker import LangchainReranker
from server.utils import embedding_device

import time
from langchain.schema import BaseOutputParser
import pandas as pd
import random
import aiohttp
import os 

role_definition = """
角色：
试界教育的一名高中生涯辅导老师，为高中生做生涯探索辅导。可以为学生提供各个学科，专业方向的指导。
背景：
中国的高中生们普遍缺乏对于职业生涯发展的探索。你作为知名的生涯辅导老师，有义务和能力改变他们的认知，让他们以轻松，非常深入浅出的方式获取各种职业学科的相关知识。
目标：
1、以专业且善解人意的态度，让高中生对了解一个职业或学科。
2、每个学生的信息都不相同，如果回答的问题需要学生的信息(比如省份，成绩等)，发问让他回答。
限制：
用亲切的语气回答，回答尽量详细。
不要出现“指令”，“已知信息”等内容。
不要描述自己的语言风格等内容。
注意：
已知信息里出现的内容都是第三方资料，不是当前学生的资料。
"""

truth_template = """<指令>
1、优先从已知信息提取答案。如果无法从已知信息中得到答案，直接说自己暂时不知道这个问题的答案
2、回答尽量详细，不要出现“角色”，“指令”内的内容。</指令>
<已知信息>{{ context }}</已知信息>
<学生问题>{{ question }}</学生问题>
注意：
0、直接说出回答，不要出现<角色>，<指令>的内容。
1、已知信息的内容里的内容不是当前咨询者的信息，是第三方资料。     
2、不允许说自己是大语言模型，以生涯老师的角度回答问题    。
3、不允许和历史回答一模一样。"""

opinion_template = """<指令>
1、优先从已知信息提取答案。如果无法从已知信息中得到答案，直接说自己暂时不知道这个问题的答案。
2、回答尽量详细，要以客观中立的态度，在回答中以“正面”和”反面“两个方面进行回答，最后附上总结。
3、不要出现“角色”，“指令”内的内容。如果回答的问题需要学生的信息(比如省份，成绩等)，发问让他回答</指令>
<已知信息>{{ context }}</已知信息>
<学生问题>{{ question }}</学生问题>
注意：
0、直接说出回答，不要出现<角色>，<指令>的内容。
1、已知信息的内容里的内容不是当前咨询者的信息，是第三方资料。
2、不允许说自己是大语言模型，以生涯老师的角度回答问题。
3、不允许和历史回答一模一样。"""

chat_template = """<角色>你是试界教育的一个高中生涯教育老师，可以为学生提供各个学科，专业方向的指导。不允许说自己是大语言模型</角色>
<限制>只能说自己是个高中生涯教育老师。不要描述自己。如果回答的问题需要学生的信息(比如省份，成绩等)，发问让他回答</限制>
<聊天历史>{{ history }}</聊天历史>
<学生问题>{{ question }}</学生问题>
根据聊天历史和自己的知识进行回答，不许说自己是大语言模型，以生涯老师的角度回答问题"""

def blocked_words_check(query):
    """遍历敏感词表

    Args:
        query (str): 用户输入的query

    Returns:
        should_be_blocked: Boolean, True代表需要被屏蔽
        searched_bad_word: str, 屏蔽词
    """
    # 是否该被屏蔽
    should_be_blocked = False
    # 搜索到的屏蔽词
    searched_bad_word = ""
    for bad_word in bad_words:
        if bad_word in query:
            should_be_blocked = True
            searched_bad_word = bad_word
            break
    return should_be_blocked, searched_bad_word

def history_reformat(h) -> {}:
    """防止传入的history有问题，主要是针对UI交互的场景

    Returns:
        _type_: _description_
    """
    res = {"role": h.role, "content": h.content}
    return res

# 敏感词
bad_words = [t.strip() for t in open("./server/chat/badwords.txt").readlines()]

# 读取'热门问题排查.csv', sep=',', encoding='utf-8'
df = pd.read_csv('./server/chat/热门问题排查.csv', sep=',', encoding='utf-8')

# 将df转为dict, key是专业名，value是问题列表
major2ques = {}
for index,row in df.iterrows():
    if row['专业名'] not in major2ques:
        major2ques[row['专业名']] = []
    major2ques[row['专业名']].append(row['问题'])

# 随机选取三个元素
def random_select_3(list, element):
    import random
    temp = list.copy()
    if element in temp:
        temp.remove(element)
    return random.sample(temp, 3)

import asyncio
from typing import Any, AsyncIterator, Dict, List, Literal, Union, cast

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema.output import LLMResult

# TODO If used by two LLM runs in parallel this won't work as expected

def token_check(token):
    for t in bad_words:
        if t in token:
            return True
    return False

def docs_merge_strategy(kb_docs, search_engine_docs, knowledge_base_name, request):
    final_docs = []
    source_documents = []
    if len(kb_docs) == 0:
        final_docs = search_engine_docs
        for inum, doc in enumerate(search_engine_docs):
            text = {
                    "type": "search",
                    "index_title": "搜索出处" + str([inum + 1]),
                    "source_title": doc.metadata["filename"].replace('<b>','').replace('</b>',''),
                    "source_url": doc.metadata["source"],
                    "content": doc.page_content.replace("@@@@@@@@@@", "")
                }
            source_documents.append(text)
    else:
        final_docs.extend(kb_docs)
        for inum, doc in enumerate(kb_docs):
            filename = os.path.split(doc.metadata["source"])[-1]
            parameters = urlencode(
                {"knowledge_base_name": knowledge_base_name, "file_name": filename}
            )
            url = f"{request.base_url}knowledge_base/download_doc?" + parameters
            text = {
                    "type": "kb",
                    "index_title": "知识库出处" + str([inum + 1]),
                    "source_title": filename.replace('.txt',''),
                    "match_score": str(1-doc.score)[:5],
                    "content": doc.page_content.replace("@@@@@@@@@@", "")
            }
            source_documents.append(text)
        if len(kb_docs) < MERGED_MAX_DOCS_NUM:
            supplement_num = MERGED_MAX_DOCS_NUM - len(kb_docs)
            search_engine_docs = search_engine_docs[:supplement_num]
            final_docs.extend(search_engine_docs)
            for inum, doc in enumerate(search_engine_docs):
                text = {
                        "type": "search",
                        "index_title": "搜索出处" + str([inum + 1]),
                        "source_title": doc.metadata["filename"].replace('<b>','').replace('</b>',''),
                        "source_url": doc.metadata["source"],
                        "content": doc.page_content.replace("@@@@@@@@@@", "")
                    }
                source_documents.append(text)
    return final_docs, source_documents

def question_type_judge(text, docs_len):
    print("模型对query的判断是", text)
    # 原始query既搜不到 也被判定成闲聊，才算闲聊
    if "闲聊" in text and docs_len == 0:
        return "闲聊"
    else:
        return "相关"

# bert判断问题是否是闲聊
async def get_idle_res(query):
    url = "http://127.0.0.1:7861/chat/bert_chat_judge"  # 你的目标 URL
    payload = query
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            return await response.text()

# 判断是否是事实型
async def get_truth_res(query):
    url = "http://127.0.0.1:7861/chat/bert_truth_judge"  # 你的目标 URL
    payload = query
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            return await response.text()
        


class AsyncIteratorCallbackHandler(AsyncCallbackHandler):

    """Callback handler that returns an async iterator."""

    queue: asyncio.Queue[str]

    done: asyncio.Event

    @property
    def always_verbose(self) -> bool:
        return True

    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()
        # 是否有敏感词
        self.llm_status = 0
        # 是否生成结束
        self.llm_is_generating = 0
        self.generate_length  = 0
        self.t0 = time.time()
        self.t1 = ''

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        # If two calls are made in a row, this resets the state
        print("llm start")
        self.generate_length = 0
        self.done.clear()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # print("生成token",token)
        stop_signal = token_check(token)
        if token is not None and token != "" and (not stop_signal):
            self.generate_length += len(token)
            self.queue.put_nowait(token)
        else:
            if len(token) > 0 and stop_signal:
                self.llm_status = 1
                print("存在敏感词",token,"修改llmstatus",self.llm_status)
                self.queue.put_nowait(token)
                # self.queue.put_nowait("########")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.llm_is_generating = 1
        print("模型生成结束",self.llm_is_generating)
        self.t1 = time.time()
        print('大模型共生成：', self.generate_length , 'token','，花费时间', round(self.t1 - self.t0, 2), 's', '生成速度',self.generate_length/(self.t1 - self.t0),'token/s')
        print("llm finished")
        self.done.set()


    async def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        self.done.set()
        print("llm error")

    # TODO implement the other methods

    async def aiter(self) -> AsyncIterator[str]:
        while not self.queue.empty() or not self.done.is_set():
            # Wait for the next token in the queue,
            # but stop waiting if the done event is set
            done, other = await asyncio.wait(
                [
                    # NOTE: If you add other tasks here, update the code below,
                    # which assumes each set has exactly one task each
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel the other task
            if other:
                other.pop().cancel()

            # Extract the value of the first completed task
            token_or_done = cast(Union[str, Literal[True]], done.pop().result())

            # If the extracted value is the boolean True, the done event was set
            if token_or_done is True:
                break

            # Otherwise, the extracted value is a token, which we yield
            yield token_or_done
            
            
class CleanupOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        for t in bad_words:
            if t in text:
                print(t)
                # text = re.sub(t, "########", text)
        # print(text)
        return text

    @property
    def _type(self) -> str:
        return "output_parser"


parser = CleanupOutputParser()



async def career_flow_chat(query: str = Body(..., description="用户输入", examples=["你好"]),
                              knowledge_base_name: str = Body(..., description="知识库名称", examples=["samples"]),
                              top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                              score_threshold: float = Body(
                                  SCORE_THRESHOLD,
                                  description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
                                  ge=0,
                                  le=2
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
                              stream: bool = Body(False, description="流式输出"),
                              model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
                              temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                              max_tokens: Optional[int] = Body(
                                  None,
                                  description="限制LLM生成Token数量，默认None代表模型最大值"
                              ),
                              prompt_name: str = Body(
                                  "default",
                                  description="使用的prompt模板名称(在configs/prompt_config.py中配置)"
                              ),
                              request: Request = None,
                              ):
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    # 计时
    t0 = time.time()
    
    # 知识库文档合集
    kb_docs = []
    # 搜索引擎文档合集
    searchengine_docs = []
    # 最终文档合集
    final_docs = []

    # 返回模版
    ret = {"answer": "暂时无法回答该问题", "docs": "", "question_type": ""}
    
    # 判断query是不是当前的专业
    # knowledge_base_name =  kb_name_check(query, knowledge_base_name)
    # print("最终查询的专业是",knowledge_base_name)

    # 前处理，如果query里包含就直接结束
    check_res, blocked_word = blocked_words_check(query)
    if check_res:
        ret["answer"] = "不好意思，该问题无法回答，因为该问题中包含屏蔽词: " + blocked_word + "，请换一个问题"
        return JSONResponse(ret)


    final_history = []
    if len(history) > 0:
        if type(history[0]) == History:
            final_history = [history_reformat(t) for t in history]
        else:
            final_history = history
    else:
        final_history = history

    # 增加角色定义
    prefix_history = [{"role": "system", "content": role_definition}]

    if prefix_history[0] not in final_history:
        final_history = prefix_history + final_history
        

    # step1 判断是哪种类型的问题
    judge_text = await get_idle_res(query)
    print("bert模型回答", judge_text)
    t1 = time.time()
    print("大模型意图判断响应耗时为：", round(t1 - t0, 2), "s", "总共时间", round(t1 - t0, 2), "s")

    # step2 在知识库里搜索
    kb_docs = search_docs(query, knowledge_base_name, top_k, score_threshold)
    docs_len = len(kb_docs)
    print("知识库搜索query", query)
    print("原始query在知识库的搜索结果共n篇", docs_len)

    t2 = time.time()
    print("知识库搜索耗时为：", round(t2 - t1, 2), "s", "总共时间", round(t2 - t0, 2), "s")

    question_type = question_type_judge(judge_text, docs_len)
    print("生涯相关性判断为,", question_type)
    print("第一阶段响应耗时为：", round(time.time() - t0, 2), "s")

    t_extra = ""

    if question_type != "闲聊":
        question_type = await get_truth_res(query)
        print("最终判断问题类型为", question_type)
        t_extra = time.time()
        print(
            "事实观点判断耗时为：",
            round(t_extra - t2, 2),
            "s",
            "总共时间",
            round(t_extra - t0, 2),
            "s",
        )
        
        # 搜索引擎搜索docs
        search_query = (
            query if knowledge_base_name in query else knowledge_base_name + "的" + query
        )
        if len(kb_docs) < MERGED_MAX_DOCS_NUM:
            try:
                searchengine_docs = lookup_search_engine(
                    search_query, "bing", MERGED_MAX_DOCS_NUM - docs_len
                )
            except:
                searchengine_docs = []
            print("搜索库共n篇", len(searchengine_docs))

        final_docs, source_documents = docs_merge_strategy(
            kb_docs, searchengine_docs, knowledge_base_name, request
        )

        # 逆反搜索结果，越重要的越靠近问题
        final_docs.reverse()

        # 模型最终看到的上下文
        max_single_content_length = 800
        context = "\n".join([doc.page_content[:max_single_content_length] for doc in final_docs]).replace(
            "@@@@@@@@@@\n", ""
        )
        
        print("未裁剪前context",len(context))
        
        # 如果context长度过长，只取前4096，因为是baichuan的限制
        # if len(context)>=4096:
        #     context = context[:4096]
        
        # print("最终context",context)

    t3 = time.time()
    if len(searchengine_docs) > 0:
        print("搜索引擎搜索耗时为：", round(t3 - t_extra, 2), "s", "总共时间", round(t3 - t0, 2), "s")

    print("前处理流程结束，共耗时", round(t3 - t0, 2), "s")

    text = ""
    if question_type == "闲聊":
        used_template = chat_template
        context = ""
        source_documents = ""
        # 只有闲聊才允许看历史记录
        history = [History.from_data(h) for h in final_history]
    else:
        history = []
        if question_type == "事实":
            used_template = truth_template
        else:
            used_template = opinion_template


    async def knowledge_base_chat_iterator(
            query: str,
            top_k: int,
            history: Optional[List[History]],
            model_name: str = model_name,
            prompt_name: str = prompt_name,
    ) -> AsyncIterable[str]:
        nonlocal max_tokens
        callback = AsyncIteratorCallbackHandler()
        if isinstance(max_tokens, int) and max_tokens <= 0:
            max_tokens = None

        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )
        docs = await run_in_threadpool(search_docs,
                                       query=query,
                                       knowledge_base_name=knowledge_base_name,
                                       top_k=top_k,
                                       score_threshold=score_threshold)

        # 加入reranker
        if USE_RERANKER:
            reranker_model_path = MODEL_PATH["reranker"].get(RERANKER_MODEL,"BAAI/bge-reranker-large")
            print("-----------------model path------------------")
            print(reranker_model_path)
            reranker_model = LangchainReranker(top_n=top_k,
                                            device=embedding_device(),
                                            max_length=RERANKER_MAX_LENGTH,
                                            model_name_or_path=reranker_model_path
                                            )
            print(docs)
            docs = reranker_model.compress_documents(documents=docs,
                                                     query=query)
            print("---------after rerank------------------")
            print(docs)
        context = "\n".join([doc.page_content for doc in docs])

        if len(docs) == 0:  # 如果没有找到相关文档，使用empty模板
            prompt_template = get_prompt_template("knowledge_base_chat", "empty")
        else:
            prompt_template = get_prompt_template("knowledge_base_chat", prompt_name)
            
        
        input_msg = History(role="user", content=used_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )

        # source_documents = []
        # for inum, doc in enumerate(docs):
        #     filename = doc.metadata.get("source")
        #     parameters = urlencode({"knowledge_base_name": knowledge_base_name, "file_name": filename})
        #     base_url = request.base_url
        #     url = f"{base_url}knowledge_base/download_doc?" + parameters
        #     text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
        #     source_documents.append(text)

        # if len(source_documents) == 0:  # 没有找到相关文档
        #     source_documents.append(f"<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>")

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield 'event:' + str(callback.llm_is_generating) + '\n'
                yield 'data: '+json.dumps({"answer": parser.parse(token), "force_stop_signal": callback.llm_status}, ensure_ascii=False)+'\n\n'
                # yield json.dumps({"answer": enforce_stop_tokens(token,bad_words)}, ensure_ascii=False)
            yield 'event:' + str(callback.llm_is_generating) + '\n'
            if knowledge_base_name != '合并类':
                suggest_list = random_select_3(major2ques[knowledge_base_name],query)
            else:
                suggest_list = []
            yield 'data: ' + json.dumps({"docs": source_documents, "recommend": suggest_list}, ensure_ascii=False) + '\n\n'
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer,
                              "docs": source_documents},
                             ensure_ascii=False)
        await task

    return EventSourceResponse(knowledge_base_chat_iterator(query, top_k, history,model_name,prompt_name))

