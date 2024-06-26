from typing import Any, List, Optional, Sequence
import torch
from sentence_transformers import CrossEncoder
from transformers import AutoTokenizer
from langchain_core.documents import Document
from langchain.callbacks.manager import Callbacks
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from llama_index.legacy.bridge.pydantic import Field, PrivateAttr
from server.utils import embedding_device
from configs import (LLM_MODELS,
                     VECTOR_SEARCH_TOP_K,
                     SCORE_THRESHOLD,
                     TEMPERATURE,
                     USE_RERANKER,
                     RERANKER_MODEL,
                     RERANKER_MAX_LENGTH,
                     MODEL_PATH)
class LangchainReranker(BaseDocumentCompressor):
    """Document compressor that uses `Cohere Rerank API`."""
    model_name_or_path: str = Field()
    _model: Any = PrivateAttr()
    top_n: int = Field()
    device: str = Field()
    max_length: int = Field()
    batch_size: int = Field()
    num_workers: int = Field()

    def __init__(
        self,
        model_name_or_path: str,
        top_n: int = 3,
        device: str = "cuda",
        max_length: int = 1024,
        batch_size: int = 32,
        num_workers: int = 0,
    ):
        self._model = CrossEncoder(model_name=model_name_or_path, device=device)
        super().__init__(
            top_n=top_n,
            model_name_or_path=model_name_or_path,
            device=device,
            max_length=max_length,
            batch_size=batch_size,
            num_workers=num_workers,
        )
    def compress_documents(
        self,
        documents: List[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        if len(documents) == 0:
            return []
        
        _docs = [d[0].page_content for d in documents]
        sentence_pairs = [[query, _doc] for _doc in _docs]
        # 批量处理文本数据，每个批次包含多个句子对
        batch_results = []
        for batch in self._get_batches(sentence_pairs, self.batch_size):
            # CrossEncoder的predict方法可以接受列表形式的句子对，并自动处理批次
            scores = self._model.predict(batch)
            batch_results.extend(scores)
        
        # 根据得分选择top_n个文档
        scores = torch.tensor(batch_results)
        top_k = self.top_n if self.top_n < len(scores) else len(scores)
        values, indices = scores.topk(top_k)

        final_results = []
        for index in indices:
            doc = documents[index]
            doc[0].metadata["relevance_score"] = values[index].item()
            final_results.append(doc)
        return final_results

    def _get_batches(self, data, batch_size):
        return [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
