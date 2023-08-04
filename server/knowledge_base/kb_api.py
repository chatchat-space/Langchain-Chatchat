import urllib
from server.utils import BaseResponse, ListResponse
from server.knowledge_base.utils import validate_kb_name
from server.knowledge_base.knowledge_base import KnowledgeBase


async def list_kbs():
    # Get List of Knowledge Base
    return ListResponse(data=KnowledgeBase.list_kbs())


async def create_kb(knowledge_base_name: str,
                    vector_store_type: str = "faiss"):
    # Create selected knowledge base
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")
    if knowledge_base_name is None or knowledge_base_name.strip() == "":
        return BaseResponse(code=404, msg="知识库名称不能为空，请重新填写知识库名称")
    if KnowledgeBase.exists(knowledge_base_name):
        return BaseResponse(code=404, msg=f"已存在同名知识库 {knowledge_base_name}")
    kb = KnowledgeBase(knowledge_base_name=knowledge_base_name,
                       vector_store_type=vector_store_type)
    kb.create()
    return BaseResponse(code=200, msg=f"已新增知识库 {knowledge_base_name}")


async def delete_kb(knowledge_base_name: str):
    # Delete selected knowledge base
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")
    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)

    if not KnowledgeBase.exists(knowledge_base_name):
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    status = KnowledgeBase.delete(knowledge_base_name)
    if status:
        return BaseResponse(code=200, msg=f"成功删除知识库 {knowledge_base_name}")
    else:
        return BaseResponse(code=500, msg=f"删除知识库失败 {knowledge_base_name}")
