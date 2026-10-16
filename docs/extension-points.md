# 扩展点定位（AC-ENV-05）

> 定位于 2026-10-16，对应上游 commit `49165d6`。本文件记录三个二次开发锚点的**具体文件路径、函数名与 grep 证据**，是后续所有改动的挂载位置。

## 1. 文件解析器注册点

上传的文件按扩展名分发到解析逻辑的位置。

**文件**：`libs/chatchat-server/chatchat/server/knowledge_base/utils.py`
**结构**：`LOADER_DICT`（扩展名 → Loader 类名映射，L99 起）→ `get_LoaderClass(file_extension)`（L169）→ `get_loader(loader_name, file_path, loader_kwargs)`（L177）

```
$ grep -n "OpenpyxlExcelLoader\|xlsx\|XLSX" libs/chatchat-server/chatchat/server/knowledge_base/utils.py | head -8
126:    "OpenpyxlExcelLoader": [".xlsx", ".xls", ".xlsd"],
181:            "OpenpyxlExcelLoader",
```

**改动方式（AC-PARSE-01）**：
- `LOADER_DICT` 中 `"UnstructuredExcelLoader": [".xlsx", ...]` 改为 `"OpenpyxlExcelLoader": [...]`（净改 1 行）
- `get_loader` 的本地 loader import 白名单追加 `"OpenpyxlExcelLoader"`（+1 行）
- 新增解析器本体：`libs/chatchat-server/chatchat/server/file_rag/document_loaders/openpyxl_loader.py`（108 行独立模块）
- 其余文件类型解析路径零改动（`git diff --stat` 验证：仅 3 文件 +111/-1）

## 2. 文本分块器（text_splitter）

**文件**：`libs/chatchat-server/chatchat/server/knowledge_base/utils.py`
**函数**：`make_text_splitter(splitter_name, chunk_size, chunk_overlap)`（L222 起）
**选择逻辑**：`Settings.kb_settings.text_splitter_dict[splitter_name]` 配置驱动（kb_settings.yaml），按 `source`（tiktoken/huggingface）与 chunk_size/overlap 构造对应 splitter。

```
$ grep -n "TEXT_SPLITTER_NAME\|text_splitter_dict\|make_text_splitter" libs/chatchat-server/chatchat/server/knowledge_base/utils.py | head -8
222:def make_text_splitter(splitter_name, chunk_size, chunk_overlap):
231:            headers_to_split_on = Settings.kb_settings.text_splitter_dict[splitter_name][
248:                Settings.kb_settings.text_splitter_dict[splitter_name]["source"] == "tiktoken"
261:                encoding_name= Settings.kb_settings.text_splitter_dict[splitter_name][
268:                Settings.kb_settings.text_splittr_dict[splitter_name]["source"] == "huggingface"
```

**Excel 行块的分块策略**：行级 Document 天然短小（单行字段拼接），走默认 `FAISS` 分块器无再切分压力；长文本 sheet（售后条款 436 字）按 chunk_size 自然分块，均已实测入库（见 acceptance-log.md AC-PARSE-03）。

## 3. search_docs 实现入口（向量检索真正执行的函数）

**链路**：
`libs/chatchat-server/chatchat/server/knowledge_base/kb_service/base.py :: search_docs()`（L201，模式分发）
→ `faiss_kb_service.py :: do_search()`（L66，FAISS 相似度检索本体）
→ `base.py :: do_search()`（L315，抽象基类定义）

```
$ grep -n "def do_search\|def search_docs" libs/chatchat-server/chatchat/server/knowledge_base/kb_service/faiss_kb_service.py libs/chatchat-server/chatchat/server/knowledge_base/kb_service/base.py
libs/chatchat-server/chatchat/server/knowledge_base/kb_service/faiss_kb_service.py:66:    def do_search(
libs/chatchat-server/chatchat/server/knowledge_base/kb_service/base.py:201:    def search_docs(
libs/chatchat-server/chatchat-server/chatchat/server/knowledge-.../base.py:315:    def do_search(
```

**改动方式（AC-RETR-04 模式开关）**：`search_docs()` 新增 `retrieval_method` 参数读取 `Settings.kb_settings.SERACH_METHOD`（vector / hybrid_rrf / hybrid_rerank），非 vector 模式走新增模块 `hybrid_search.py`（与原 `do_search` 并存，原路径保持原样可运行——全局约束 1「基线可回退」）。
