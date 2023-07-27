import os
import urllib
import shutil
from configs.model_config import KB_ROOT_PATH
from server.utils import BaseResponse, ListResponse
from server.knowledge_base.utils import validate_kb_name, get_kb_path, get_vs_path


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

    return ListResponse(data=all_doc_ids)


async def create_kb(knowledge_base_name: str):
    # Create selected knowledge base
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")
    if knowledge_base_name is None or knowledge_base_name.strip() == "":
        return BaseResponse(code=404, msg="知识库名称不能为空，请重新填写知识库名称")
    if os.path.exists(get_kb_path(knowledge_base_name)):
        return BaseResponse(code=404, msg=f"已存在同名知识库 {knowledge_base_name}")
    if not os.path.exists(os.path.join(KB_ROOT_PATH, knowledge_base_name, "content")):
        os.makedirs(os.path.join(KB_ROOT_PATH, knowledge_base_name, "content"))
    if not os.path.exists(os.path.join(KB_ROOT_PATH, knowledge_base_name, "vector_store")):
        os.makedirs(get_vs_path(knowledge_base_name))
    return BaseResponse(code=200, msg=f"已新增知识库 {knowledge_base_name}")


async def delete_kb(knowledge_base_name: str):
    # Delete selected knowledge base
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")
    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)
    kb_path = get_kb_path(knowledge_base_name)
    if not os.path.exists(kb_path):
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")
    shutil.rmtree(kb_path)
    return BaseResponse(code=200, msg=f"成功删除知识库 {knowledge_base_name}")
