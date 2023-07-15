#encoding:utf-8
import argparse
import json
import os
import shutil
from typing import List, Optional
import urllib
import asyncio
import nltk
import pydantic
import uvicorn
from fastapi import Body, FastAPI, File, Form, Query, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing_extensions import Annotated
from starlette.responses import RedirectResponse

from chains.local_doc_qa import LocalDocQA
from configs.model_config import (KB_ROOT_PATH, EMBEDDING_DEVICE,
                                  EMBEDDING_MODEL, NLTK_DATA_PATH,
                                  VECTOR_SEARCH_TOP_K, LLM_HISTORY_LEN, OPEN_CROSS_DOMAIN)
import models.shared as shared
from models.loader.args import parser
from models.loader import LoaderCheckPoint

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path


class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="HTTP status code")
    msg: str = pydantic.Field("success", description="HTTP status message")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }


class ListDocsResponse(BaseResponse):
    data: List[str] = pydantic.Field(..., description="List of document names")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": ["doc1.docx", "doc2.pdf", "doc3.txt"],
            }
        }


class ChatMessage(BaseModel):
    question: str = pydantic.Field(..., description="Question text")
    response: str = pydantic.Field(..., description="Response text")
    history: List[List[str]] = pydantic.Field(..., description="History text")
    source_documents: List[str] = pydantic.Field(
        ..., description="List of source documents and their scores"
    )

    class Config:
        schema_extra = {
            "example": {
                "question": "工伤保险如何办理？",
                "response": "根据已知信息，可以总结如下：\n\n1. 参保单位为员工缴纳工伤保险费，以保障员工在发生工伤时能够获得相应的待遇。\n2. 不同地区的工伤保险缴费规定可能有所不同，需要向当地社保部门咨询以了解具体的缴费标准和规定。\n3. 工伤从业人员及其近亲属需要申请工伤认定，确认享受的待遇资格，并按时缴纳工伤保险费。\n4. 工伤保险待遇包括工伤医疗、康复、辅助器具配置费用、伤残待遇、工亡待遇、一次性工亡补助金等。\n5. 工伤保险待遇领取资格认证包括长期待遇领取人员认证和一次性待遇领取人员认证。\n6. 工伤保险基金支付的待遇项目包括工伤医疗待遇、康复待遇、辅助器具配置费用、一次性工亡补助金、丧葬补助金等。",
                "history": [
                    [
                        "工伤保险是什么？",
                        "工伤保险是指用人单位按照国家规定，为本单位的职工和用人单位的其他人员，缴纳工伤保险费，由保险机构按照国家规定的标准，给予工伤保险待遇的社会保险制度。",
                    ]
                ],
                "source_documents": [
                    "出处 [1] 广州市单位从业的特定人员参加工伤保险办事指引.docx：\n\n\t( 一)  从业单位  (组织)  按“自愿参保”原则，  为未建 立劳动关系的特定从业人员单项参加工伤保险 、缴纳工伤保 险费。",
                    "出处 [2] ...",
                    "出处 [3] ...",
                ],
            }
        }


def get_kb_path(local_doc_id: str):
    return os.path.join(KB_ROOT_PATH, local_doc_id)


def get_doc_path(local_doc_id: str):
    return os.path.join(get_kb_path(local_doc_id), "content")


def get_vs_path(local_doc_id: str):
    return os.path.join(get_kb_path(local_doc_id), "vector_store")


def get_file_path(local_doc_id: str, doc_name: str):
    return os.path.join(get_doc_path(local_doc_id), doc_name)


def validate_kb_name(knowledge_base_id: str) -> bool:
    # 检查是否包含预期外的字符或路径攻击关键字
    if "../" in knowledge_base_id:
        return False
    return True


