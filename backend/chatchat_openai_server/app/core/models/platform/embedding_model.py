from abc import abstractmethod
from typing import List, Union

from app._types.embedding_object import ListEmbedding


class EmbeddingModel:

    def __init__(self, config):
        ...

    @abstractmethod
    def embeddings(self, model: str,
                   input: Union[List, str],
                   dimensions: int) -> ListEmbedding:
        ...
