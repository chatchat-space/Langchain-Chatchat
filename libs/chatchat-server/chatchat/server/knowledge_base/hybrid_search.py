"""混合检索（向量 + BM25 RRF 融合）与 LLM Rerank 实现（改动2）。

检索方法由 kb_settings.yaml 的 SEARCH_METHOD 控制：
- vector:        纯向量检索
- ensemble:      原 EnsembleRetriever 行为
- hybrid_rrf:    向量 + BM25(jieba) RRF 融合
- hybrid_rerank: hybrid_rrf 基础上再用 LLM(bge-m3) 对 query-doc 相关性打分重排

设计要点：
- BM25 索引按 (kb_name, vector_name) 进程内缓存，文档数变化时自动重建
- Rerank 分数 (query, doc_id) 进程内 LRU 缓存，避免重复调用 Ollama
- Rerank 用 bge-m3 的 embedding 模拟交叉编码：sim(query_emb, doc_emb)，
  query 拼上"为这个句子生成表示以用于检索相关文章：" 前缀提升效果
"""
from __future__ import annotations

import threading
from collections import OrderedDict
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from langchain.docstore.document import Document

from chatchat.settings import Settings
from chatchat.server.utils import build_logger

logger = build_logger()

# ---------------------------------------------------------------------------
# BM25 索引缓存（按 kb 维度）
# ---------------------------------------------------------------------------
_bm25_cache: "OrderedDict[Tuple[str, str], Tuple[int, object]]" = OrderedDict()
_bm25_lock = threading.Lock()
_BM25_MAX_CACHE = 4


def _tokenize_zh(text: str) -> List[str]:
    import jieba

    return [t for t in jieba.lcut_for_search(text) if t.strip()]


def get_bm25_retriever(kb_key: Tuple[str, str], docs: List[Document], top_k: int):
    """获取（或构建）BM25Retriever。docs 数量变化时重建索引。"""
    from langchain_community.retrievers import BM25Retriever

    with _bm25_lock:
        cached = _bm25_cache.get(kb_key)
        if cached is not None and cached[0] == len(docs):
            retriever = cached[1]
            retriever.k = top_k
            _bm25_cache.move_to_end(kb_key)
            return retriever

    retriever = BM25Retriever.from_documents(docs, preprocess_func=_tokenize_zh)
    retriever.k = top_k
    with _bm25_lock:
        _bm25_cache[kb_key] = (len(docs), retriever)
        _bm25_cache.move_to_end(kb_key)
        while len(_bm25_cache) > _BM25_MAX_CACHE:
            _bm25_cache.popitem(last=False)
    return retriever


def drop_bm25_cache(kb_key: Optional[Tuple[str, str]] = None):
    """知识库文档变化时调用；kb_key 为 None 时清空全部。"""
    with _bm25_lock:
        if kb_key is None:
            _bm25_cache.clear()
        else:
            _bm25_cache.pop(kb_key, None)


# ---------------------------------------------------------------------------
# RRF 融合
# ---------------------------------------------------------------------------
def rrf_fuse(rank_lists: List[List[str]], k: int = 60) -> "OrderedDict[str, float]":
    """Reciprocal Rank Fusion：多路召回的 doc_id 排名列表 -> 融合分数。

    score(d) = sum( 1 / (k + rank_i(d)) )，未出现的路不贡献分数。
    """
    scores: "OrderedDict[str, float]" = OrderedDict()
    for ranking in rank_lists:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    # 分数降序
    return OrderedDict(sorted(scores.items(), key=lambda x: -x[1]))


# ---------------------------------------------------------------------------
# LLM Rerank（embedding 相关度模拟）
# ---------------------------------------------------------------------------
QUERY_PREFIX = "为这个句子生成表示以用于检索相关文章："

_rerank_cache: "OrderedDict[Tuple[str, str], float]" = OrderedDict()
_rerank_lock = threading.Lock()
_RERANK_CACHE_MAX = 2048


def _embed(texts: List[str], embed_model: str) -> List[List[float]]:
    """调用 chatchat 的 Embeddings（走 Ollama）批量向量化。"""
    from chatchat.server.utils import get_Embeddings

    emb = get_Embeddings(embed_model=embed_model)
    return emb.embed_documents(texts)


