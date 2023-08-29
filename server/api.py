import nltk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from configs.model_config import LLM_MODEL, NLTK_DATA_PATH
from configs.server_config import OPEN_CROSS_DOMAIN, HTTPX_DEFAULT_TIMEOUT
from configs import VERSION
import argparse
import uvicorn
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from server.chat import (chat, knowledge_base_chat, openai_chat,
                         search_engine_chat)
from server.knowledge_base.kb_api import list_kbs, create_kb, delete_kb
from server.knowledge_base.kb_doc_api import (list_files, upload_doc, delete_doc,
                                              update_doc, download_doc, recreate_vector_store,
                                              search_docs, DocumentWithScore)
from server.utils import BaseResponse, ListResponse, FastAPI, MakeFastAPIOffline, fschat_controller_address
import httpx
from typing import List

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path


async def document():
    return RedirectResponse(url="/docs")


def create_app():
    app = FastAPI(
        title="Langchain-Chatchat API Server",
        version=VERSION
    )
    MakeFastAPIOffline(app)
    # Add CORS middleware to allow all origins
    # 在config.py中设置OPEN_DOMAIN=True，允许跨域
    # set OPEN_DOMAIN=True in config.py to allow cross-domain
    if OPEN_CROSS_DOMAIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.get("/",
            response_model=BaseResponse,
            summary="swagger 文档")(document)

    # Tag: Chat
    app.post("/chat/fastchat",
             tags=["Chat"],
             summary="与llm模型对话(直接与fastchat api对话)")(openai_chat)

    app.post("/chat/chat",
             tags=["Chat"],
             summary="与llm模型对话(通过LLMChain)")(chat)

    app.post("/chat/knowledge_base_chat",
             tags=["Chat"],
             summary="与知识库对话")(knowledge_base_chat)

    app.post("/chat/search_engine_chat",
             tags=["Chat"],
             summary="与搜索引擎对话")(search_engine_chat)

    # Tag: Knowledge Base Management
    app.get("/knowledge_base/list_knowledge_bases",
            tags=["Knowledge Base Management"],
            response_model=ListResponse,
            summary="获取知识库列表")(list_kbs)

    app.post("/knowledge_base/create_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="创建知识库"
             )(create_kb)

    app.post("/knowledge_base/delete_knowledge_base",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="删除知识库"
             )(delete_kb)

    app.get("/knowledge_base/list_files",
            tags=["Knowledge Base Management"],
            response_model=ListResponse,
            summary="获取知识库内的文件列表"
            )(list_files)

    app.post("/knowledge_base/search_docs",
             tags=["Knowledge Base Management"],
             response_model=List[DocumentWithScore],
             summary="搜索知识库"
             )(search_docs)

    app.post("/knowledge_base/upload_doc",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="上传文件到知识库"
             )(upload_doc)

    app.post("/knowledge_base/delete_doc",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="删除知识库内指定文件"
             )(delete_doc)

    app.post("/knowledge_base/update_doc",
             tags=["Knowledge Base Management"],
             response_model=BaseResponse,
             summary="更新现有文件到知识库"
             )(update_doc)

    app.get("/knowledge_base/download_doc",
            tags=["Knowledge Base Management"],
            summary="下载对应的知识文件")(download_doc)

    app.post("/knowledge_base/recreate_vector_store",
             tags=["Knowledge Base Management"],
             summary="根据content中文档重建向量库，流式输出处理进度。"
             )(recreate_vector_store)

    # LLM模型相关接口
    @app.post("/llm_model/list_models",
            tags=["LLM Model Management"],
            summary="列出当前已加载的模型")
    def list_models(
        controller_address: str = Body(None, description="Fastchat controller服务器地址", examples=[fschat_controller_address()])
    ) -> BaseResponse:
        '''
        从fastchat controller获取已加载模型列表
        '''
        try:
            controller_address = controller_address or fschat_controller_address()
            r = httpx.post(controller_address + "/list_models")
            return BaseResponse(data=r.json()["models"])
        except Exception as e:
            return BaseResponse(
                code=500,
                data=[],
                msg=f"failed to get available models from controller: {controller_address}。错误信息是： {e}")

    @app.post("/llm_model/stop",
            tags=["LLM Model Management"],
            summary="停止指定的LLM模型（Model Worker)",
            )
    def stop_llm_model(
        model_name: str = Body(..., description="要停止的LLM模型名称", examples=[LLM_MODEL]),
        controller_address: str = Body(None, description="Fastchat controller服务器地址", examples=[fschat_controller_address()])
    ) -> BaseResponse:
        '''
        向fastchat controller请求停止某个LLM模型。
        注意：由于Fastchat的实现方式，实际上是把LLM模型所在的model_worker停掉。
        '''
        try:
            controller_address = controller_address or fschat_controller_address()
            r = httpx.post(
                controller_address + "/release_worker",
                json={"model_name": model_name},
            )
            return r.json()
        except Exception as e:
            return BaseResponse(
                code=500,
                msg=f"failed to stop LLM model {model_name} from controller: {controller_address}。错误信息是： {e}")

    @app.post("/llm_model/change",
            tags=["LLM Model Management"],
            summary="切换指定的LLM模型（Model Worker)",
            )
    def change_llm_model(
        model_name: str = Body(..., description="当前运行模型", examples=[LLM_MODEL]),
        new_model_name: str = Body(..., description="要切换的新模型", examples=[LLM_MODEL]),
        controller_address: str = Body(None, description="Fastchat controller服务器地址", examples=[fschat_controller_address()])
    ):
        '''
        向fastchat controller请求切换LLM模型。
        '''
        try:
            controller_address = controller_address or fschat_controller_address()
            r = httpx.post(
                controller_address + "/release_worker",
                json={"model_name": model_name, "new_model_name": new_model_name},
                timeout=HTTPX_DEFAULT_TIMEOUT, # wait for new worker_model
            )
            return r.json()
        except Exception as e:
            return BaseResponse(
                code=500,
                msg=f"failed to switch LLM model from controller: {controller_address}。错误信息是： {e}")

    return app


app = create_app()


def run_api(host, port, **kwargs):
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(app,
                    host=host,
                    port=port,
                    ssl_keyfile=kwargs.get("ssl_keyfile"),
                    ssl_certfile=kwargs.get("ssl_certfile"),
                    )
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='langchain-ChatGLM',
                                     description='About langchain-ChatGLM, local knowledge based ChatGLM with langchain'
                                                 ' ｜ 基于本地知识库的 ChatGLM 问答')
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7861)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)
    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)
    run_api(host=args.host,
            port=args.port,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
            )
