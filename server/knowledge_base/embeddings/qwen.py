from abc import ABC
from typing import List

from langchain.schema.embeddings import Embeddings


class QwenEmbeddings(Embeddings, ABC):

    def __init__(self, api_key: str):
        self.api_key = api_key

    def embed_query(self, text: str) -> List[float]:
        import dashscope
        textEmbedding = dashscope.TextEmbedding()
        response = textEmbedding.call(
            model=textEmbedding.Models.text_embedding_v1,
            api_key=self.api_key,
            input=text
        )

        if response["status_code"] == 200:
            return response["output"]["embeddings"][0]["embedding"]
        else:
            raise
            return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import dashscope
        textEmbedding = dashscope.TextEmbedding()

        # 定义每个子列表的长度限制
        segment_size = 25
        input_segments = [texts[i:i + segment_size] for i in range(0, len(texts), segment_size)]

        # 对每个子列表分别调用 TextEmbedding.call 方法
        responses = []
        for segment in input_segments:
            response = textEmbedding.call(
                model=textEmbedding.Models.text_embedding_v1,
                api_key=self.api_key,
                input=segment
            )
            responses.append(response)

            # 合并每个子列表的嵌入结果
        embeddings = []
        for response in responses:
            if response["status_code"] == 200:
                embeddings.extend([embedding["embedding"] for embedding in response["output"]["embeddings"]])
            else:
                embeddings.extend([])

        return embeddings