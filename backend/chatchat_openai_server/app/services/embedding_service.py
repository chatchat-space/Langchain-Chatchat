from typing import Union

from app.core.models.model_factory import embedding_model_handler


class EmbeddingService:

    @staticmethod
    def create_embeddings(input: Union[str, list[str]],
                          model: str = 'embedding-2',
                          encoding_format: str = 'float',
                          dimensions: int = 2048,
                          user: str = None):
        # 调用OpenAI的Embedding API生成文本的嵌入向量
        embedding_model_handler_obj = embedding_model_handler('zhipuai', 'embedding_model')
        embedding_model = embedding_model_handler_obj(
            {'api_key': '24c2cdd3ff19e270ae444a72a6df05fe.wXbgHRoBOcYIFFWV'}
        )
        return embedding_model.embeddings(
            input,
            model=model,
            encoding_format=encoding_format,
            dimensions=dimensions,
            user=user
        )
