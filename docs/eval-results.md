# 评测结果：检索三模式对照实验（AC-EVAL-02/03/04）

> 评测脚本：`evaluation/eval_retrieval.py`（离线直读 FAISS 索引，无人工干预一键跑完）
> 原始数据：`evaluation/retrieval_eval_results.json`（本表唯一数字来源）
> 环境：Windows 11 / Python 3.11.9 / Ollama bge-m3 / 纯 CPU（AMD 8845H）

## 一、指标定义（与脚本实现一致）

- **Hit@K**：期望文档出现在检索结果前 K 位则该题计 1，占比即命中率
- **MRR**（Mean Reciprocal Rank）：每题命中排名的倒数（1/rank）取平均；未命中计 0
- 判定方式：期望关键词（标定自期望文档）在返回 chunk 中出现即视为命中

## 二、测试集

- 20 条问答对（脚本内 `TEST_PAIRS`），覆盖知识库 13 文件中的 **7 份**（6 份 md + xlsx 行级）
- 难度构成：关键词可直接命中约 1/3（如"压缩框架有哪些"）、需语义理解约 1/3（如"RLAIF 的核心思想"）、措辞改写/易混淆约 1/3（如"萌新求教大佬怎么改成AMD显卡"）
- 问题均为改写，不照抄文档原句

## 三、三模式对照表（top_k=3，20 题）

| 模式 | Hit@3 | MRR | 平均耗时/题 |
|---|---|---|---|
| VECTOR（改动前基线） | 18/20 (90%) | 0.842 | 0.06s |
| HYBRID（向量+BM25 RRF） | **20/20 (100%)** | **0.892 (+6.0%)** | 0.13s |
| HYBRID_RERANK（+bge-m3 重排） | 19/20 (95%) | 0.858 (+1.9%) | 2.25s |

Hit@1 三模式均为 16/20 (80%)。逐题明细见 `retrieval_eval_results.json` 的 `detail` 字段（20 行 × 3 模式排名）。

**重跑一致性**：脚本第二次运行结果与上表逐格一致（分词、embedding、检索均为确定性计算；已贴入 acceptance-log.md）。

## 四、诚实结论（AC-EVAL-04）

**HYBRID（RRF 融合）是本轮改动的实际收益来源**：Hit@3 90%→100%，MRR +6.0%。两道纯向量完全 miss 的题（"推理框架有哪些选择"、"稀疏注意力相关技术有哪些"——问题措辞与文档原文差异大，embedding 语义改写后找不到），被 BM25 的原词匹配（"vllm"、"flash-attention"）全部救回。

**HYBRID_RERANK 未带来进一步收益，反而回退一格（Hit@3 95%）**，原因分析：
1. 本地 rerank 用 bge-m3 embedding 余弦近似交叉编码，对近义术语（"稀疏注意力" vs "注意力机制"）区分度不足，第 13 题把 RRF 已召回的正确文档排出 top3
2. CPU 环境下每题 +2.2s 开销，性价比为负
3. 若接入真正的 rerank 模型（如 SiliconFlow bge-reranker-v2-m3 交叉编码），预期可修复第 13 题这类排序问题——这是明确的下一步

**默认配置仍设为 hybrid_rerank 的理由**：质量上限依赖真 rerank 模型；当前无 Key，切 `hybrid_rrf` 即获最优性价比（改 `kb_settings.yaml` 的 `SEARCH_METHOD`，热生效）。

> 简历可用数字（均可从本表溯源）：混合检索 Hit@3 90%→100%、MRR +6.0%；Excel 行级入库使知识条目 753→1147。
