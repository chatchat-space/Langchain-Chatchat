# 该文件包含webui通用工具，可以被不同的webui使用

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
    ):
        self.base_url = base_url
        self.timeout = timeout

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
                return httpx.get(url, params, **kwargs)
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
                    return await client.get(url, params, **kwargs)
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

    def _stream2generator(self, response: StreamingResponse):
        '''
        将api.py中视图函数返回的StreamingResponse转化为同步生成器
        '''
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        return iter_over_async(response.body_iterator, loop)

    def chat_fastchat(
        self,
        messages: List[Dict],
        stream: bool = True,
        model: str = LLM_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1024, # todo:根据message内容自动计算max_tokens
        no_remote_api=False,  # all api view function directly
        **kwargs: Any,
    ):
        '''
        对应api.py/chat/fastchat接口
        '''
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
            return self._stream2generator(response)
        else:
            data = msg.dict(exclude_unset=True, exclude_none=True)
            response = self.post(
                "/chat/fastchat",
                json=data,
                stream=stream,
            )
            return response

    def chat_chat(
        self,
        query: str,
        no_remote_api: bool = False,
    ):
        '''
        对应api.py/chat/chat接口
        '''
        if no_remote_api:
            from server.chat.chat import chat
            response = chat(query)
            return self._stream2generator(response)
        else:
            response = self.post("/chat/chat", json=f"{query}", stream=True)
            return response


if __name__ == "__main__":
    api = ApiRequest()
    # print(api.chat_fastchat(
    #     messages=[{"role": "user", "content": "hello"}]
    # ))

    with api.chat_chat("你好") as r:
        for t in r.iter_text(None):
            print(t)

    r = api.chat_chat("你好", no_remote_api=True)
    for t in r:
        print(t)