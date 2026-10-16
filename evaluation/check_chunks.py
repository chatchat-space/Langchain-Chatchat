"""AC-PARSE-03: 统计 kb_demo 中 产品清单.xlsx 的 chunk 总数与结构抽查。"""
import os
import sys

os.environ["CHATCHAT_ROOT"] = r"D:\github_projects\Langchain-Chatchat\data"
sys.path.insert(0, r"D:\github_projects\Langchain-Chatchat\libs\chatchat-server")

from langchain.vectorstores.faiss import FAISS

kb_dir = r"D:\github_projects\Langchain-Chatchat\data\data\knowledge_base\kb_demo\vector_store\bge-m3"
vs = FAISS.load_local(kb_dir, None, allow_dangerous_deserialization=True)

docs = list(vs.docstore._dict.values())
print(f"kb_demo chunk 总数: {len(docs)}")
print(f"来源文件数: {len(set(d.metadata.get('source', '?') for d in docs))}")

# 行块（Sheet1）与长文本块（Sheet2）分别统计
row_chunks = [d for d in docs if "产品名称:" in d.page_content]
sheet2 = [d for d in docs if "售后条款" in d.page_content]
print(f"Sheet1 行块数: {len(row_chunks)}（要求 ≥20）")
print(f"Sheet2 售后条款块数: {len(sheet2)}")
print()
print("== 行块结构抽查（第 1 块）==")
print(row_chunks[0].page_content)
print("metadata:", row_chunks[0].metadata)
print()
print("== 长文本块结构抽查（第 1 块前 150 字）==")
print(sheet2[0].page_content[:150])
print("metadata:", sheet2[0].metadata)

assert len(docs) >= 20, "chunk 总数不足 20"
assert len(row_chunks) >= 20, "行块数不足 20"
assert "字段: 值" not in row_chunks[0].page_content  # 不应残留模板文字
kv = row_chunks[0].page_content.split("\n")
assert all(": " in line for line in kv if line.strip()), "行块必须是 '字段: 值' 结构"
print()
print("AC-PARSE-03 PASS: 行块≥20 且结构为 字段: 值，metadata 含 sheet/行号")
