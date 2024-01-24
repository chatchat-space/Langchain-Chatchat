import numpy as np
from typing import List, Union, Dict
from langchain.embeddings.base import Embeddings
from configs import (kbs_config, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD,
                     EMBEDDING_MODEL, KB_INFO)
from server.embeddings.core.embeddings_api import embed_texts, aembed_texts
from server.utils import embedding_device


class EmbeddingsFunAdapter(Embeddings):
    _endpoint_host: str
    _endpoint_host_key: str
    _endpoint_host_proxy: str

    def __init__(self,
                 endpoint_host: str,
                 endpoint_host_key: str,
                 endpoint_host_proxy: str,
                 embed_model: str = EMBEDDING_MODEL,
                 ):
        self._endpoint_host = endpoint_host
        self._endpoint_host_key = endpoint_host_key
        self._endpoint_host_proxy = endpoint_host_proxy
        self.embed_model = embed_model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = embed_texts(texts=texts,
                                 endpoint_host=self._endpoint_host,
                                 endpoint_host_key=self._endpoint_host_key,
                                 endpoint_host_proxy=self._endpoint_host_proxy,
                                 embed_model=self.embed_model,
                                 to_query=False).data
        return self._normalize(embeddings=embeddings).tolist()

    def embed_query(self, text: str) -> List[float]:
        embeddings = embed_texts(texts=[text],
                                 endpoint_host=self._endpoint_host,
                                 endpoint_host_key=self._endpoint_host_key,
                                 endpoint_host_proxy=self._endpoint_host_proxy,
                                 embed_model=self.embed_model,
                                 to_query=True).data
        query_embed = embeddings[0]
        query_embed_2d = np.reshape(query_embed, (1, -1))  # 将一维数组转换为二维数组
        normalized_query_embed = self._normalize(embeddings=query_embed_2d)
        return normalized_query_embed[0].tolist()  # 将结果转换为一维数组并返回

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = (await aembed_texts(texts=texts,
                                         endpoint_host=self._endpoint_host,
                                         endpoint_host_key=self._endpoint_host_key,
                                         endpoint_host_proxy=self._endpoint_host_proxy,
                                         embed_model=self.embed_model,
                                         to_query=False)).data
        return self._normalize(embeddings=embeddings).tolist()

    async def aembed_query(self, text: str) -> List[float]:
        embeddings = (await aembed_texts(texts=[text],
                                         endpoint_host=self._endpoint_host,
                                         endpoint_host_key=self._endpoint_host_key,
                                         endpoint_host_proxy=self._endpoint_host_proxy,
                                         embed_model=self.embed_model,
                                         to_query=True)).data
        query_embed = embeddings[0]
        query_embed_2d = np.reshape(query_embed, (1, -1))  # 将一维数组转换为二维数组
        normalized_query_embed = self._normalize(embeddings=query_embed_2d)
        return normalized_query_embed[0].tolist()  # 将结果转换为一维数组并返回

    @staticmethod
    def _normalize(embeddings: List[List[float]]) -> np.ndarray:
        '''
        sklearn.preprocessing.normalize 的替代（使用 L2），避免安装 scipy, scikit-learn
        #TODO 此处内容处理错误
        '''
        norm = np.linalg.norm(embeddings, axis=1)
        norm = np.reshape(norm, (norm.shape[0], 1))
        norm = np.tile(norm, (1, len(embeddings[0])))
        return np.divide(embeddings, norm)


def load_kb_adapter_embeddings(
        kb_name: str,
        embed_device: str = embedding_device(),
        default_embed_model: str = EMBEDDING_MODEL,
) -> "EmbeddingsFunAdapter":
    """
    加载知识库配置的Embeddings模型
    本地模型最终会通过load_embeddings加载
    在线模型会在适配器中直接返回
    :param kb_name:
    :param embed_device:
    :param default_embed_model:
    :return:
    """
    from server.db.repository.knowledge_base_repository import get_kb_detail

    kb_detail = get_kb_detail(kb_name)
    embed_model = kb_detail.get("embed_model", default_embed_model)
    endpoint_host = kb_detail.get("endpoint_host", None)
    endpoint_host_key = kb_detail.get("endpoint_host_key", None)
    endpoint_host_proxy = kb_detail.get("endpoint_host_proxy", None)

    return EmbeddingsFunAdapter(endpoint_host=endpoint_host,
                                endpoint_host_key=endpoint_host_key,
                                endpoint_host_proxy=endpoint_host_proxy,
                                embed_model=embed_model)


def load_temp_adapter_embeddings(
        endpoint_host: str,
        endpoint_host_key: str,
        endpoint_host_proxy: str,
        embed_device: str = embedding_device(),
        default_embed_model: str = EMBEDDING_MODEL,
) -> "EmbeddingsFunAdapter":
    """
    加载临时的Embeddings模型
    本地模型最终会通过load_embeddings加载
    在线模型会在适配器中直接返回
    :param endpoint_host:
    :param endpoint_host_key:
    :param endpoint_host_proxy:
    :param embed_device:
    :param default_embed_model:
    :return:
    """

    return EmbeddingsFunAdapter(endpoint_host=endpoint_host,
                                endpoint_host_key=endpoint_host_key,
                                endpoint_host_proxy=endpoint_host_proxy,
                                embed_model=default_embed_model)
