from typing import Union, List

from zhipuai import ZhipuAI

from app.core.models.platform.embedding_model import EmbeddingModel
from app._types.embedding_object import ListEmbedding, Usage, EmbeddingObject


class ZhipuaiEmbeddingModel(EmbeddingModel):
    client: ZhipuAI

    def __init__(self, config, client: ZhipuAI = None):
        super().__init__(config)
        if client:
            self.client = client
        else:
            self.client = ZhipuAI(api_key=config.get('api_key'))

    def embeddings(self
                   , input: Union[List, str]
                   , model: str
                   , encoding_format='float'
                   , dimensions: int = 2048
                   , user=None) -> ListEmbedding:
        embeddings_responded = self.client.embeddings.create(input=input
                                                             , model=model
                                                             , encoding_format=encoding_format)
        return ListEmbedding(
            data=[EmbeddingObject(
                index=embedding.index,
                embedding=embedding.embedding,
            ) for embedding in embeddings_responded.data],
            model=embeddings_responded.model,
            usage=Usage(
                prompt_tokens=embeddings_responded.usage.prompt_tokens,
                total_tokens=embeddings_responded.usage.total_tokens,
            ),
        )
