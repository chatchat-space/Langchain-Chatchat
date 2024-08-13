from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.embedding_service import EmbeddingService
from app._types.embedding_object import ListEmbedding

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class CreateEmbeddingsRequest(BaseModel):
    input: Union[str, list[str]]
    model: str = 'embedding-2'
    encoding_format: str = 'float'
    dimensions: int = 2048
    user: str = None


# id 模型id(platform_model_type_model_name)  平台 模型类型 模型名称 别名 模型类 配置 加载来源(配置文件,手动配置,远程加载) 模型实例信息
# id model_id   platform model_type model_name alias_name model_class config loader_source model_instance_info
@router.post("/", response_model=ListEmbedding)
def create_embeddings(embeddings_request: CreateEmbeddingsRequest):
    return EmbeddingService.create_embeddings(**embeddings_request.dict())
