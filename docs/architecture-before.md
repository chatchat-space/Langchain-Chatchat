# 检索链路架构（改动前 baseline）

> 记录于 2026-10-16，对应上游 commit `49165d6`（fork 基线）。本文件描述**改动前**的完整检索链路，供与 architecture-after.md 对比。

## 一、检索链路（WebUI 发问 → 返回排序结果）

```
WebUI (Streamlit, :8501)
  │  POST /chat/kb_chat
  ▼
api_server 路由层
  libs/chatchat-server/chatchat/server/chat/kb_chat.py :: kb_chat()          [入口路由]
  │  mode=local_kb 时: run_in_threadpool(search_docs, ...)
  ▼
knowledge_base 模块
  libs/chatchat-server/chatchat/server/knowledge_base/kb_doc_api.py :: search_docs()   [API 封装]
  │  调 KBServiceFactory.get_service_by_name(kb_name)
  ▼
  libs/chatchat-server/chatchat/server/knowledge_base/kb_service/base.py :: KBService.search_docs()  [抽象入口]
  │
  ▼
  libs/chatchat-server/chatchat/server/knowledge_base/kb_service/faiss_kb_service.py :: FaissKBService.do_search()  [实际执行]
  │  get_Retriever("ensemble").from_vectorstore(vs, ...)
  ▼
Retriever 层（改动前为 EnsembleRetriever）
  libs/chatchat-server/chatchat/server/file_rag/utils.py :: get_Retriever()        [Retriever 工厂]
  libs/chatchat-server/chatchat/server/file_rag/retrievers/ensemble.py
    :: EnsembleRetrieverService.from_vectorstore()  [构建 BM25Retriever + FAISS retriever，权重 0.5/0.5]
  │
  ▼
向量库 FAISS
  kb_faiss_pool (kb_cache/faiss_cache.py :: KBFaissPool.load_vector_store())
  │  磁盘: data/data/knowledge_base/<kb>/vector_store/<embed_model>/index.faiss
  ▼
返回排序结果（Document 列表）→ format_reference() → LLM 生成回答
```

## 二、模型接入（与验收基线的环境差异说明）

| 项 | 验收标准预设 | 实际部署 | 差异原因 |
|---|---|---|---|
| LLM | DeepSeek API | **本地 Ollama qwen2.5:7b** | 本机无独立 GPU，但 Ollama CPU 推理 7B 可用（27.8GB 内存），且无需 API Key/费用，链路验证等价 |
| Embedding | SiliconFlow bge-m3 / 本地 bge-small-zh | **本地 Ollama bge-m3** | 与预设同模型（bge-m3），本地运行满足"无预算则本地"的备选路径 |
| Rerank | SiliconFlow bge-reranker-v2-m3 | **本地 bge-m3 embedding 余弦相似度** | 无 SiliconFlow Key；Ollama 不提供专用 rerank 端点，用同模型 embedding 近似（已实现降级路径，见 after 文档） |

**端点实测修正**（0.3.1.3 实际路径，与验收文档假设的 `/api/v1/...` 不同）：
- `GET  /knowledge_base/list_knowledge_bases`
- `POST /knowledge_base/upload_docs`
- `POST /knowledge_base/search_docs`
- `POST /knowledge_base/create_knowledge_base`
- `POST /chat/kb_chat`

## 三、改动前的已知问题（改动动机）

1. `do_search` 每次查询都从 docstore 全量重建 BM25 索引（EnsembleRetrieverService.from_vectorstore 每次调用都 `BM25Retriever.from_documents`）
2. `UnstructuredExcelLoader` 在 Windows 下 libmagic DLL 冲突 → 子进程段错误 → `kb -r` 无限等待
3. xlsx 整表拼一个字符串，无行级检索粒度
4. 纯向量检索对"术语原词"类问题（语义改写后）会 miss（见 eval-results 实测）
