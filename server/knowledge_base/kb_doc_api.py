import os
import urllib
import shutil
from fastapi import File, Form, UploadFile
from server.utils import BaseResponse, ListResponse
from server.knowledge_base.utils import (validate_kb_name, get_kb_path, get_doc_path,
                                         get_file_path, refresh_vs_cache, get_vs_path)
from fastapi.responses import StreamingResponse
import json
from server.knowledge_base.knowledge_file import KnowledgeFile
from server.knowledge_base.knowledge_base import KnowledgeBase


async def list_docs(knowledge_base_name: str):
    if not validate_kb_name(knowledge_base_name):
        return ListResponse(code=403, msg="Don't attack me", data=[])

    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    kb_path = get_kb_path(knowledge_base_name)
    if not os.path.exists(kb_path):
        return ListResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}", data=[])
    else:
        all_doc_names = KnowledgeBase.load(knowledge_base_name=knowledge_base_name).list_docs()
    return ListResponse(data=all_doc_names)


async def upload_doc(file: UploadFile = File(description="上传文件"),
                     knowledge_base_name: str = Form(..., description="知识库名称", example="kb1"),
                     override: bool = Form(False, description="覆盖已有文件", example=False),
                     ):
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    if not KnowledgeBase.exists(knowledge_base_name=knowledge_base_name):
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    kb = KnowledgeBase.load(knowledge_base_name=knowledge_base_name)

    file_content = await file.read()  # 读取上传文件的内容

    kb_file = KnowledgeFile(filename=file.filename,
                            knowledge_base_name=knowledge_base_name)

    if (os.path.exists(kb_file.filepath)
        and not override
        and os.path.getsize(kb_file.filepath) == len(file_content)
    ):
        file_status = f"文件 {kb_file.filename} 已存在。"
        return BaseResponse(code=404, msg=file_status)

    try:
        with open(kb_file.filepath, "wb") as f:
            f.write(file_content)
    except Exception as e:
        return BaseResponse(code=500, msg=f"{kb_file.filename} 文件上传失败，报错信息为: {e}")

    kb.add_doc(kb_file)
    return BaseResponse(code=200, msg=f"成功上传文件 {kb_file.filename}")


async def delete_doc(knowledge_base_name: str,
                     doc_name: str,
                     ):
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    if not KnowledgeBase.exists(knowledge_base_name=knowledge_base_name):
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    kb = KnowledgeBase.load(knowledge_base_name=knowledge_base_name)
    if not kb.exist_doc(doc_name):
        return BaseResponse(code=404, msg=f"未找到文件 {doc_name}")
    kb_file = KnowledgeFile(filename=doc_name,
                            knowledge_base_name=knowledge_base_name)
    kb.delete_doc(kb_file)
    return BaseResponse(code=200, msg=f"{kb_file.filename} 文件删除成功")
    # return BaseResponse(code=500, msg=f"{kb_file.filename} 文件删除失败")


async def update_doc():
    # TODO: 替换文件
    # refresh_vs_cache(knowledge_base_name)
    pass

async def download_doc():
    # TODO: 下载文件
    pass


async def recreate_vector_store(knowledge_base_name: str):
    '''
    recreate vector store from the content.
    this is usefull when user can copy files to content folder directly instead of upload through network.
    '''
    async def output(kb_name):
        vs_path = get_vs_path(kb_name)
        if os.path.isdir(vs_path):
            shutil.rmtree(vs_path)
        os.mkdir(vs_path)
        print(f"start to recreate vectore in {vs_path}")

        docs = (await list_docs(kb_name)).data
        for i, filename in enumerate(docs):
            kb_file = KnowledgeFile(filename=filename,
                                    knowledge_base_name=kb_name)
            print(f"processing {kb_file.filepath} to vector store.")
            kb = KnowledgeBase.load(knowledge_base_name=kb_name)
            kb.add_doc(kb_file)
            yield json.dumps({
                "total": len(docs),
                "finished": i + 1,
                "doc": filename,
            })
    
    return StreamingResponse(output(knowledge_base_name), media_type="text/event-stream")
