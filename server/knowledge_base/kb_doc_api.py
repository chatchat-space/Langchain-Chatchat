import os
import urllib
from fastapi import File, Form, UploadFile
from server.utils import BaseResponse, ListResponse
from server.knowledge_base.utils import (validate_kb_name)
from fastapi.responses import StreamingResponse
import json
from server.knowledge_base.utils import KnowledgeFile, KBServiceFactory, list_docs_from_folder
from server.knowledge_base.kb_service.base import SupportedVSType
from server.knowledge_base.kb_service.faiss_kb_service import refresh_vs_cache


async def list_docs(knowledge_base_name: str):
    if not validate_kb_name(knowledge_base_name):
        return ListResponse(code=403, msg="Don't attack me", data=[])

    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return ListResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}", data=[])
    else:
        all_doc_names = kb.list_docs()
    return ListResponse(data=all_doc_names)


async def upload_doc(file: UploadFile = File(description="上传文件"),
                     knowledge_base_name: str = Form(..., description="知识库名称", example="kb1"),
                     override: bool = Form(False, description="覆盖已有文件", example=False),
                     ):
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    file_content = await file.read()  # 读取上传文件的内容

    kb_file = KnowledgeFile(filename=file.filename,
                            knowledge_base_name=knowledge_base_name)

    if (os.path.exists(kb_file.filepath)
            and not override
            and os.path.getsize(kb_file.filepath) == len(file_content)
    ):
        # TODO: filesize 不同后的处理
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
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

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
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    async def output(kb):
        kb.clear_vs()
        print(f"start to recreate vector store of {kb.kb_name}")
        docs = list_docs_from_folder(knowledge_base_name)
        print(docs)
        for i, filename in enumerate(docs):
            yield json.dumps({
                "total": len(docs),
                "finished": i,
                "doc": filename,
            })
            kb_file = KnowledgeFile(filename=filename,
                                    knowledge_base_name=kb.kb_name)
            print(f"processing {kb_file.filepath} to vector store.")
            kb.add_doc(kb_file)
        if kb.vs_type == SupportedVSType.FAISS:
            refresh_vs_cache(knowledge_base_name)

    return StreamingResponse(output(kb), media_type="text/event-stream")
