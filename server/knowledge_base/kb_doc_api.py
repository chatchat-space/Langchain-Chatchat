import os
import urllib
from fastapi import File, Form, Body, Query, UploadFile
from configs.model_config import (DEFAULT_VS_TYPE, EMBEDDING_MODEL, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD)
from server.utils import BaseResponse, ListResponse
from server.knowledge_base.utils import validate_kb_name, list_docs_from_folder, KnowledgeFile
from fastapi.responses import StreamingResponse, FileResponse
import json
from server.knowledge_base.kb_service.base import KBServiceFactory
from typing import List, Dict
from langchain.docstore.document import Document


class DocumentWithScore(Document):
    score: float = None


def search_docs(query: str = Body(..., description="用户输入", examples=["你好"]),
                knowledge_base_name: str = Body(..., description="知识库名称", examples=["samples"]),
                top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                score_threshold: float = Body(SCORE_THRESHOLD, description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右", ge=0, le=1),
                ) -> List[DocumentWithScore]:
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return {"code": 404, "msg": f"未找到知识库 {knowledge_base_name}", "docs": []}
    docs = kb.search_docs(query, top_k, score_threshold)
    data = [DocumentWithScore(**x[0].dict(), score=x[1]) for x in docs]

    return data


async def list_docs(
    knowledge_base_name: str
):
    if not validate_kb_name(knowledge_base_name):
        return ListResponse(code=403, msg="Don't attack me", data=[])

    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return ListResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}", data=[])
    else:
        all_doc_names = kb.list_docs()
    return ListResponse(data=all_doc_names)


async def upload_doc(file: UploadFile = File(..., description="上传文件"),
                     knowledge_base_name: str = Form(..., description="知识库名称", examples=["kb1"]),
                     override: bool = Form(False, description="覆盖已有文件"),
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


async def delete_doc(knowledge_base_name: str = Body(..., examples=["samples"]),
                     doc_name: str = Body(..., examples=["file_name.md"]),
                     delete_content: bool = Body(False),
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
    kb.delete_doc(kb_file, delete_content)
    return BaseResponse(code=200, msg=f"{kb_file.filename} 文件删除成功")
    # return BaseResponse(code=500, msg=f"{kb_file.filename} 文件删除失败")


async def update_doc(
        knowledge_base_name: str = Body(..., examples=["samples"]),
        file_name: str = Body(..., examples=["file_name"]),
    ):
    '''
    更新知识库文档
    '''
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    kb_file = KnowledgeFile(filename=file_name,
                            knowledge_base_name=knowledge_base_name)

    if os.path.exists(kb_file.filepath):
        kb.update_doc(kb_file)
        return BaseResponse(code=200, msg=f"成功更新文件 {kb_file.filename}")
    else:
        return BaseResponse(code=500, msg=f"{kb_file.filename} 文件更新失败")


async def download_doc(
        knowledge_base_name: str = Query(..., examples=["samples"]),
        file_name: str = Query(..., examples=["test.txt"]),
    ):
    '''
    下载知识库文档
    '''
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    kb_file = KnowledgeFile(filename=file_name,
                            knowledge_base_name=knowledge_base_name)

    if os.path.exists(kb_file.filepath):
        return FileResponse(
            path=kb_file.filepath,
            filename=kb_file.filename,
            media_type="multipart/form-data")
    else:
        return BaseResponse(code=500, msg=f"{kb_file.filename} 读取文件失败")




async def recreate_vector_store(
        knowledge_base_name: str = Body(..., examples=["samples"]),
        allow_empty_kb: bool = Body(True),
        vs_type: str = Body(DEFAULT_VS_TYPE),
        embed_model: str = Body(EMBEDDING_MODEL),
    ):
    '''
    recreate vector store from the content.
    this is usefull when user can copy files to content folder directly instead of upload through network.
    by default, get_service_by_name only return knowledge base in the info.db and having document files in it.
    set allow_empty_kb to True make it applied on empty knowledge base which it not in the info.db or having no documents.
    '''
    kb = KBServiceFactory.get_service(knowledge_base_name, vs_type, embed_model)
    if not kb.exists() and not allow_empty_kb:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    async def output(kb):
        kb.create_kb()
        kb.clear_vs()
        docs = list_docs_from_folder(knowledge_base_name)
        for i, doc in enumerate(docs):
            try:
                kb_file = KnowledgeFile(doc, knowledge_base_name)
                yield json.dumps({
                    "total": len(docs),
                    "finished": i,
                    "doc": doc,
                }, ensure_ascii=False)
                kb.add_doc(kb_file)
            except Exception as e:
                print(e)

    return StreamingResponse(output(kb), media_type="text/event-stream")
