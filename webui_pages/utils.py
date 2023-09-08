# 该文件包含webui通用工具，可以被不同的webui使用
from typing import *
from pathlib import Path
from configs.model_config import (
    EMBEDDING_MODEL,
    DEFAULT_VS_TYPE,
    KB_ROOT_PATH,
    LLM_MODEL,
    llm_model_dict,
    HISTORY_LEN,
    SCORE_THRESHOLD,
    VECTOR_SEARCH_TOP_K,
    SEARCH_ENGINE_TOP_K,
    logger,
)
from configs.server_config import HTTPX_DEFAULT_TIMEOUT
import httpx
import asyncio
from server.chat.openai_chat import OpenAiChatMsgIn
from fastapi.responses import StreamingResponse
import contextlib
import json
from io import BytesIO
from server.db.repository.knowledge_base_repository import get_kb_detail
from server.db.repository.knowledge_file_repository import get_file_detail
from server.utils import run_async, iter_over_async, set_httpx_timeout

from configs.model_config import NLTK_DATA_PATH
import nltk
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path
from pprint import pprint


KB_ROOT_PATH = Path(KB_ROOT_PATH)
set_httpx_timeout()


class ApiRequest:
    '''
    api.py调用的封装,主要实现:
    1. 简化api调用方式
    2. 实现无api调用(直接运行server.chat.*中的视图函数获取结果),无需启动api.py
    '''
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:7861",
        timeout: float = HTTPX_DEFAULT_TIMEOUT,
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
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[httpx.Response, None]:
        url = self._parse_url(url)
        kwargs.setdefault("timeout", self.timeout)
        while retry > 0:
            try:
                if stream:
                    return httpx.stream("GET", url, params=params, **kwargs)
                else:
                    return httpx.get(url, params=params, **kwargs)
            except Exception as e:
                logger.error(e)
                retry -= 1

    async def aget(
        self,
        url: str,
        params: Union[Dict, List[Tuple], bytes] = None,
        retry: int = 3,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[httpx.Response, None]:
        url = self._parse_url(url)
        kwargs.setdefault("timeout", self.timeout)
        async with httpx.AsyncClient() as client:
            while retry > 0:
                try:
                    if stream:
                        return await client.stream("GET", url, params=params, **kwargs)
                    else:
                        return await client.get(url, params=params, **kwargs)
                except Exception as e:
                    logger.error(e)
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
            except Exception as e:
                logger.error(e)
                retry -= 1

    async def apost(
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
        async with httpx.AsyncClient() as client:
            while retry > 0:
                try:
                    if stream:
                        return await client.stream("POST", url, data=data, json=json, **kwargs)
                    else:
                        return await client.post(url, data=data, json=json, **kwargs)
                except Exception as e:
                    logger.error(e)
                    retry -= 1

    def delete(
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
                if stream:
                    return httpx.stream("DELETE", url, data=data, json=json, **kwargs)
                else:
                    return httpx.delete(url, data=data, json=json, **kwargs)
            except Exception as e:
                logger.error(e)
                retry -= 1

    async def adelete(
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
        async with httpx.AsyncClient() as client:
            while retry > 0:
                try:
                    if stream:
                        return await client.stream("DELETE", url, data=data, json=json, **kwargs)
                    else:
                        return await client.delete(url, data=data, json=json, **kwargs)
                except Exception as e:
                    logger.error(e)
                    retry -= 1

    def _fastapi_stream2generator(self, response: StreamingResponse, as_json: bool =False):
        '''
        将api.py中视图函数返回的StreamingResponse转化为同步生成器
        '''
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        
        try:
            for chunk in  iter_over_async(response.body_iterator, loop):
                if as_json and chunk:
                    yield json.loads(chunk)
                elif chunk.strip():
                    yield chunk
        except Exception as e:
            logger.error(e)

    def _httpx_stream2generator(
        self,
        response: contextlib._GeneratorContextManager,
        as_json: bool = False,
    ):
        '''
        将httpx.stream返回的GeneratorContextManager转化为普通生成器
        '''
        try:
            with response as r:
                for chunk in r.iter_text(None):
                    if not chunk: # fastchat api yield empty bytes on start and end
                        continue
                    if as_json:
                        try:
                            data = json.loads(chunk)
                            pprint(data, depth=1)
                            yield data
                        except Exception as e:
                            logger.error(f"接口返回json错误： ‘{chunk}’。错误信息是：{e}。")
                    else:
                        print(chunk, end="", flush=True)
                        yield chunk
        except httpx.ConnectError as e:
            msg = f"无法连接API服务器，请确认 ‘api.py’ 已正常启动。"
            logger.error(msg)
            logger.error(e)
            yield {"code": 500, "msg": msg}
        except httpx.ReadTimeout as e:
            msg = f"API通信超时，请确认已启动FastChat与API服务（详见RADME '5. 启动 API 服务或 Web UI'）"
            logger.error(msg)
            logger.error(e)
            yield {"code": 500, "msg": msg}
        except Exception as e:
            logger.error(e)
            yield {"code": 500, "msg": str(e)}

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
            print(f"received input message:")
            pprint(data)

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
        stream: bool = True,
        model: str = LLM_MODEL,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/chat/chat接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        data = {
            "query": query,
            "history": history,
            "stream": stream,
            "model_name": model,
        }

        print(f"received input message:")
        pprint(data)

        if no_remote_api:
            from server.chat.chat import chat
            response = chat(**data)
            return self._fastapi_stream2generator(response)
        else:
            response = self.post("/chat/chat", json=data, stream=True)
            return self._httpx_stream2generator(response)

    def knowledge_base_chat(
        self,
        query: str,
        knowledge_base_name: str,
        top_k: int = VECTOR_SEARCH_TOP_K,
        score_threshold: float = SCORE_THRESHOLD,
        history: List[Dict] = [],
        stream: bool = True,
        model: str = LLM_MODEL,
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
            "score_threshold": score_threshold,
            "history": history,
            "stream": stream,
            "model_name": model,
            "local_doc_url": no_remote_api,
        }

        print(f"received input message:")
        pprint(data)

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
        model: str = LLM_MODEL,
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
            "model_name": model,
        }

        print(f"received input message:")
        pprint(data)

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

    def _check_httpx_json_response(
            self,
            response: httpx.Response,
            errorMsg: str = f"无法连接API服务器，请确认已执行python server\\api.py",
        ) -> Dict:
        '''
        check whether httpx returns correct data with normal Response.
        error in api with streaming support was checked in _httpx_stream2enerator
        '''
        try:
            return response.json()
        except Exception as e:
            logger.error(e)
            return {"code": 500, "msg": errorMsg or str(e)}

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
            data = self._check_httpx_json_response(response)
            return data.get("data", [])

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
            return self._check_httpx_json_response(response)

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
            response = self.post(
                "/knowledge_base/delete_knowledge_base",
                json=f"{knowledge_base_name}",
            )
            return self._check_httpx_json_response(response)

    def list_kb_docs(
        self,
        knowledge_base_name: str,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/list_files接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import list_files
            response = run_async(list_files(knowledge_base_name))
            return response.data
        else:
            response = self.get(
                "/knowledge_base/list_files",
                params={"knowledge_base_name": knowledge_base_name}
            )
            data = self._check_httpx_json_response(response)
            return data.get("data", [])

    def upload_kb_doc(
        self,
        file: Union[str, Path, bytes],
        knowledge_base_name: str,
        filename: str = None,
        override: bool = False,
        not_refresh_vs_cache: bool = False,
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
                UploadFile(file=temp_file, filename=filename),
                knowledge_base_name,
                override,
            ))
            return response.dict()
        else:
            response = self.post(
                "/knowledge_base/upload_doc",
                data={
                    "knowledge_base_name": knowledge_base_name,
                    "override": override,
                    "not_refresh_vs_cache": not_refresh_vs_cache,
                },
                files={"file": (filename, file)},
            )
            return self._check_httpx_json_response(response)

    def delete_kb_doc(
        self,
        knowledge_base_name: str,
        doc_name: str,
        delete_content: bool = False,
        not_refresh_vs_cache: bool = False,
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
            "not_refresh_vs_cache": not_refresh_vs_cache,
        }

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import delete_doc
            response = run_async(delete_doc(**data))
            return response.dict()
        else:
            response = self.post(
                "/knowledge_base/delete_doc",
                json=data,
            )
            return self._check_httpx_json_response(response)

    def update_kb_doc(
        self,
        knowledge_base_name: str,
        file_name: str,
        not_refresh_vs_cache: bool = False,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/update_doc接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import update_doc
            response = run_async(update_doc(knowledge_base_name, file_name))
            return response.dict()
        else:
            response = self.post(
                "/knowledge_base/update_doc",
                json={
                    "knowledge_base_name": knowledge_base_name,
                    "file_name": file_name,
                    "not_refresh_vs_cache": not_refresh_vs_cache,
                },
            )
            return self._check_httpx_json_response(response)

    def recreate_vector_store(
        self,
        knowledge_base_name: str,
        allow_empty_kb: bool = True,
        vs_type: str = DEFAULT_VS_TYPE,
        embed_model: str = EMBEDDING_MODEL,
        no_remote_api: bool = None,
    ):
        '''
        对应api.py/knowledge_base/recreate_vector_store接口
        '''
        if no_remote_api is None:
            no_remote_api = self.no_remote_api

        data = {
            "knowledge_base_name": knowledge_base_name,
            "allow_empty_kb": allow_empty_kb,
            "vs_type": vs_type,
            "embed_model": embed_model,
        }

        if no_remote_api:
            from server.knowledge_base.kb_doc_api import recreate_vector_store
            response = run_async(recreate_vector_store(**data))
            return self._fastapi_stream2generator(response, as_json=True)
        else:
            response = self.post(
                "/knowledge_base/recreate_vector_store",
                json=data,
                stream=True,
                timeout=None,
            )
            return self._httpx_stream2generator(response, as_json=True)

    def list_running_models(self, controller_address: str = None):
        '''
        获取Fastchat中正运行的模型列表
        '''
        r = self.post(
            "/llm_model/list_models",
        )
        return r.json().get("data", [])

    def list_config_models(self):
        '''
        获取configs中配置的模型列表
        '''
        return list(llm_model_dict.keys())

    def stop_llm_model(
        self,
        model_name: str,
        controller_address: str = None,
    ):
        '''
        停止某个LLM模型。
        注意：由于Fastchat的实现方式，实际上是把LLM模型所在的model_worker停掉。
        '''
        data = {
            "model_name": model_name,
            "controller_address": controller_address,
        }
        r = self.post(
            "/llm_model/stop",
            json=data,
        )
        return r.json()
    
    def change_llm_model(
        self,
        model_name: str,
        new_model_name: str,
        controller_address: str = None,
    ):
        '''
        向fastchat controller请求切换LLM模型。
        '''
        if not model_name or not new_model_name:
            return

        if new_model_name == model_name:
            return {
                "code": 200,
                "msg": "什么都不用做"
            }

        running_models = self.list_running_models()
        if model_name not in running_models:
            return {
                "code": 500,
                "msg": f"指定的模型'{model_name}'没有运行。当前运行模型：{running_models}"
            }

        config_models = self.list_config_models()
        if new_model_name not in config_models:
            return {
                "code": 500,
                "msg": f"要切换的模型'{new_model_name}'在configs中没有配置。"
            }

        data = {
            "model_name": model_name,
            "new_model_name": new_model_name,
            "controller_address": controller_address,
        }
        r = self.post(
            "/llm_model/change",
            json=data,
            timeout=HTTPX_DEFAULT_TIMEOUT, # wait for new worker_model
        )
        return r.json()


def check_error_msg(data: Union[str, dict, list], key: str = "errorMsg") -> str:
    '''
    return error message if error occured when requests API
    '''
    if isinstance(data, dict):
        if key in data:
            return data[key]
        if "code" in data and data["code"] != 200:
            return data["msg"]
    return ""


def check_success_msg(data: Union[str, dict, list], key: str = "msg") -> str:
    '''
    return error message if error occured when requests API
    '''
    if (isinstance(data, dict)
        and key in data
        and "code" in data
        and data["code"] == 200):
        return data[key]
    return ""


if __name__ == "__main__":
    api = ApiRequest(no_remote_api=True)

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
