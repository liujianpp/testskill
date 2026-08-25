#!/usr/bin/env python3
"""
export_excel.py
汇总所有批次的测试用例 JSON，导出为标准格式 Excel 文件。
"""

import argparse
import json
import glob
import os
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ── 颜色定义 ─────────────────────────────────────────────────
HEADER_FILL  = PatternFill("solid", fgColor="2E75B6") if HAS_OPENPYXL else None
FILL_MAP = {
    "正向": "FFFFFF",
    "负向": "FFF2CC",
    "边界": "DDEEFF",
    "安全": "FFE4CC",
} if HAS_OPENPYXL else {}

# ── 标准列顺序（与功能测试用例25列保持一致） ─────────────────
COLUMNS = [
    ("project",         "系统/项目",        12),
    ("module",          "模块",             15),
    ("feature",         "功能",             15),
    ("test_item",       "测试项",           25),
    ("title",           "用例标题",         30),
    ("preconditions",   "前置条件",         30),
    ("db_tables",       "涉及到数据库表",   20),
    ("test_data",       "测试数据",         35),
    ("steps",           "测试步骤",         55),
    ("expected_result", "预期结果",         55),
    ("validation_sql",  "验证SQL",          60),
    ("actual_result",   "实际结果",         20),
    ("is_passed",       "是否通过",         10),
    ("estimated_hours", "预计工时(h)",      12),
    ("execute_date",    "执行时间(年月日)", 15),
    ("test_progress",   "测试进度(%)",      12),
    ("case_type",       "用例类型",         10),
    ("priority",        "用例优先级",        8),
    ("is_regression",   "是否回归用例",     12),
    ("is_blocker",      "是否阻塞上线",     12),
    ("requirement_id",  "关联需求ID",       15),
    ("api_url",         "API URL",          25),
    ("bug_count",       "BUG数",             8),
    ("bug_unresolved",  "BUG未解决数",      10),
    ("case_version",    "用例版本",         10),
]

# 需要自动换行的列 key
WRAP_COLS = {"test_item", "steps", "test_data", "expected_result", "validation_sql", "preconditions", "db_tables"}


def load_all_batches(workspace: str) -> list[dict]:
    """加载 output/ 目录下所有 cases_batch_*.json 文件"""
    output_dir = Path(workspace) / "output"
    pattern = str(output_dir / "cases_batch_*.json")
    files = sorted(glob.glob(pattern))

    if not files:
        # 兼容：也搜索根目录
        pattern2 = str(Path(workspace) / "cases_batch_*.json")
        files = sorted(glob.glob(pattern2))

    all_cases = []
    for f in files:
        with open(f, encoding="utf-8") as fp:
            batch = json.load(fp)
            if isinstance(batch, list):
                all_cases.extend(batch)
            elif isinstance(batch, dict) and "cases" in batch:
                all_cases.extend(batch["cases"])
        print(f"   📂 加载 {f}: {len(batch) if isinstance(batch, list) else len(batch.get('cases', []))} 条用例")

    print(f"✅ 共加载 {len(all_cases)} 条测试用例")
    return all_cases


def auto_case_id(cases: list[dict]) -> list[dict]:
    """为没有 case_id 的用例自动编号"""
    seq = 1
    for c in cases:
        if not c.get("case_id"):
            c["case_id"] = f"TC-API-{seq:03d}"
        seq += 1
    return cases


def make_thin_border():
    side = Side(style="thin", color="CCCCCC")
    return Border(left=side, right=side, top=side, bottom=side)


def export_excel(cases: list[dict], output_path: str):
    if not HAS_OPENPYXL:
        raise RuntimeError("请安装 openpyxl: pip install openpyxl")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "API测试用例"

    thin_border = make_thin_border()

    # ── 写表头 ────────────────────────────────────────────────
    header_font = Font(name="微软雅黑", bold=True, color="FFFFFF", size=11)
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for col_idx, (key, name, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=name)
        cell.fill = HEADER_FILL
        cell.font = header_font
        cell.alignment = header_align
        cell.border = thin_border
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"  # 冻结首行

    # ── 写数据行 ────────────────────────────────────────────────
    data_font = Font(name="微软雅黑", size=10)
    center_align = Alignment(horizontal="center", vertical="top")
    left_align   = Alignment(horizontal="left", vertical="top", wrap_text=True)

    # 按 API 分组（用于合并用例编号列显示）
    current_api = None
    api_start_row = 2

    for row_idx, case in enumerate(cases, start=2):
        test_type = case.get("test_type", case.get("case_type", "正向"))
        fill_color = FILL_MAP.get(test_type, "FFFFFF")
        row_fill = PatternFill("solid", fgColor=fill_color)

        for col_idx, (key, name, width) in enumerate(COLUMNS, start=1):
            val = case.get(key, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=str(val) if val is not None else "")
            cell.fill = row_fill
            cell.font = data_font
            cell.border = thin_border

            if key in WRAP_COLS:
                cell.alignment = left_align
            elif key in ("case_type", "priority", "is_passed", "is_regression", "is_blocker", "bug_count", "bug_unresolved", "case_version", "estimated_hours", "test_progress"):
                cell.alignment = center_align
            else:
                cell.alignment = Alignment(horizontal="left", vertical="top")

        ws.row_dimensions[row_idx].height = 60

    # ── 添加筛选器 ────────────────────────────────────────────
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{len(cases) + 1}"

    # ── 统计 Sheet ────────────────────────────────────────────
    ws_stat = wb.create_sheet("覆盖率统计")
    _write_stats_sheet(ws_stat, cases, thin_border, data_font)

    wb.save(output_path)
    print(f"✅ Excel 已生成: {output_path}")