async def upload_file(
        file: UploadFile = File(description="A single binary file"),
        knowledge_base_id: str = Form(..., description="Knowledge Base Name", example="kb1"),
):
    if not validate_kb_name(knowledge_base_id):
        return BaseResponse(code=403, msg="Don't attack me", data=[])

    saved_path = get_doc_path(knowledge_base_id)
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)

    file_content = await file.read()  # 读取上传文件的内容

    file_path = os.path.join(saved_path, file.filename)
    if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
        file_status = f"文件 {file.filename} 已存在。"
        return BaseResponse(code=200, msg=file_status)

    with open(file_path, "wb") as f:
        f.write(file_content)

    vs_path = get_vs_path(knowledge_base_id)
    vs_path, loaded_files = local_doc_qa.init_knowledge_vector_store([file_path], vs_path)
    if len(loaded_files) > 0:
        file_status = f"文件 {file.filename} 已上传至新的知识库，并已加载知识库，请开始提问。"
        return BaseResponse(code=200, msg=file_status)
    else:
        file_status = "文件上传失败，请重新上传"
        return BaseResponse(code=500, msg=file_status)


async def upload_files(
        files: Annotated[
            List[UploadFile], File(description="Multiple files as UploadFile")
        ],
        knowledge_base_id: str = Form(..., description="Knowledge Base Name", example="kb1"),
):
    if not validate_kb_name(knowledge_base_id):
        return BaseResponse(code=403, msg="Don't attack me", data=[])

    saved_path = get_doc_path(knowledge_base_id)
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    filelist = []
    for file in files:
        file_content = ''
        file_path = os.path.join(saved_path, file.filename)
        file_content = await file.read()
        if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
            continue
        with open(file_path, "wb") as f:
            f.write(file_content)
        filelist.append(file_path)
    if filelist:
        vs_path = get_vs_path(knowledge_base_id)
        vs_path, loaded_files = local_doc_qa.init_knowledge_vector_store(filelist, vs_path)
        if len(loaded_files):
            file_status = f"documents {', '.join([os.path.split(i)[-1] for i in loaded_files])} upload success"
            return BaseResponse(code=200, msg=file_status)
    file_status = f"documents {', '.join([os.path.split(i)[-1] for i in loaded_files])} upload fail"
    return BaseResponse(code=500, msg=file_status)


async def list_kbs():
    # Get List of Knowledge Base
    if not os.path.exists(KB_ROOT_PATH):
        all_doc_ids = []
    else:
        all_doc_ids = [
            folder
            for folder in os.listdir(KB_ROOT_PATH)
            if os.path.isdir(os.path.join(KB_ROOT_PATH, folder))
               and os.path.exists(os.path.join(KB_ROOT_PATH, folder, "vector_store", "index.faiss"))
        ]

    return ListDocsResponse(data=all_doc_ids)


async def list_docs(
        knowledge_base_id: str = Query(..., description="Knowledge Base Name", example="kb1")
):
    if not validate_kb_name(knowledge_base_id):
        return ListDocsResponse(code=403, msg="Don't attack me", data=[])

    knowledge_base_id = urllib.parse.unquote(knowledge_base_id)
    kb_path = get_kb_path(knowledge_base_id)
    local_doc_folder = get_doc_path(knowledge_base_id)
    if not os.path.exists(kb_path):
        return ListDocsResponse(code=404, msg=f"Knowledge base {knowledge_base_id} not found", data=[])
    if not os.path.exists(local_doc_folder):
        all_doc_names = []
    else:
        all_doc_names = [
            doc
            for doc in os.listdir(local_doc_folder)
            if os.path.isfile(os.path.join(local_doc_folder, doc))
        ]
    return ListDocsResponse(data=all_doc_names)


async def delete_kb(
        knowledge_base_id: str = Query(...,
                                       description="Knowledge Base Name",
                                       example="kb1"),
):
    if not validate_kb_name(knowledge_base_id):
        return BaseResponse(code=403, msg="Don't attack me")

    # TODO: 确认是否支持批量删除知识库
    knowledge_base_id = urllib.parse.unquote(knowledge_base_id)
    kb_path = get_kb_path(knowledge_base_id)
    if not os.path.exists(kb_path):
        return BaseResponse(code=404, msg=f"Knowledge base {knowledge_base_id} not found")
    shutil.rmtree(kb_path)
    return BaseResponse(code=200, msg=f"Knowledge Base {knowledge_base_id} delete success")


