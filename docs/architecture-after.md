# 检索链路架构（改动后）— 含 Mermaid 对比图

> 对应 feature 分支 `feature/excel-loader-and-hybrid-search`。改动前链路见 architecture-before.md。

## 一、改动后完整链路（Mermaid）

```mermaid
flowchart TD
    U[WebUI :8501 / API 调用方] -->|POST /chat/kb_chat 或 /knowledge_base/search_docs| A[api_server 路由<br/>kb_chat.py :: kb_chat]
    A --> B[kb_doc_api.py :: search_docs]
    B --> C[KBService.search_docs<br/>base.py 元组兼容层]
    C --> D["FaissKBService.do_search<br/>faiss_kb_service.py"]

    D -->|SEARCH_METHOD 路由| E{hybrid_search.py<br/>:: hybrid_search}

    E -->|vector| F1[FAISS 向量检索<br/>similarity_search_with_score]
    E -->|ensemble| F0[原 EnsembleRetriever<br/>保留兼容]
    E -->|hybrid_rrf / hybrid_rerank| F1
    E -->|hybrid_rrf / hybrid_rerank| F2["BM25 通道<br/>rank_bm25 + jieba.lcut_for_search<br/>索引按 KB 缓存"]

    F1 --> G["RRF Fusion<br/>score(d)=Σ 1/(k+rank)<br/>k=60"]
    F2 --> G

    G -->|hybrid_rrf| H1[返回 top_k]
    G -->|hybrid_rerank| I["Reranker<br/>bge-m3 query-doc 余弦<br/>LRU 缓存 2048"]
    I --> H1

    subgraph 入库链路（改动点一）
        J[上传 .xlsx] --> K["XlsxParser<br/>OpenpyxlExcelLoader<br/>表头识别+行转文档块"]
        K --> L[ChineseRecursiveTextSplitter]
        L --> M[FAISS 入库<br/>行级 chunk + metadata.row_id]
    end

    H1 --> N[format_reference → LLM 生成回答]
```

**4 个新增节点**（验收要求）：
1. `XlsxParser` = `chatchat/server/file_rag/document_loaders/openpyxl_loader.py` :: `OpenpyxlExcelLoader`
2. `BM25 Index` = `chatchat/server/knowledge_base/hybrid_search.py` :: `get_bm25_retriever()`（jieba 分词 + 按库缓存）
3. `RRF Fusion` = `hybrid_search.py` :: `rrf_fuse()`
4. `Reranker` = `hybrid_search.py` :: `llm_rerank()`（含降级路径：embedding 调用异常时返回 RRF 融合结果并日志标注）

## 二、模式开关与回归保障

`data/kb_settings.yaml` 的 `SEARCH_METHOD`（热加载）：

| 模式 | 行为 | 与改动前关系 |
|---|---|---|
| `vector` | 纯 FAISS | 原版行为还原 |
| `ensemble` | 原 EnsembleRetriever | **完全保留原代码路径**（基线可回退红线） |
| `hybrid_rrf` | 向量+BM25 → RRF | 新增 |
| `hybrid_rerank` | RRF + bge-m3 重排 | 新增（默认） |

原检索函数 `get_Retriever("ensemble")` 及 `EnsembleRetrieverService` **零改动**，新增逻辑全部在独立文件 `hybrid_search.py`，`do_search` 仅做分发调用——满足"新增模块 + 模式开关"红线。

## 三、Rerank 降级路径（AC-RETR-03 说明）

原验收标准要求接 SiliconFlow rerank API + 失败降级。实际部署无 SiliconFlow Key（见 architecture-before 模型差异表），rerank 用本地 bge-m3 embedding 余弦实现：
- **降级语义保留**：`llm_rerank()` 内 embedding 调用若抛异常，由调用方 `hybrid_search()` 捕获后回退返回 `hybrid_rrf` 融合结果（代码中 try 包裹 + 日志 `rerank=degraded`）
- 如后续申请到 SiliconFlow Key，仅需在 `llm_rerank()` 内替换为 API 调用，接口不变
