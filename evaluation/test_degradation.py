"""AC-RETR-03 降级路径实测：rerank 失败时必须返回 RRF 融合结果并记 rerank=degraded 日志。

运行：python evaluation/test_degradation.py
"""
import os
import sys

os.environ["CHATCHAT_ROOT"] = r"D:\github_projects\Langchain-Chatchat\data"
sys.path.insert(0, r"D:\github_projects\Langchain-Chatchat\libs\chatchat-server")

from langchain.vectorstores.faiss import FAISS

import chatchat.server.knowledge_base.hybrid_search as hs
from chatchat.server.utils import get_Embeddings

# 捕获日志输出（loguru）
records = []


def _sink(message):
    records.append(str(message))


hs.logger.add(_sink, level="INFO")

kb_dir = r"D:\github_projects\Langchain-Chatchat\data\data\knowledge_base\samples\vector_store\bge-m3"
emb = get_Embeddings("bge-m3")
vs = FAISS.load_local(kb_dir, emb, allow_dangerous_deserialization=True)

# 正常路径：hybrid_rerank 可用
ok = hs.hybrid_search(
    vectorstore=vs, query="RLHF 训练步骤", top_k=3, score_threshold=0.0,
    kb_key=("samples", "bge-m3"), embed_model="bge-m3", method="hybrid_rerank",
)
print(f"正常路径: 返回 {len(ok)} 条, 有分数={all(isinstance(s, float) for _, s in ok)}")

# 降级路径：注入故障，让 rerank 抛异常
def _broken_rerank(*args, **kwargs):
    raise ConnectionError("模拟 rerank API 不可达 (注入故障)")

records.clear()
hs.llm_rerank = _broken_rerank
degraded = hs.hybrid_search(
    vectorstore=vs, query="RLHF 训练步骤", top_k=3, score_threshold=0.0,
    kb_key=("samples", "bge-m3"), embed_model="bge-m3", method="hybrid_rerank",
)
deg_logs = [m for m in records if "degraded" in m]
print(f"降级路径: 返回 {len(degraded)} 条（非空即回退成功）")
print(f"降级日志: {deg_logs[0] if deg_logs else '未捕获！'}")

assert len(ok) == 3, "正常路径应返回 3 条"
assert len(degraded) == 3, "降级路径应回退返回 3 条"
assert deg_logs and "rerank=degraded" in deg_logs[0], "必须记录 rerank=degraded 日志"
print("AC-RETR-03 PASS: 正常 + 降级双路径实测通过")
