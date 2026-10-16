"""20 条测试问答对 + 三种检索方法对比实验（改动2）。

评测指标：
- Hit@1 / Hit@3：top1 / top3 是否命中期望文档（按期望关键词判定）
- MRR：倒数排名
- 平均耗时

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

# ---------------- 20 条测试问答对 ----------------
# (问题, 期望命中文档的关键词列表) —— 关键词在期望文档中出现、在其他文档中少出现
TEST_PAIRS = [
    ("萌新求教大佬怎么改成AMD显卡或者CPU？", ["把.cuda()去掉就行", "AMD显卡"]),
    ("训练框架都有哪些？", ["deepspeed", "megatron-lm"]),
    ("推理框架有哪些选择？", ["vllm", "text-generation-inference"]),
    ("PagedAttention 是做什么的？解决了什么问题？", ["PagedAttention", "KV cache"]),
    ("RLHF 训练包括哪几个步骤？", ["SFT", "RM", "PPO"]),
    ("RRHF 方法的特点是什么？", ["RRHF", "排名损失"]),
    ("LIMA 是哪类方法？", ["LIMA", "SFT-only"]),
    ("分布式训练中的 FSDP 算法是怎么来的？", ["FSDP", "ZeroRedundancyOptimizer"]),
    ("DDP 是怎么同步梯度的？", ["DistributedDataParallel", "AllReduce"]),
    ("ZeRO 的三个阶段分别切分什么？", ["ZeRO1", "optimizer state"]),
    ("Tokenizer 的 subword 级别方法有哪些？", ["BPE", "WordPiece"]),
    ("位置编码有哪些技术？", ["ROPE", "AliBi"]),
    ("稀疏注意力相关技术有哪些？", ["稀疏注意力", "flash-attention"]),
    ("向量数据库的选型标准是什么？", ["选型标准", "开源vs.闭源"]),
    ("langchain-ChatGLM 的 issue 里，纯 CPU 环境运行报什么错？", ["nvcuda.dll", "纯CPU"]),
    ("issue 里有人反馈知识库提取的文字乱码，问题是什么？", ["乱码", "prompt"]),
    ("压缩框架有哪些？", ["bitsandbytes", "auto-gptq"]),
    ("python API 工具有哪些？", ["FastAPI", "flask"]),
    ("RLAIF 的核心思想是什么？", ["AI 模型监督其他 AI 模型", "自我批评"]),
    ("向量数据库 chroma 属于哪种托管方式？", ["embeded+cloud-native", "chroma"]),
]


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
    out_path = r"D:\github_projects\retrieval_eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nSUMMARY:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nsaved -> {out_path}")
    print("EVAL-DONE")


if __name__ == "__main__":
    main()
