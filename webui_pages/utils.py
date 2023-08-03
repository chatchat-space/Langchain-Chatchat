# 该文件包含webui通用工具，可以被不同的webui使用

import tempfile
from typing import *
from pathlib import Path
import os
from configs.model_config import (
    KB_ROOT_PATH,
    LLM_MODEL,
    llm_model_dict,
)
import httpx
import asyncio
from server.chat.openai_chat import OpenAiChatMsgIn
from fastapi.responses import StreamingResponse
import contextlib


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


def get_kb_list() -> List[str]:
    '''
    获取知识库列表
    '''
    kb_list = os.listdir(KB_ROOT_PATH)
    return [x for x in kb_list if (KB_ROOT_PATH / x).is_dir()]


def get_kb_files(kb: str) -> List[str]:
    '''
    获取某个知识库下包含的所有文件（只包括根目录一级）
    '''
    kb = KB_ROOT_PATH / kb / "content"
    if kb.is_dir():
        kb_files = os.listdir(kb)
        return kb_files
    else:
        return []


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

    def _fastapi_stream2generator(self, response: StreamingResponse):
        '''
        将api.py中视图函数返回的StreamingResponse转化为同步生成器
        '''
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        return iter_over_async(response.body_iterator, loop)

    def _httpx_stream2generator(self,response: contextlib._GeneratorContextManager):
        '''
        将httpx.stream返回的GeneratorContextManager转化为普通生成器
        '''
        with response as r:
            for chunk in r.iter_text(None):
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
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.chat.chat import chat
            response = chat(query)
            return self._fastapi_stream2generator(response)
        else:
            response = self.post("/chat/chat", json=f"{query}", stream=True)
            return self._httpx_stream2generator(response)

    def knowledge_base_chat(
        self,
        query: str,
        knowledge_base_name: str,
        top_k: int = 3,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/knowledge_base_chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.chat.knowledge_base_chat import knowledge_base_chat
            response = knowledge_base_chat(query, knowledge_base_name, top_k)
            return self._fastapi_stream2generator(response)
        else:
            response = self.post(
                "/chat/knowledge_base_chat",
                json={"query": query, "knowledge_base_name": knowledge_base_name, "top_k": top_k},
                stream=True,
            )
            return self._httpx_stream2generator(response)

    def duckduckgo_search_chat(
        self,
        query: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/duckduckgo_search_chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.chat.duckduckgo_search_chat import duckduckgo_search_chat
            response = duckduckgo_search_chat(query)
            return self._fastapi_stream2generator(response)
        else:
            response = self.post(
                "/chat/duckduckgo_search_chat",
                json=f"{query}",
                stream=True,
            )
            return self._httpx_stream2generator(response)

    def bing_search_chat(
        self,
        query: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/bing_search_chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.chat.bing_search_chat import bing_search_chat
            response = bing_search_chat(query)
            return self._fastapi_stream2generator(response)
        else:
            response = self.post(
                "/chat/bing_search_chat",
                json=f"{query}",
                stream=True,
            )
            return self._httpx_stream2generator(response)

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
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/create_knowledge_base接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_api import create_kb
            response = run_async(create_kb(knowledge_base_name))
            return response.dict()
        else:
            response = self.post(
                "/knowledge_base/create_knowledge_base",
                json={"knowledge_base_name": knowledge_base_name},
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
        file: Union[str, Path],
        knowledge_base_name: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/upload_docs接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        file = Path(file).absolute()
        filename = file.name

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import upload_doc
            from fastapi import UploadFile
            from tempfile import SpooledTemporaryFile

            temp_file = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
            with file.open("rb") as fp:
                temp_file.write(fp.read())
            response = run_async(upload_doc(
                UploadFile(temp_file, filename=filename),
                knowledge_base_name,
            ))
            return response.dict()
        else:
            response = self.post(
                "/knowledge_base/upload_doc",
                data={"knowledge_base_name": knowledge_base_name},
                files={"file": (filename, file.open("rb"))},
            )
            return response.json()

    def delete_kb_doc(
        self,
        knowledge_base_name: str,
        doc_name: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/delete_doc接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import delete_doc
            response = run_async(delete_doc(knowledge_base_name, doc_name))
            return response.dict()
        else:
            response = self.delete(
                "/knowledge_base/delete_doc",
                json={"knowledge_base_name": knowledge_base_name, "doc_name": doc_name},
            )
            return response.json()


if __name__ == "__main__":
    api = ApiRequest()

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

    print(api.list_knowledge_bases())
