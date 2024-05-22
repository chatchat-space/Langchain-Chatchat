from decimal import Decimal
from typing import List

from model_providers.core.model_runtime.entities.model_entities import ModelUsage

from ...._models import BaseModel


class EmbeddingUsage(ModelUsage):
    """
    Model class for embedding usage.
    """

    tokens: int
    total_tokens: int
    unit_price: Decimal
    price_unit: Decimal
    total_price: Decimal
    currency: str
    latency: float


class TextEmbeddingResult(BaseModel):
    """
    Model class for text embedding result.
    """

    model: str
    embeddings: List[List[float]]
    usage: EmbeddingUsage