async def delete_doc(
        knowledge_base_id: str = Query(...,
                                       description="Knowledge Base Name",
                                       example="kb1"),
        doc_name: str = Query(
            ..., description="doc name", example="doc_name_1.pdf"
        ),
):
    if not validate_kb_name(knowledge_base_id):
        return BaseResponse(code=403, msg="Don't attack me")

    knowledge_base_id = urllib.parse.unquote(knowledge_base_id)
    if not os.path.exists(get_kb_path(knowledge_base_id)):
        return BaseResponse(code=404, msg=f"Knowledge base {knowledge_base_id} not found")
    doc_path = get_file_path(knowledge_base_id, doc_name)
    if os.path.exists(doc_path):
        os.remove(doc_path)
        remain_docs = await list_docs(knowledge_base_id)
        if len(remain_docs.data) == 0:
            shutil.rmtree(get_kb_path(knowledge_base_id), ignore_errors=True)
            return BaseResponse(code=200, msg=f"document {doc_name} delete success")
        else:
            status = local_doc_qa.delete_file_from_vector_store(doc_path, get_vs_path(knowledge_base_id))
            if "success" in status:
                return BaseResponse(code=200, msg=f"document {doc_name} delete success")
            else:
                return BaseResponse(code=500, msg=f"document {doc_name} delete fail")
    else:
        return BaseResponse(code=404, msg=f"document {doc_name} not found")


async def update_doc(
        knowledge_base_id: str = Query(...,
                                       description="知识库名",
                                       example="kb1"),
        old_doc: str = Query(
            ..., description="待删除文件名，已存储在知识库中", example="doc_name_1.pdf"
        ),
        new_doc: UploadFile = File(description="待上传文件"),
):
    if not validate_kb_name(knowledge_base_id):
        return BaseResponse(code=403, msg="Don't attack me")

    knowledge_base_id = urllib.parse.unquote(knowledge_base_id)
    if not os.path.exists(get_kb_path(knowledge_base_id)):
        return BaseResponse(code=404, msg=f"Knowledge base {knowledge_base_id} not found")
    doc_path = get_file_path(knowledge_base_id, old_doc)
    if not os.path.exists(doc_path):
        return BaseResponse(code=404, msg=f"document {old_doc} not found")
    else:
        os.remove(doc_path)
        delete_status = local_doc_qa.delete_file_from_vector_store(doc_path, get_vs_path(knowledge_base_id))
        if "fail" in delete_status:
            return BaseResponse(code=500, msg=f"document {old_doc} delete failed")
        else:
            saved_path = get_doc_path(knowledge_base_id)
            if not os.path.exists(saved_path):
                os.makedirs(saved_path)

            file_content = await new_doc.read()  # 读取上传文件的内容

            file_path = os.path.join(saved_path, new_doc.filename)
            if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
                file_status = f"document {new_doc.filename} already exists"
                return BaseResponse(code=200, msg=file_status)

            with open(file_path, "wb") as f:
                f.write(file_content)

            vs_path = get_vs_path(knowledge_base_id)
            vs_path, loaded_files = local_doc_qa.init_knowledge_vector_store([file_path], vs_path)
            if len(loaded_files) > 0:
                file_status = f"document {old_doc} delete and document {new_doc.filename} upload success"
                return BaseResponse(code=200, msg=file_status)
            else:
                file_status = f"document {old_doc} success but document {new_doc.filename} upload fail"
                return BaseResponse(code=500, msg=file_status)



