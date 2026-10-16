# 面试九问：两个功能 + 一组评测（AC-INT-01）

> 项目：Langchain-Chatchat 二次开发（fork: sheep719/Langchain-Chatchat，分支 feature/excel-loader-and-hybrid-search）
> 评测数字唯一来源：`docs/eval-results.md`（源自 `evaluation/retrieval_eval_results.json`）

## 功能一：Excel 结构化入库解析器

### Q1 为什么这么做？（设计动机）

上游对 .xlsx 走 UnstructuredExcelLoader，整表当一坨文本切分，检索命中后拿不到结构化字段——问"某产品价格"返回的是截断的表格碎片。我们把解析改为**表头识别 + 行转文档块**：每行变成一个独立 Document，内容按 `字段名: 值` 逐行拼接，metadata 携带 sheet 名 + 行号。这样每个产品行都是可独立命中的检索单元，且命中后能定位回原表（sheet + 行号）。

### Q2 遇到什么坑？

三个：① Unstructured 在 Windows 上对中文 xlsx 的解码不稳，出现字段串列；② 行内数字格式被 openpyxl 读成科学计数法（大价格数字）；③ 上游 LOADER_DICT 的注册方式是「类名 → 扩展名数组」，替换成自定义 Loader 时必须同步改 `get_loader` 里的 import 白名单，否则走 langchain_community 的同名类去（不存在）。

### Q3 怎么解决？

① 直接换 openpyxl 手写解析（108 行独立模块 `openpyxl_loader.py`），不依赖 Unstructured；② 数值单元格显式转 int/str，日期走 isoformat，实测四类边界（多 sheet/合并单元格/空行/数字日期）全过；③ 注册改动最小化：LOADER_DICT 键替换 + import 白名单 +1 行，git diff 对上游基线仅 3 文件 +111/-1，其他文件类型解析路径零改动。

## 功能二：混合检索 + RRF 融合 + Rerank

### Q4 为什么 BM25 必须配 jieba？

BM25 的打分单位是 token。不做分词的中文整句会被当成一个 token，query 和文档没有可对齐的词项，IDF/TF 全部失效——中文 BM25 不分词等于没做。用 jieba 切词后，query「RLHF 训练步骤」→ ['RLHF', '训练', '步骤']，才能与文档 token 对齐计算。日志里可见分词样例（`[hybrid] jieba分词=[...]`）。

### Q5 RRF 相比分数加权融合的优势？

RRF 公式 `score(d) = Σ 1/(k + rank_i(d))`（k=60），只用**排名**不用原始分数。好处：① 向量是余弦相似度、BM25 是 TF-IDF 族分数，两者分布和量纲完全不同，加权融合必须先归一化，归一化方法本身引入调参负担；② RRF 对分数分布不敏感、免归一化，对异常分数（某一路整体偏高）鲁棒；③ 工业界标准做法（ElasticSearch 等都用），面试好讲。我们用手工构造的两路各 3 文档排名做了手算比对，期望分数与函数输出完全一致（`evaluation/unit_tests.py`，AC-RETR-02）。

### Q6 为什么 embedding 建库后不能换？

向量检索的物理基础是**同空间近邻**：query 和 doc 向量必须由同一模型映射到同一向量空间才可比。换 embedding 模型 = 换空间，新 query 向量与旧库内 doc 向量毫无对齐关系，相似度全乱——等价于全库向量作废，必须删库重建。所以本项目 bge-m3 一旦建库就锁定（这也是验收红线之一）。

### Q7 rerank 降级策略的设计动机？

rerank 属于增益层而非必需层：融合结果（RRF top-K）本身已可用，rerank 失败不应让整条查询挂掉。设计为 try/except 包住 rerank 调用，任何异常（超时/网络/key 无效）→ 记 `rerank=degraded` 日志 + 返回 RRF 融合结果。可用性优先于最优排序，这是线上服务的基本素养。双路径已实测：注入 ConnectionError 后日志出现 `rerank=degraded` 且返回 3 条非空结果（`evaluation/test_degradation.py`）。

## 评测

### Q8 评测方法怎么设计的？

20 条改写问题（不照抄文档原句，否则 BM25 白给），覆盖 5 份入库文档，难度三分：关键词可命中 / 需语义理解 / 刁钻题。同一库、同一测试集、同一 top_k，离线直读 FAISS 索引跑 vector / hybrid_rrf / hybrid_rerank 三轮，指标 Hit@1/Hit@3/MRR（MRR = 命中排名倒数的平均，未命中计 0）。脚本重跑数字完全一致（确定性检索无随机性），简历数字全部可溯源到 `eval-results.md`。

### Q9 数字说明了什么？（诚实结论）

三模式 20 题：Hit@3 vector 90% → hybrid_rrf 100% → hybrid_rerank 95%；MRR 0.842 → 0.892 → 0.858。**HYBRID(RRF) 是最大赢家**：BM25 把 vector 未进 top3 的 2 题（关键词题：专有名词 "XJ"-类 token 与 issue 原文）救回。hybrid_rerank 比 hybrid_rrf 低 5%：本地 LLM 打分重排（qwen2.5:7b 余弦代理）对短 query 的语义判断不如 RRF 排名稳，属已知局限——生产环境接真 rerank API（bge-reranker-v2-m3）预期会反超，这步留作下一步。**不挑数字、不编造**，表格是唯一事实源。
