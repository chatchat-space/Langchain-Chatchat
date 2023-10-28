from configs import EMBEDDING_MODEL
from server.utils import BaseResponse, list_online_embed_models
from server.knowledge_base.kb_service.base import embed_texts
from fastapi import Body
from typing import List


online_embed_models = list_online_embed_models()

def embed_texts_endpoint(
    texts: List[str] = Body(..., description="要嵌入的文本列表", examples=[["hello", "world"]]),
    embed_model: str = Body(EMBEDDING_MODEL, description=f"使用的嵌入模型，除了本地部署的Embedding模型，也支持在线API({online_embed_models})提供的嵌入服务。"),
    to_query: bool = Body(False, description="向量是否用于查询。有些模型如Minimax对存储/查询的向量进行了区分优化。"),
) -> BaseResponse:
    '''
    对文本进行向量化，返回 BaseResponse(data=List[List[float]])
    '''
    return embed_texts(texts=texts, embed_model=embed_model, to_query=to_query)