async def local_doc_chat(
        knowledge_base_id: str = Body(..., description="Knowledge Base Name", example="kb1"),
        question: str = Body(..., description="Question", example="工伤保险是什么？"),
        history: List[List[str]] = Body(
            [],
            description="History of previous questions and answers",
            example=[
                [
                    "工伤保险是什么？",
                    "工伤保险是指用人单位按照国家规定，为本单位的职工和用人单位的其他人员，缴纳工伤保险费，由保险机构按照国家规定的标准，给予工伤保险待遇的社会保险制度。",
                ]
            ],
        ),
):
    vs_path = get_vs_path(knowledge_base_id)
    if not os.path.exists(vs_path):
        # return BaseResponse(code=404, msg=f"Knowledge base {knowledge_base_id} not found")
        return ChatMessage(
            question=question,
            response=f"Knowledge base {knowledge_base_id} not found",
            history=history,
            source_documents=[],
        )
    else:
        for resp, history in local_doc_qa.get_knowledge_based_answer(
                query=question, vs_path=vs_path, chat_history=history, streaming=True
        ):
            pass
        source_documents = [
            f"""出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n"""
            f"""相关度：{doc.metadata['score']}\n\n"""
            for inum, doc in enumerate(resp["source_documents"])
        ]

        return ChatMessage(
            question=question,
            response=resp["result"],
            history=history,
            source_documents=source_documents,
        )


async def bing_search_chat(
        question: str = Body(..., description="Question", example="工伤保险是什么？"),
        history: Optional[List[List[str]]] = Body(
            [],
            description="History of previous questions and answers",
            example=[
                [
                    "工伤保险是什么？",
                    "工伤保险是指用人单位按照国家规定，为本单位的职工和用人单位的其他人员，缴纳工伤保险费，由保险机构按照国家规定的标准，给予工伤保险待遇的社会保险制度。",
                ]
            ],
        ),
):
    for resp, history in local_doc_qa.get_search_result_based_answer(
            query=question, chat_history=history, streaming=True
    ):
        pass
    source_documents = [
        f"""出处 [{inum + 1}] [{doc.metadata["source"]}]({doc.metadata["source"]}) \n\n{doc.page_content}\n\n"""
        for inum, doc in enumerate(resp["source_documents"])
    ]

    return ChatMessage(
        question=question,
        response=resp["result"],
        history=history,
        source_documents=source_documents,
    )


async def chat(
        question: str = Body(..., description="Question", example="工伤保险是什么？"),
        history: List[List[str]] = Body(
            [],
            description="History of previous questions and answers",
            example=[
                [
                    "工伤保险是什么？",
                    "工伤保险是指用人单位按照国家规定，为本单位的职工和用人单位的其他人员，缴纳工伤保险费，由保险机构按照国家规定的标准，给予工伤保险待遇的社会保险制度。",
                ]
            ],
        ),
):
    answer_result_stream_result = local_doc_qa.llm_model_chain(
        {"prompt": question, "history": history, "streaming": True})

    for answer_result in answer_result_stream_result['answer_result_stream']:
        resp = answer_result.llm_output["answer"]
        history = answer_result.history
        pass

    return ChatMessage(
        question=question,
        response=resp,
        history=history,
        source_documents=[],
    )


async def stream_chat(websocket: WebSocket):
    await websocket.accept()
    turn = 1
    while True:
        input_json = await websocket.receive_json()
        question, history, knowledge_base_id = input_json["question"], input_json["history"], input_json[
            "knowledge_base_id"]
        vs_path = get_vs_path(knowledge_base_id)

        if not os.path.exists(vs_path):
            await websocket.send_json({"error": f"Knowledge base {knowledge_base_id} not found"})
            await websocket.close()
            return

        await websocket.send_json({"question": question, "turn": turn, "flag": "start"})

        last_print_len = 0
        for resp, history in local_doc_qa.get_knowledge_based_answer(
                query=question, vs_path=vs_path, chat_history=history, streaming=True
        ):
            await asyncio.sleep(0)
            await websocket.send_text(resp["result"][last_print_len:])
            last_print_len = len(resp["result"])

        source_documents = [
            f"""出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n"""
            f"""相关度：{doc.metadata['score']}\n\n"""
            for inum, doc in enumerate(resp["source_documents"])
        ]

        await websocket.send_text(
            json.dumps(
                {
                    "question": question,
                    "turn": turn,
                    "flag": "end",
                    "sources_documents": source_documents,
                },
                ensure_ascii=False,
            )
        )
        turn += 1

