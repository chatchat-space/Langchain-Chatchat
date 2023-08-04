import os
import urllib
import shutil
from fastapi import File, Form, UploadFile
from server.utils import BaseResponse, ListResponse
from server.knowledge_base.utils import (validate_kb_name, get_kb_path, get_doc_path,
                                         get_file_path, file2text, docs2vs,
                                         refresh_vs_cache, get_vs_path, )
from fastapi.responses import StreamingResponse
import json
import shutil


async def list_docs(knowledge_base_name: str):
    if not validate_kb_name(knowledge_base_name):
        return ListResponse(code=403, msg="Don't attack me", data=[])

    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    kb_path = get_kb_path(knowledge_base_name)
    local_doc_folder = get_doc_path(knowledge_base_name)
    if not os.path.exists(kb_path):
        return ListResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}", data=[])
    if not os.path.exists(local_doc_folder):
        all_doc_names = []
    else:
        all_doc_names = [
            doc
            for doc in os.listdir(local_doc_folder)
            if os.path.isfile(os.path.join(local_doc_folder, doc))
        ]
    return ListResponse(data=all_doc_names)


async def upload_doc(file: UploadFile = File(description="上传文件"),
                     knowledge_base_name: str = Form(..., description="知识库名称", example="kb1"),
                     override: bool = Form(False, description="覆盖已有文件", example=False),
                     ):
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    saved_path = get_doc_path(knowledge_base_name)
    if not os.path.exists(saved_path):
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    file_content = await file.read()  # 读取上传文件的内容

    file_path = os.path.join(saved_path, file.filename)
    if (os.path.exists(file_path)
        and not override
        and os.path.getsize(file_path) == len(file_content)
    ):
        file_status = f"文件 {file.filename} 已存在。"
        return BaseResponse(code=404, msg=file_status)

    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        return BaseResponse(code=500, msg=f"{file.filename} 文件上传失败，报错信息为: {e}")

    filepath = get_file_path(knowledge_base_name, file.filename)
    docs = file2text(filepath)
    docs2vs(docs, knowledge_base_name)

    return BaseResponse(code=200, msg=f"成功上传文件 {file.filename}")


async def delete_doc(knowledge_base_name: str,
                     doc_name: str,
                     ):
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    if not os.path.exists(get_kb_path(knowledge_base_name)):
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")
    doc_path = get_file_path(knowledge_base_name, doc_name)
    if os.path.exists(doc_path):
        os.remove(doc_path)
        remain_docs = await list_docs(knowledge_base_name)
        if len(remain_docs.data) == 0:
            shutil.rmtree(get_kb_path(knowledge_base_name), ignore_errors=True)
            return BaseResponse(code=200, msg=f"{doc_name} 文件删除成功")
        else:
            # TODO: 重写从向量库中删除文件
            status = ""  # local_doc_qa.delete_file_from_vector_store(doc_path, get_vs_path(knowledge_base_name))
            if "success" in status:
                refresh_vs_cache(knowledge_base_name)
                return BaseResponse(code=200, msg=f"{doc_name} 文件删除成功")
            else:
                return BaseResponse(code=500, msg=f"{doc_name} 文件删除失败")
    else:
        return BaseResponse(code=404, msg=f"未找到文件 {doc_name}")


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
    async def output(kb):
        vs_path = get_vs_path(kb)
        if os.path.isdir(vs_path):
            shutil.rmtree(vs_path)
        os.mkdir(vs_path)
        print(f"start to recreate vectore in {vs_path}")

        docs = (await list_docs(kb)).data
        for i, filename in enumerate(docs):
            filepath = get_file_path(kb, filename)
            print(f"processing {filepath} to vector store.")
            docs = file2text(filepath)
            docs2vs(docs, kb)
            yield json.dumps({
                "total": len(docs),
                "finished": i + 1,
                "doc": filename,
            })
    
    return StreamingResponse(output(knowledge_base_name), media_type="text/event-stream")
