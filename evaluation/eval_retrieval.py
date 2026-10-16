"""20 条测试问答对 + 三种检索方法对比实验（改动2）。

评测指标：
- Hit@1 / Hit@3：top1 / top3 是否命中期望文档（按期望关键词判定）
- MRR：Mean Reciprocal Rank，每题命中排名倒数（1/rank）的平均值；未命中计 0
- 平均耗时

测试集：evaluation/testset.json（AC-EVAL-01，每条含 id/question/expected_doc/keywords）
离线运行：直接加载磁盘 FAISS 索引，不依赖 API 服务。
"""
import json
import os
import re
import sys
import time

os.environ["CHATCHAT_ROOT"] = r"D:\github_projects\Langchain-Chatchat\data"
sys.path.insert(0, r"D:\github_projects\Langchain-Chatchat\libs\chatchat-server")

from langchain.vectorstores.faiss import FAISS

from chatchat.server.knowledge_base.hybrid_search import hybrid_search
from chatchat.server.utils import get_Embeddings

# ---------------- 测试集：从 testset.json 加载（AC-EVAL-01） ----------------
_TESTSET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testset.json")
with open(_TESTSET_PATH, encoding="utf-8") as _f:
    _TESTSET = json.load(_f)["testset"]
# (问题, 期望命中文档的关键词列表) —— 关键词在期望文档中出现、在其他文档中少出现
TEST_PAIRS = [(t["question"], t["keywords"]) for t in _TESTSET]


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def hit(page_content: str, keywords: list) -> bool:
    """命中判定：任一关键词原文出现，或全部关键词去空格后出现。"""
    nc = normalize(page_content)
    for kw in keywords:
        if kw in page_content or normalize(kw) in nc:
            return True
    return False


def main():
    vs_path = r"D:\github_projects\Langchain-Chatchat\data\data\knowledge_base\samples\vector_store\bge-m3"
    vs = FAISS.load_local(
        vs_path, get_Embeddings("bge-m3"), normalize_L2=True,
        allow_dangerous_deserialization=True,
    )
    kb_key = ("samples", "bge-m3")

    methods = ["vector", "hybrid_rrf", "hybrid_rerank"]
    results = {m: {"hit1": 0, "hit3": 0, "mrr": 0.0, "times": []} for m in methods}

    detail_rows = []
    for query, keywords in TEST_PAIRS:
        row = {"query": query}
        for method in methods:
            t0 = time.time()
            docs = hybrid_search(vs, query, 3, 2.0, kb_key, "bge-m3", method=method)
            dt = time.time() - t0
            results[method]["times"].append(dt)

            rank = None
            for i, (d, _s) in enumerate(docs, start=1):
                if hit(d.page_content, keywords):
                    rank = i
                    break
            row[method] = rank
            if rank == 1:
                results[method]["hit1"] += 1
            if rank is not None and rank <= 3:
                results[method]["hit3"] += 1
            if rank is not None:
                results[method]["mrr"] += 1.0 / rank
        detail_rows.append(row)
        print(f"done: {query[:24]}... vector={row['vector']} rrf={row['hybrid_rrf']} rerank={row['hybrid_rerank']}", flush=True)

    n = len(TEST_PAIRS)
    summary = {}
    for method in methods:
        r = results[method]
        avg_t = sum(r["times"]) / len(r["times"])
        summary[method] = {
            "Hit@1": f"{r['hit1']}/{n} ({r['hit1']/n*100:.0f}%)",
            "Hit@3": f"{r['hit3']}/{n} ({r['hit3']/n*100:.0f}%)",
            "MRR": f"{r['mrr']/n:.3f}",
            "平均耗时(s)": f"{avg_t:.2f}",
        }

    out = {"summary": summary, "detail": detail_rows}
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retrieval_eval_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nSUMMARY:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nsaved -> {out_path}")
    print("EVAL-DONE")


if __name__ == "__main__":
    main()
