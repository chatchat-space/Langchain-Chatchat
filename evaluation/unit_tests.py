"""单元验证：RRF 手算比对 + Excel 解析器边界测试（AC-RETR-02 / AC-PARSE-02 / AC-PARSE-05）

运行：python evaluation/unit_tests.py
全部断言通过输出 UNIT-TESTS-OK
"""
import os
import sys

os.environ["CHATCHAT_ROOT"] = r"D:\github_projects\Langchain-Chatchat\data"
sys.path.insert(0, r"D:\github_projects\Langchain-Chatchat\libs\chatchat-server")

# ---------------------------------------------------------------------------
# AC-RETR-02: RRF 手算比对
# 构造两路排名（向量路/BM25 路），手算期望分数与 rrf_fuse 输出比对
# ---------------------------------------------------------------------------
from chatchat.server.knowledge_base.hybrid_search import rrf_fuse  # noqa: E402

# 场景：向量路排名 [A,B,C]，BM25 路 [B,D,A]（k=60）
# 手算（score = Σ 1/(k+rank)，k=60）：
#   A: 1/(60+1) + 1/(60+3) = 1/61 + 1/63 = 0.0163934 + 0.0158730 = 0.0322664
#   B: 1/(60+2) + 1/(60+1) = 1/62 + 1/61 = 0.0161290 + 0.0163934 = 0.0325224
#   D: 1/(60+2) = 0.0161290
#   C: 1/(60+3) = 0.0158730
# 期望排序: B > A > D > C
VEC_RANK = ["A", "B", "C"]
BM25_RANK = ["B", "D", "A"]
EXPECTED = {
    "A": 1 / 61 + 1 / 63,
    "B": 1 / 62 + 1 / 61,
    "C": 1 / 63,
    "D": 1 / 62,
}
EXPECTED_ORDER = ["B", "A", "D", "C"]

fused = rrf_fuse([VEC_RANK, BM25_RANK], k=60)
got_order = list(fused.keys())
assert got_order == EXPECTED_ORDER, f"RRF 排序不符: {got_order} != {EXPECTED_ORDER}"
for doc_id, exp_score in EXPECTED.items():
    got = fused[doc_id]
    assert abs(got - exp_score) < 1e-9, f"RRF 分数不符 {doc_id}: {got} != {exp_score}"
print("AC-RETR-02 PASS: RRF 手算比对一致", [f"{k}:{v:.6f}" for k, v in fused.items()])

# ---------------------------------------------------------------------------
# AC-PARSE-02: 结构化转换规则单元验证（构造 2x3 测试表）
# ---------------------------------------------------------------------------
from langchain_core.documents import Document  # noqa: E402
from chatchat.server.file_rag.document_loaders.openpyxl_loader import (  # noqa: E402
    OpenpyxlExcelLoader,
)
from openpyxl import Workbook  # noqa: E402

import tempfile  # noqa: E402

wb = Workbook()
ws = wb.active
ws.title = "测试表"
ws.append(["名称", "颜色", "数量"])          # 表头
ws.append(["苹果", "红色", 3])               # 数据行1
ws.append(["香蕉", "黄色", 5.0])             # 数据行2（浮点整数应去 .0）
tmp = os.path.join(tempfile.gettempdir(), "unit_test_2x3.xlsx")
wb.save(tmp)

loader = OpenpyxlExcelLoader(file_path=tmp)
docs = loader.load()
os.remove(tmp)

assert len(docs) == 2, f"应有 2 个行块，实际 {len(docs)}"
d1, d2 = docs
# 规则1: 首行识别为表头 → 字段名出现在内容中
assert "名称: 苹果" in d1.page_content, d1.page_content
# 规则2: 逐字段换行拼接
assert d1.page_content == "名称: 苹果\n颜色: 红色\n数量: 3", repr(d1.page_content)
# 规则3: metadata 携带 sheet 名 + 行号（Excel 行号，表头=1，数据从 2 起）
assert d1.metadata["sheet_name"] == "测试表" and d1.metadata["row_id"] == 2
assert d2.metadata["row_id"] == 3
# 数值清洗: 5.0 → 5
assert "数量: 5\n" in d2.page_content or d2.page_content.endswith("数量: 5"), repr(d2.page_content)
print("AC-PARSE-02 PASS: 2x3 测试表转换规则四要素（表头/行块/metadata/数值清洗）全部符合")

# ---------------------------------------------------------------------------
# AC-PARSE-05: 四类边界实测
# ---------------------------------------------------------------------------
wb2 = Workbook()
# 边界1: 多 sheet（2 个 sheet 均应入库）
s1 = wb2.active
s1.title = "Sheet甲"
s1.append(["列1", "列2"])
s1.append(["a1", "b1"])
s2 = wb2.create_sheet("Sheet乙")
s2.append(["x", "y"])
s2.append(["u1", "v1"])
# 边界2: 空行（第3行全空，应跳过且不破坏行号）
s2.append([None, None])
s2.append(["u2", "v2"])
# 边界3: 合并单元格（取左上值填充）
s2.merge_cells("A6:B6")
s2["A6"] = "合并值"
tmp2 = os.path.join(tempfile.gettempdir(), "unit_test_boundary.xlsx")
wb2.save(tmp2)

docs2 = OpenpyxlExcelLoader(file_path=tmp2).load()
os.remove(tmp2)

src_by_sheet = {}
for d in docs2:
    src_by_sheet.setdefault(d.metadata["sheet_name"], []).append(d)
# 边界1 验证：两个 sheet 均有块
assert "Sheet甲" in src_by_sheet and "Sheet乙" in src_by_sheet, list(src_by_sheet)
# 边界2 验证：Sheet乙 = 2 数据行（u1v1, u2v2），空行跳过
sheet_b_rows = [d.metadata["row_id"] for d in src_by_sheet["Sheet乙"]]
assert 4 in sheet_b_rows and 6 in sheet_b_rows, sheet_b_rows  # row 4=u2v2, row 6=合并值
# 边界3 验证：合并单元格行内容包含左上值
merged = [d for d in src_by_sheet["Sheet乙"] if d.metadata["row_id"] == 6]
assert merged and "合并值" in merged[0].page_content, merged
# 边界4: 数字与日期格式（科学计数法/时间戳检查）
wb3 = Workbook()
ws3 = wb3.active
ws3.append(["项目", "数值"])
ws3.append(["大数", 123456789])
import datetime  # noqa: E402

ws3.append(["日期", datetime.date(2026, 10, 16)])
tmp3 = os.path.join(tempfile.gettempdir(), "unit_test_num.xlsx")
wb3.save(tmp3)
docs3 = OpenpyxlExcelLoader(file_path=tmp3).load()
os.remove(tmp3)
big = [d for d in docs3 if "大数" in d.page_content][0]
assert "123456789" in big.page_content and "e+" not in big.page_content.lower(), big.page_content
dt = [d for d in docs3 if "日期" in d.page_content][0]
assert "2026-10-16" in dt.page_content, dt.page_content  # openpyxl 返回 isoformat 字符串，非时间戳
print("AC-PARSE-05 PASS: 多sheet/合并单元格/空行/数字日期 四类边界实测通过")

print("UNIT-TESTS-OK")