def _cosine(a: List[float], b: List[float]) -> float:
    import math

    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def llm_rerank(
    query: str,
    docs: List[Document],
    doc_ids: List[str],
    embed_model: str,
    top_n: Optional[int] = None,
) -> List[Tuple[Document, float]]:
    """对候选文档按与 query 的 embedding 余弦相似度重排。

    query 向量做了检索前缀增强；doc 向量直接用原文（与建库时一致）。
    返回 (Document, score) 列表，按分数降序。
    """
    if not docs:
        return []

    # 1) query embedding（可缓存）
    with _rerank_lock:
        pass  # query 粒度缓存意义不大（每次 query 不同），直接算

    q_vec = _embed([QUERY_PREFIX + query], embed_model)[0]

    # 2) doc 向量：优先用缓存；未命中的批量计算
    need: List[int] = []
    for i, doc_id in enumerate(doc_ids):
        if (query, doc_id) in _rerank_cache:
            continue
        need.append(i)

    if need:
        texts = [docs[i].page_content for i in need]
        vecs = _embed(texts, embed_model)
        with _rerank_lock:
            for i, vec in zip(need, vecs):
                _rerank_cache[(query, doc_ids[i])] = _cosine(q_vec, vec)
                _rerank_cache.move_to_end((query, doc_ids[i]))
                if len(_rerank_cache) > _RERANK_CACHE_MAX:
                    _rerank_cache.popitem(last=False)

    scored: List[Tuple[Document, float]] = []
    with _rerank_lock:
        for doc, doc_id in zip(docs, doc_ids):
            scored.append((doc, _rerank_cache.get((query, doc_id), 0.0)))
    scored.sort(key=lambda x: -x[1])
    if top_n is not None:
        scored = scored[:top_n]
    return scored


# ---------------------------------------------------------------------------
# 统一检索入口
# ---------------------------------------------------------------------------
def hybrid_search(
    vectorstore,
    query: str,
    top_k: int,
    score_threshold: float,
    kb_key: Tuple[str, str],
    embed_model: str,
    method: str = None,
) -> List[Tuple[Document, float]]:
    """混合检索统一入口，返回 (Document, score)。

    method 来自 Settings.kb_settings.SEARCH_METHOD：
    - vector / ensemble：保持原行为（ensemble 走原 EnsembleRetriever）
    - hybrid_rrf：RRF 融合分数
    - hybrid_rerank：rerank 余弦分数
    """
    method = method or getattr(Settings.kb_settings, "SEARCH_METHOD", "vector")

    if method == "vector":
        docs_and_scores = vectorstore.similarity_search_with_score(query, k=top_k)
        # FAISS 返回的是距离（越小越好），归一化为"越大越好"的分数保持接口一致
        return [(d, 1.0 / (1.0 + float(s))) for d, s in docs_and_scores]

    if method == "ensemble":
        # 原 EnsembleRetriever 行为（无分数概念，给固定 0.0）
        from chatchat.server.file_rag.utils import get_Retriever

        retriever = get_Retriever("ensemble").from_vectorstore(
            vectorstore, top_k=top_k, score_threshold=score_threshold
        )
        return [(d, 0.0) for d in retriever.get_relevant_documents(query)]

    recall_k = int(getattr(Settings.kb_settings, "HYBRID_RECALL_K", 8))
    bm25_k = int(getattr(Settings.kb_settings, "BM25_RECALL_K", 8))
    rrf_k = int(getattr(Settings.kb_settings, "RRF_K", 60))

    # 1) 向量召回（多取一些用于融合）
    vec_hits = vectorstore.similarity_search_with_score(query, k=recall_k)
    # doc_id -> Document 映射（用 id(doc) 不可靠，用对象身份键）
    id2doc: Dict[int, Document] = {}
    vec_ranking: List[int] = []
    for d, s in vec_hits:
        key = id(d)
        if key not in id2doc:
            id2doc[key] = d
            vec_ranking.append(key)

    # 2) BM25 召回
    all_docs = list(vectorstore.docstore._dict.values())
    bm25 = get_bm25_retriever(kb_key, all_docs, top_k=bm25_k)
    bm25_ranking: List[int] = []
    for d in bm25.get_relevant_documents(query):
        key = id(d)
        if key not in id2doc:
            id2doc[key] = d
        if key not in bm25_ranking:
            bm25_ranking.append(key)

    # 3) RRF 融合（用对象身份做 doc_id）
    fused = rrf_fuse([vec_ranking, bm25_ranking], k=rrf_k)

    if method == "hybrid_rrf":
        result = [(id2doc[k], s) for k, s in fused.items()]
        return result[:top_k]

    if method == "hybrid_rerank":
        cand_k = int(getattr(Settings.kb_settings, "RERANK_CANDIDATE_K", 6))
        cand_ids = [k for k, _ in list(fused.items())[:cand_k]]
        cand_docs = [id2doc[k] for k in cand_ids]
        # rerank 用字符串 doc_id 缓存（page_content hash），跨进程不共享但进程内有效
        str_ids = [f"{k}:{hash(d.page_content)}" for k, d in zip(cand_ids, cand_docs)]
        reranked = llm_rerank(query, cand_docs, str_ids, embed_model, top_n=top_k)
        return reranked

    raise ValueError(f"unknown SEARCH_METHOD: {method}")
