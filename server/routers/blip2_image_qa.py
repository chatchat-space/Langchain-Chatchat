import json
import os
import models.shared as shared

from models.loader.args import parser
from models.loader import LoaderCheckPoint
from models.base import LavisBlip2Multimodal
from fastapi import File, Form, Body, UploadFile, APIRouter, Depends
from server.model import BaseResponse, ChatMessage, ListDocsResponse
from typing import List, Optional
from configs.model_config import (VS_ROOT_PATH, UPLOAD_ROOT_PATH)

llm_model_ins: LavisBlip2Multimodal = None
blip2_image_qa_router = APIRouter(
    prefix="/blip2_image_qa",  # 前缀只在这个模块中使用
    tags=["blip2_image_qa"]
)

def get_folder_path(local_image_id: str):
    return os.path.join(UPLOAD_ROOT_PATH, local_image_id)


def get_file_path(local_image_id: str, image_name: str):
    return os.path.join(UPLOAD_ROOT_PATH, local_image_id, image_name)


@blip2_image_qa_router.post("/init_blip2_model")
async def init_blip2_model():
    global llm_model_ins
    args = None
    args = parser.parse_args(
        args=['--model-dir', '/media/checkpoint/', '--model', 'LavisBlip2Vicuna', '--no-remote-model'])
    args_dict = vars(args)

    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    if llm_model_ins:
        file_status = f"模型加载成功"
        return BaseResponse(code=200, msg=file_status)
    else:
        file_status = "文件上传失败，请重新上传"
        return BaseResponse(code=500, msg=file_status)


@blip2_image_qa_router.post("/upload_file")
async def upload_file(
        file: UploadFile = File(description="A single binary file"),
        local_image_id: str = Form(..., description="image Base Name", example="kb1"),
):
    saved_path = get_folder_path(local_image_id)
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)

    file_content = await file.read()  # 读取上传文件的内容

    file_path = os.path.join(saved_path, file.filename)
    if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
        file_status = f"文件 {file.filename} 已存在。"
        return BaseResponse(code=200, msg=file_status)

    with open(file_path, "wb") as f:
        f.write(file_content)

    if file_path:
        file_status = f"文件 {file.filename} 已上传至，请开始提问。"
        return BaseResponse(code=200, msg=file_status)
    else:
        file_status = "文件上传失败，请重新上传"
        return BaseResponse(code=500, msg=file_status)


@blip2_image_qa_router.post("/chat")
async def chat(
        local_image_id: str = Body(..., description="image Base Name", example="kb1"),
        image_name: str = Body(..., description="image Name", example="1.png"),
        question: str = Body(..., description="Question", example="这个图片里面有什么，总结下？"),
        history: List[List[str]] = Body(
            [],
            description="History of previous questions and answers",
            example=[
                [
                    "这个图片里面有什么，总结下？",
                    ""
                ]
            ],
        ),
):
    global llm_model_ins
    file_path = get_file_path(local_image_id,image_name)
    if llm_model_ins:
        llm_model_ins.set_image_path(file_path)
    else:
        file_status = "模型未加载"
        return BaseResponse(code=500, msg=file_status)

    for answer_result in llm_model_ins.generatorAnswer(prompt=question, history=history,
                                                          streaming=True):
        resp = answer_result.llm_output["answer"]
        history = answer_result.history
        pass

    return ChatMessage(
        question=question,
        response=resp,
        history=history,
        source_documents=[],
    )
