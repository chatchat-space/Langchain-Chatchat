# 该文件包含webui通用工具，可以被不同的webui使用
from typing import *
from pathlib import Path
import os
from configs.model_config import (
    EMBEDDING_MODEL,
    KB_ROOT_PATH,
    LLM_MODEL,
    llm_model_dict,
    VECTOR_SEARCH_TOP_K,
    SEARCH_ENGINE_TOP_K,
)
import httpx
import asyncio
from server.chat.openai_chat import OpenAiChatMsgIn
from fastapi.responses import StreamingResponse
import contextlib
import json
from io import BytesIO
import pandas as pd
from server.knowledge_base.utils import list_kbs_from_folder, list_docs_from_folder
from server.db.repository.knowledge_base_repository import get_kb_detail
from server.db.repository.knowledge_file_repository import get_file_detail


def set_httpx_timeout(timeout=60.0):
    '''
    设置httpx默认timeout到60秒。
    httpx默认timeout是5秒，在请求LLM回答时不够用。
    '''
    httpx._config.DEFAULT_TIMEOUT_CONFIG.connect = timeout
    httpx._config.DEFAULT_TIMEOUT_CONFIG.read = timeout
    httpx._config.DEFAULT_TIMEOUT_CONFIG.write = timeout


KB_ROOT_PATH = Path(KB_ROOT_PATH)
set_httpx_timeout()


def run_async(cor):
    '''
    在同步环境中运行异步代码.
    '''
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
    return loop.run_until_complete(cor)


def iter_over_async(ait, loop):
    '''
    将异步生成器封装成同步生成器.
    '''
    ait = ait.__aiter__()
    async def get_next():
        try:
            obj = await ait.__anext__()
            return False, obj
        except StopAsyncIteration:
            return True, None
    while True:
        done, obj = loop.run_until_complete(get_next())
        if done:
            break
        yield obj


