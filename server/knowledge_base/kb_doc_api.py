import os
import urllib
import shutil
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from fastapi import File, Form, UploadFile
from server.utils import BaseResponse, ListResponse, torch_gc
from server.knowledge_base.utils import (validate_kb_name, get_kb_path, get_doc_path,
                                         get_vs_path, get_file_path, file2text)
from configs.model_config import embedding_model_dict, EMBEDDING_MODEL, EMBEDDING_DEVICE
from server.knowledge_base.utils import load_embeddings, refresh_vs_cache


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
                     ):
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    saved_path = get_doc_path(knowledge_base_name)
    if not os.path.exists(saved_path):
        return BaseResponse(code=404, msg="未找到知识库 {knowledge_base_name}")

    file_content = await file.read()  # 读取上传文件的内容

    file_path = os.path.join(saved_path, file.filename)
    if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
        file_status = f"文件 {file.filename} 已存在。"
        return BaseResponse(code=404, msg=file_status)

    with open(file_path, "wb") as f:
        f.write(file_content)

    vs_path = get_vs_path(knowledge_base_name)
    # TODO: 重写知识库生成/添加逻辑
    filepath = get_file_path(knowledge_base_name, file.filename)
    docs = file2text(filepath)
    loaded_files = [file]
    embeddings = load_embeddings(embedding_model_dict[EMBEDDING_MODEL], EMBEDDING_DEVICE)
    if os.path.exists(vs_path) and "index.faiss" in os.listdir(vs_path):
        vector_store = FAISS.load_local(vs_path, embeddings)
        vector_store.add_documents(docs)
        torch_gc()
    else:
        if not os.path.exists(vs_path):
            os.makedirs(vs_path)
        vector_store = FAISS.from_documents(docs, embeddings)  # docs 为Document列表
        torch_gc()
    vector_store.save_local(vs_path)
    if len(loaded_files) > 0:
        file_status = f"成功上传文件 {file.filename}"
        refresh_vs_cache(knowledge_base_name)
        return BaseResponse(code=200, msg=file_status)
    else:
        file_status = f"上传文件 {file.filename} 失败"
        return BaseResponse(code=500, msg=file_status)


async def delete_doc(knowledge_base_name: str,
                     doc_name: str,
                     ):
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")

    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    if not os.path.exists(get_kb_path(knowledge_base_name)):
        return BaseResponse(code=404, msg=f"Knowledge base {knowledge_base_name} not found")
    doc_path = get_file_path(knowledge_base_name, doc_name)
    if os.path.exists(doc_path):
        os.remove(doc_path)
        remain_docs = await list_docs(knowledge_base_name)
        if len(remain_docs.data) == 0:
            shutil.rmtree(get_kb_path(knowledge_base_name), ignore_errors=True)
            return BaseResponse(code=200, msg=f"document {doc_name} delete success")
        else:
            # TODO: 重写从向量库中删除文件
            status = ""  # local_doc_qa.delete_file_from_vector_store(doc_path, get_vs_path(knowledge_base_name))
            if "success" in status:
                refresh_vs_cache(knowledge_base_name)
                return BaseResponse(code=200, msg=f"document {doc_name} delete success")
            else:
                return BaseResponse(code=500, msg=f"document {doc_name} delete fail")
    else:
        return BaseResponse(code=404, msg=f"document {doc_name} not found")


async def update_doc():
    # TODO: 替换文件
    # refresh_vs_cache(knowledge_base_name)
    pass

async def download_doc():
    # TODO: 下载文件
    pass
