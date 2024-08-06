from app.core.models.platform.embedding_model import EmbeddingModel
from app.core.models.platform.zhipuai.zhipuai_embedding_model import ZhipuaiEmbeddingModel

model_class = {
    'zhipuai': {
        'embedding_model': ZhipuaiEmbeddingModel,
        'lang_model': ZhipuaiEmbeddingModel,
        'rerank_model': ZhipuaiEmbeddingModel
    }
}


class ModelFactory:

    def __init__(self, model_class):
        self.model_class = model_class

    def create(self, **kwargs):
        return self.model_class(**kwargs)


def embedding_model_handler(platform: str, model_type: str):
    return model_class[platform][model_type]