async def stream_chat_bing(websocket: WebSocket):
    """
    基于bing搜索的流式问答
    """
    await websocket.accept()
    turn = 1
    while True:
        input_json = await websocket.receive_json()
        question, history = input_json["question"], input_json["history"]

        await websocket.send_json({"question": question, "turn": turn, "flag": "start"})

        last_print_len = 0
        for resp, history in local_doc_qa.get_search_result_based_answer(question, chat_history=history, streaming=True):
            await websocket.send_text(resp["result"][last_print_len:])
            last_print_len = len(resp["result"])

        source_documents = [
            f"""出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n"""
            f"""相关度：{doc.metadata['score']}\n\n"""
            for inum, doc in enumerate(resp["source_documents"])
        ]

        await websocket.send_text(
            json.dumps(
                {
                    "question": question,
                    "turn": turn,
                    "flag": "end",
                    "sources_documents": source_documents,
                },
                ensure_ascii=False,
            )
        )
        turn += 1

async def document():
    return RedirectResponse(url="/docs")


def api_start(host, port, **kwargs):
    global app
    global local_doc_qa

    llm_model_ins = shared.loaderLLM()

    app = FastAPI()
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
    # 修改了stream_chat的接口，直接通过ws://localhost:7861/local_doc_qa/stream_chat建立连接，在请求体中选择knowledge_base_id
    app.websocket("/local_doc_qa/stream_chat")(stream_chat)

    app.get("/", response_model=BaseResponse, summary="swagger 文档")(document)

    # 增加基于bing搜索的流式问答
    # 需要说明的是，如果想测试websocket的流式问答，需要使用支持websocket的测试工具，如postman,insomnia
    # 强烈推荐开源的insomnia
    # 在测试时选择new websocket request,并将url的协议改为ws,如ws://localhost:7861/local_doc_qa/stream_chat_bing
    app.websocket("/local_doc_qa/stream_chat_bing")(stream_chat_bing)

    app.post("/chat", response_model=ChatMessage, summary="与模型对话")(chat)

    app.post("/local_doc_qa/upload_file", response_model=BaseResponse, summary="上传文件到知识库")(upload_file)
    app.post("/local_doc_qa/upload_files", response_model=BaseResponse, summary="批量上传文件到知识库")(upload_files)
    app.post("/local_doc_qa/local_doc_chat", response_model=ChatMessage, summary="与知识库对话")(local_doc_chat)
    app.post("/local_doc_qa/bing_search_chat", response_model=ChatMessage, summary="与必应搜索对话")(bing_search_chat)
    app.get("/local_doc_qa/list_knowledge_base", response_model=ListDocsResponse, summary="获取知识库列表")(list_kbs)
    app.get("/local_doc_qa/list_files", response_model=ListDocsResponse, summary="获取知识库内的文件列表")(list_docs)
    app.delete("/local_doc_qa/delete_knowledge_base", response_model=BaseResponse, summary="删除知识库")(delete_kb)
    app.delete("/local_doc_qa/delete_file", response_model=BaseResponse, summary="删除知识库内的文件")(delete_doc)
    app.post("/local_doc_qa/update_file", response_model=BaseResponse, summary="上传文件到知识库，并删除另一个文件")(update_doc)

    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(
        llm_model=llm_model_ins,
        embedding_model=EMBEDDING_MODEL,
        embedding_device=EMBEDDING_DEVICE,
        top_k=VECTOR_SEARCH_TOP_K,
    )
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(app, host=host, port=port, ssl_keyfile=kwargs.get("ssl_keyfile"),
                    ssl_certfile=kwargs.get("ssl_certfile"))
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7861)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)
    # 初始化消息
    args = None
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    api_start(args.host, args.port, ssl_keyfile=args.ssl_keyfile, ssl_certfile=args.ssl_certfile)
