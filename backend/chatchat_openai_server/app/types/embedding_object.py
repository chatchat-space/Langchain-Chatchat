from typing import List

from pydantic import BaseModel


class EmbeddingObject(BaseModel):
    index: int = 0
    embedding: list[float] = []
    object: str = 'embedding'


class Usage(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0


class ListEmbedding(BaseModel):
    object: str = 'list'
    data: List[EmbeddingObject] = []
    model: str = ''
    usage: Usage = None