class ApiRequest:
    '''
    api.py调用的封装,主要实现:
    1. 简化api调用方式
    2. 实现无api调用(直接运行server.chat.*中的视图函数获取结果),无需启动api.py
    '''
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:7861",
        timeout: float = 60.0,
        no_remote_api: bool = False,   # call api view function directly
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.no_remote_api = no_remote_api

    def _parse_url(self, url: str) -> str:
        if (not url.startswith("http")
                    and self.base_url
                ):
            part1 = self.base_url.strip(" /")
            part2 = url.strip(" /")
            return f"{part1}/{part2}"
        else:
            return url

    def get(
        self,
        url: str,
        params: Union[Dict, List[Tuple], bytes] = None,
        retry: int = 3,
        **kwargs: Any,
    ) -> Union[httpx.Response, None]:
        url = self._parse_url(url)
        kwargs.setdefault("timeout", self.timeout)
        while retry > 0:
            try:
                return httpx.get(url, params=params, **kwargs)
            except:
                retry -= 1

    async def aget(
        self,
        url: str,
        params: Union[Dict, List[Tuple], bytes] = None,
        retry: int = 3,
        **kwargs: Any,
    ) -> Union[httpx.Response, None]:
        rl = self._parse_url(url)
        kwargs.setdefault("timeout", self.timeout)
        async with httpx.AsyncClient() as client:
            while retry > 0:
                try:
                    return await client.get(url, params=params, **kwargs)
                except:
                    retry -= 1

    def post(
        self,
        url: str,
        data: Dict = None,
        json: Dict = None,
        retry: int = 3,
        stream: bool = False,
        **kwargs: Any
    ) -> Union[httpx.Response, None]:
        url = self._parse_url(url)
        kwargs.setdefault("timeout", self.timeout)
        while retry > 0:
            try:
                # return requests.post(url, data=data, json=json, stream=stream, **kwargs)
                if stream:
                    return httpx.stream("POST", url, data=data, json=json, **kwargs)
                else:
                    return httpx.post(url, data=data, json=json, **kwargs)
            except:
                retry -= 1

    async def apost(
        self,
        url: str,
        data: Dict = None,
        json: Dict = None,
        retry: int = 3,
        **kwargs: Any
    ) -> Union[httpx.Response, None]:
        rl = self._parse_url(url)
        kwargs.setdefault("timeout", self.timeout)
        async with httpx.AsyncClient() as client:
            while retry > 0:
                try:
                    return await client.post(url, data=data, json=json, **kwargs)
                except:
                    retry -= 1

    def _fastapi_stream2generator(self, response: StreamingResponse, as_json: bool =False):
        '''
        将api.py中视图函数返回的StreamingResponse转化为同步生成器
        '''
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        
        for chunk in  iter_over_async(response.body_iterator, loop):
            if as_json and chunk:
                yield json.loads(chunk)
            elif chunk.strip():
                yield chunk

    def _httpx_stream2generator(
        self,
        response: contextlib._GeneratorContextManager,
        as_json: bool = False,
    ):
        '''
        将httpx.stream返回的GeneratorContextManager转化为普通生成器
        '''
        with response as r:
            for chunk in r.iter_text(None):
                if as_json and chunk:
                    yield json.loads(chunk)
                elif chunk.strip():
                    yield chunk

    # 对话相关操作

    def chat_fastchat(
        self,
        messages: List[Dict],
        stream: bool = True,
        model: str = LLM_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1024, # todo:根据message内容自动计算max_tokens
        no_remote_api: bool = None,
        **kwargs: Any,
    ):
        '''
        对应api.py/chat/fastchat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api
        msg = OpenAiChatMsgIn(**{
            "messages": messages,
            "stream": stream,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        })

        if no_remote_api:
            from server.chat.openai_chat import openai_chat
            response = openai_chat(msg)
            return self._fastapi_stream2generator(response)
        else:
            data = msg.dict(exclude_unset=True, exclude_none=True)
            response = self.post(
                "/chat/fastchat",
                json=data,
                stream=stream,
            )
            return self._httpx_stream2generator(response)

    def chat_chat(
        self,
        query: str,
        history: List[Dict] = [],
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.chat.chat import chat
            response = chat(query, history)
            return self._fastapi_stream2generator(response)
        else:
            response = self.post("/chat/chat", json={"query": query, "history": history}, stream=True)
            return self._httpx_stream2generator(response)

    def knowledge_base_chat(
        self,
        query: str,
        knowledge_base_name: str,
        top_k: int = VECTOR_SEARCH_TOP_K,
        history: List[Dict] = [],
        stream: bool = True,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/knowledge_base_chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        data = {
            "query": query,
            "knowledge_base_name": knowledge_base_name,
            "top_k": top_k,
            "history": history,
            "stream": stream,
        }

        if no_remote_api:
            from server.chat.knowledge_base_chat import knowledge_base_chat
            response = knowledge_base_chat(**data)
            return self._fastapi_stream2generator(response, as_json=True)
        else:
            response = self.post(
                "/chat/knowledge_base_chat",
                json=data,
                stream=True,
            )
            return self._httpx_stream2generator(response, as_json=True)

    def search_engine_chat(
        self,
        query: str,
        search_engine_name: str,
        top_k: int = SEARCH_ENGINE_TOP_K,
        stream: bool = True,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/search_engine_chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        data = {
            "query": query,
            "search_engine_name": search_engine_name,
            "top_k": top_k,
            "stream": stream,
        }

        if no_remote_api:
            from server.chat.search_engine_chat import search_engine_chat
            response = search_engine_chat(**data)
            return self._fastapi_stream2generator(response, as_json=True)
        else:
            response = self.post(
                "/chat/search_engine_chat",
                json=data,
                stream=True,
            )
            return self._httpx_stream2generator(response, as_json=True)

    # 知识库相关操作

    def list_knowledge_bases(
        self,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/list_knowledge_bases接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_api import list_kbs
            response = run_async(list_kbs())
            return response.data
        else:
            response = self.get("/knowledge_base/list_knowledge_bases")
            return response.json().get("data")

    def create_knowledge_base(
        self,
        knowledge_base_name: str,
        vector_store_type: str = "faiss",
        embed_model: str = EMBEDDING_MODEL,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/create_knowledge_base接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        data = {
            "knowledge_base_name": knowledge_base_name,
            "vector_store_type": vector_store_type,
            "embed_model": embed_model,
        }

        if no_remote_api:
            from server.knowledge_base.kb_api import create_kb
            response = run_async(create_kb(**data))
            return response.dict()
        else:
            response = self.post(
                "/knowledge_base/create_knowledge_base",
                json=data,
            )
            return response.json()

    def delete_knowledge_base(
        self,
        knowledge_base_name: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/delete_knowledge_base接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_api import delete_kb
            response = run_async(delete_kb(knowledge_base_name))
            return response.dict()
        else:
            response = self.delete(
                "/knowledge_base/delete_knowledge_base",
                json={"knowledge_base_name": knowledge_base_name},
            )
            return response.json()

    def list_kb_docs(
        self,
        knowledge_base_name: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/list_docs接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import list_docs
            response = run_async(list_docs(knowledge_base_name))
            return response.data
        else:
            response = self.get(
                "/knowledge_base/list_docs",
                params={"knowledge_base_name": knowledge_base_name}
            )
            return response.json().get("data")

    def upload_kb_doc(
        self,
        file: Union[str, Path, bytes],
        knowledge_base_name: str,
        filename: str = None,
        override: bool = False,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/upload_docs接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if isinstance(file, bytes): # raw bytes
            file = BytesIO(file)
        elif hasattr(file, "read"): # a file io like object
            filename = filename or file.name
        else: # a local path
            file = Path(file).absolute().open("rb")
            filename = filename or file.name

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import upload_doc
            from fastapi import UploadFile
            from tempfile import SpooledTemporaryFile

            temp_file = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
            temp_file.write(file.read())
            temp_file.seek(0)
            response = run_async(upload_doc(
                UploadFile(temp_file, filename=filename),
                knowledge_base_name,
                override,
            ))
            return response.dict()
        else:
            response = self.post(
                "/knowledge_base/upload_doc",
                data={"knowledge_base_name": knowledge_base_name, "override": override},
                files={"file": (filename, file)},
            )
            return response.json()

    def delete_kb_doc(
        self,
        knowledge_base_name: str,
        doc_name: str,
        delete_content: bool = False,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/delete_doc接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        data = {
            "knowledge_base_name": knowledge_base_name,
            "doc_name": doc_name,
            "delete_content": delete_content,
        }

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import delete_doc
            response = run_async(delete_doc(**data))
            return response.dict()
        else:
            response = self.delete(
                "/knowledge_base/delete_doc",
                json=data,
            )
            return response.json()

    def update_kb_doc(
        self,
        knowledge_base_name: str,
        doc_name: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/update_doc接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import update_doc
            response = run_async(update_doc(knowledge_base_name, doc_name))
            return response.dict()
        else:
            response = self.delete(
                "/knowledge_base/update_doc",
                json={"knowledge_base_name": knowledge_base_name, "doc_name": doc_name},
            )
            return response.json()

    def recreate_vector_store(
        self,
        knowledge_base_name: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/recreate_vector_store接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import recreate_vector_store
            response = run_async(recreate_vector_store(knowledge_base_name))
            return self._fastapi_stream2generator(response, as_json=True)
        else:
            response = self.post(
                "/knowledge_base/recreate_vector_store",
                json={"knowledge_base_name": knowledge_base_name},
            )
            return self._httpx_stream2generator(response, as_json=True)


def get_kb_details(api: ApiRequest) -> pd.DataFrame:
    kbs_in_folder = list_kbs_from_folder()
    kbs_in_db = api.list_knowledge_bases()
    result = {}

    for kb in kbs_in_folder:
        result[kb] = {
            "kb_name": kb,
            "vs_type": "",
            "embed_model": "",
            "file_count": 0,
            "create_time": None,
            "in_folder": True,
            "in_db": False,
        }
    
    for kb in kbs_in_db:
        kb_detail = get_kb_detail(kb)
        if kb_detail:
            kb_detail["in_db"] = True
            if kb in result:
                result[kb].update(kb_detail)
            else:
                kb_detail["in_folder"] = False
                result[kb] = kb_detail

    df = pd.DataFrame(result.values(), columns=[
            "kb_name",
            "vs_type",
            "embed_model",
            "file_count",
            "create_time",
            "in_folder",
            "in_db",
    ])
    df.insert(0, "No", range(1, len(df) + 1))
    return df


def get_kb_doc_details(api: ApiRequest, kb: str) -> pd.DataFrame:
    docs_in_folder = list_docs_from_folder(kb)
    docs_in_db = api.list_kb_docs(kb)
    result = {}

    for doc in docs_in_folder:
        result[doc] = {
            "kb_name": kb,
            "file_name": doc,
            "file_ext": os.path.splitext(doc)[-1],
            "file_version": 0,
            "document_loader": "",
            "text_splitter": "",
            "create_time": None,
            "in_folder": True,
            "in_db": False,
        }
    
    for doc in docs_in_db:
        doc_detail = get_file_detail(kb, doc)
        if doc_detail:
            doc_detail["in_db"] = True
            if doc in result:
                result[doc].update(doc_detail)
            else:
                doc_detail["in_folder"] = False
                result[doc] = doc_detail

    df = pd.DataFrame(result.values(), columns=[
            "kb_name",
            "file_name",
            "file_ext",
            "file_version",
            "document_loader",
            "text_splitter",
            "create_time",
            "in_folder",
            "in_db",        
    ])
    df.insert(0, "No", range(1, len(df) + 1))
    return df


def init_vs_database(recreate_vs: bool = False):
    '''
    init local vector store info to database
    '''
    from server.db.base import Base, engine
    from server.db.repository.knowledge_base_repository import add_kb_to_db, kb_exists
    from server.db.repository.knowledge_file_repository import add_doc_to_db
    from server.knowledge_base.utils import KnowledgeFile

    Base.metadata.create_all(bind=engine)

    if recreate_vs:
        api = ApiRequest(no_remote_api=True)
        for kb in list_kbs_from_folder():
            for t in api.recreate_vector_store(kb):
                print(t)
    else: # add vs info to db only
        for kb in list_kbs_from_folder():
            if not kb_exists(kb):
                add_kb_to_db(kb, "faiss", EMBEDDING_MODEL)
                for doc in list_docs_from_folder(kb):
                    try:
                        kb_file = KnowledgeFile(doc, kb)
                        add_doc_to_db(kb_file)
                    except Exception as e:
                        print(e)


if __name__ == "__main__":
    api = ApiRequest(no_remote_api=True)
    # init vector store database
    init_vs_database()

    # print(api.chat_fastchat(
    #     messages=[{"role": "user", "content": "hello"}]
    # ))

    # with api.chat_chat("你好") as r:
    #     for t in r.iter_text(None):
    #         print(t)

    # r = api.chat_chat("你好", no_remote_api=True)
    # for t in r:
    #     print(t)

    # r = api.duckduckgo_search_chat("室温超导最新研究进展", no_remote_api=True)
    # for t in r:
    #     print(t)

    # print(api.list_knowledge_bases())