def _write_stats_sheet(ws, cases, border, font):
    """在统计 Sheet 中写覆盖率汇总"""
    from openpyxl.styles import PatternFill, Font, Alignment
    title_font = Font(name="微软雅黑", bold=True, size=12)
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 15

    ws.cell(1, 1, "覆盖率统计报告").font = title_font
    ws.cell(2, 1, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total = len(cases)
    type_counts = {}
    api_counts = {}
    priority_counts = {}
    for c in cases:
        ct = c.get("test_type", c.get("case_type", "未知"))
        type_counts[ct] = type_counts.get(ct, 0) + 1
        ap = c.get("api_url", c.get("api_path", "未知"))
        api_counts[ap] = api_counts.get(ap, 0) + 1
        pr = c.get("priority", "未知")
        priority_counts[pr] = priority_counts.get(pr, 0) + 1

    # 类型分布
    ws.cell(4, 1, "用例类型分布").font = Font(bold=True, name="微软雅黑")
    ws.cell(5, 1, "类型"); ws.cell(5, 2, "数量"); ws.cell(5, 3, "比例"); ws.cell(5, 4, "目标")
    row = 6
    targets = {"正向": "≥40%", "负向": "≥30%", "边界": "≥20%", "安全": "≥10%"}
    for ct, cnt in sorted(type_counts.items()):
        ws.cell(row, 1, ct)
        ws.cell(row, 2, cnt)
        ws.cell(row, 3, f"{cnt/total*100:.1f}%" if total else "0%")
        ws.cell(row, 4, targets.get(ct, "-"))
        row += 1
    ws.cell(row, 1, "合计"); ws.cell(row, 2, total)
    row += 2

    # API 分布
    ws.cell(row, 1, "接口用例分布").font = Font(bold=True, name="微软雅黑")
    row += 1
    ws.cell(row, 1, "接口路径"); ws.cell(row, 2, "用例数")
    row += 1
    for ap, cnt in sorted(api_counts.items(), key=lambda x: -x[1]):
        ws.cell(row, 1, ap); ws.cell(row, 2, cnt)
        row += 1
    row += 1

    # 优先级分布
    ws.cell(row, 1, "优先级分布").font = Font(bold=True, name="微软雅黑")
    row += 1
    ws.cell(row, 1, "优先级"); ws.cell(row, 2, "数量")
    row += 1
    for pr in ["P0", "P1", "P2", "P3"]:
        ws.cell(row, 1, pr); ws.cell(row, 2, priority_counts.get(pr, 0))
        row += 1


def main():
    parser = argparse.ArgumentParser(description="导出测试用例为标准 Excel")
    parser.add_argument("--workspace", required=True, help="工作区路径")
    parser.add_argument("--template",  default=None,  help="tablecase_template/template_headers.json（可选）")
    parser.add_argument("--output",    default=None,  help="输出 Excel 文件路径（默认 workspace/output/api_testcases_*.xlsx）")
    args = parser.parse_args()

    if not HAS_OPENPYXL:
        print("❌ 请先安装 openpyxl: pip install openpyxl")
        return

    # 1. 加载所有批次用例
    cases = load_all_batches(args.workspace)
    if not cases:
        print("⚠️  没有找到任何测试用例 JSON 文件（cases_batch_*.json）")
        return

    # 2. 自动补充 case_id
    cases = auto_case_id(cases)

    # 3. 输出路径
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.workspace) / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"api_testcases_{timestamp}.xlsx")

    # 4. 导出
    export_excel(cases, output_path)

    # 5. 打印覆盖率汇总
    total = len(cases)
    type_counts = {}
    for c in cases:
        ct = c.get("test_type", c.get("case_type", "未知"))
        type_counts[ct] = type_counts.get(ct, 0) + 1

    print(f"\n📊 覆盖率汇总（共 {total} 条用例）:")
    targets = {"正向": 0.4, "负向": 0.3, "边界": 0.2, "安全": 0.1}
    for ct, target in targets.items():
        cnt = type_counts.get(ct, 0)
        ratio = cnt / total if total else 0
        status = "✅" if ratio >= target else "⚠️ 未达标"
        print(f"   {status} {ct}: {cnt}/{total} = {ratio*100:.0f}%（目标≥{target*100:.0f}%）")

    print(f"\n📁 输出文件: {output_path}")


if __name__ == "__main__":
    main()
