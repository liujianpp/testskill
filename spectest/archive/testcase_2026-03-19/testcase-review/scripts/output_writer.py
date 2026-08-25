#!/usr/bin/env python3
"""
Step 5: 生成带时间戳的评审报告
在原测试用例文档的基础上新增"评审意见"列，输出到 output/ 目录
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

try:
    import pandas as pd
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("缺少依赖: pip install pandas openpyxl", file=sys.stderr)
    sys.exit(1)

# 兼容补丁：部分 WPS/新版 Excel 文件包含 openpyxl 不认识的 DataValidation.id 属性
try:
    from openpyxl.worksheet.datavalidation import DataValidation as _DV
    _orig_dv_init = _DV.__init__
    def _patched_dv_init(self, *args, **kwargs):
        kwargs.pop("id", None)
        _orig_dv_init(self, *args, **kwargs)
    _DV.__init__ = _patched_dv_init
except Exception:
    pass


def load_review_results(review_path: Path) -> tuple[dict[int, str], str | int | None]:
    """返回 ({row_index: review_comment}, sheet名)"""
    with open(review_path, encoding="utf-8") as f:
        data = json.load(f)
    review_map = {
        r.get("_row_index", i): r.get("评审意见", "")
        for i, r in enumerate(data.get("results", []))
    }
    return review_map, data.get("sheet")


def write_excel_report(original_path: Path, review_map: dict[int, str],
                       output_path: Path, sheet: str | int | None = None):
    """基于原Excel文件，在最后添加评审意见列"""
    wb = load_workbook(original_path)

    # 选择正确的 Sheet（与 reader 保持一致）
    if sheet is not None and sheet in wb.sheetnames:
        ws = wb[sheet]
    else:
        ws = wb.active

    # ws.max_column 是正确的 openpyxl API（max_dimension 是字符串，不是元组）
    max_col = ws.max_column
    review_col = max_col + 1
    review_col_letter = get_column_letter(review_col)

    # 写入表头
    header_cell = ws.cell(row=1, column=review_col, value="评审意见")
    header_cell.font = Font(bold=True, color="FFFFFF")
    header_cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # 定义颜色
    fill_issue = PatternFill(start_color="FFE4E1", end_color="FFE4E1", fill_type="solid")   # 有问题 - 浅红
    fill_pass = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")    # 通过 - 浅绿
    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # 写入评审意见（从第2行开始，对应pandas的row_index 0-based）
    for row_idx in range(2, ws.max_row + 1):
        pandas_idx = row_idx - 2  # pandas DataFrame的0-based索引
        comment = review_map.get(pandas_idx, "")
        cell = ws.cell(row=row_idx, column=review_col, value=comment)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.border = border
        if comment.strip():
            cell.fill = fill_issue
        else:
            cell.fill = fill_pass

    # 调整列宽
    ws.column_dimensions[review_col_letter].width = 50

    wb.save(output_path)


def write_csv_report(original_path: Path, review_map: dict[int, str], output_path: Path):
    """基于原CSV，添加评审意见列"""
    for enc in ["utf-8", "gbk", "gb2312"]:
        try:
            df = pd.read_csv(original_path, dtype=str, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        df = pd.read_csv(original_path, dtype=str, encoding="utf-8", errors="replace")

    df["评审意见"] = [review_map.get(i, "") for i in range(len(df))]
    df.to_csv(output_path, index=False, encoding="utf-8-sig")


def generate_summary(review_map: dict[int, str]) -> str:
    """生成评审摘要"""
    total = len(review_map)
    issues = [(idx, comment) for idx, comment in review_map.items() if comment.strip()]
    passed = total - len(issues)

    # 分类统计
    categories = {}
    keywords = {
        "缺少预期结果": ["预期结果", "期望结果"],
        "步骤不清晰": ["步骤", "操作", "不清晰", "模糊", "不明确"],
        "前置条件缺失": ["前置条件", "先决条件", "预置条件"],
        "边界值未覆盖": ["边界", "边界值", "最大", "最小"],
        "缺少异常场景": ["异常", "错误", "失败", "负向"],
        "字段/接口不一致": ["字段", "接口", "API", "表名"],
    }
    for _, comment in issues:
        matched = False
        for cat, kws in keywords.items():
            if any(kw in comment for kw in kws):
                categories[cat] = categories.get(cat, 0) + 1
                matched = True
                break
        if not matched:
            categories["其他问题"] = categories.get("其他问题", 0) + 1

    lines = [
        "## 评审摘要",
        f"- 总用例数：{total}",
        f"- 有问题：{len(issues)} 条",
        f"- 通过：{passed} 条",
        f"- 通过率：{passed/total*100:.1f}%",
        "",
        "## 问题分类统计",
    ]
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        lines.append(f"- {cat}：{count} 条")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成评审报告")
    parser.add_argument("--original", required=True, help="原始测试用例文件路径")
    parser.add_argument("--review", required=True, help="评审结果JSON路径")
    parser.add_argument("--output", default=None, help="输出目录（默认: output/）")
    args = parser.parse_args()

    print(f"\n=== Step 5: 生成评审报告 ===")

    original_path = Path(args.original)
    if not original_path.is_absolute():
        original_path = SKILL_DIR / original_path

    review_path = Path(args.review)
    if not review_path.is_absolute():
        review_path = SKILL_DIR / review_path

    output_dir = Path(args.output) if args.output else SKILL_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    # 生成带时间戳的输出文件名
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = original_path.stem
    suffix = original_path.suffix.lower()
    # CSV输出也保存为xlsx以便查看颜色
    output_suffix = ".xlsx" if suffix in (".xlsx", ".xls") else ".csv"
    output_path = output_dir / f"{stem}_reviewed_{ts}{output_suffix}"

    # 加载评审结果（同时获取 sheet 信息，与 reader 保持一致）
    review_map, sheet = load_review_results(review_path)

    # 写入报告
    if suffix in (".xlsx", ".xls"):
        write_excel_report(original_path, review_map, output_path, sheet=sheet)
    else:
        if output_suffix == ".xlsx":
            # CSV转Excel输出
            for enc in ["utf-8", "gbk", "gb2312"]:
                try:
                    import pandas as pd
                    df = pd.read_csv(original_path, dtype=str, encoding=enc)
                    df["评审意见"] = [review_map.get(i, "") for i in range(len(df))]
                    df.to_excel(output_path, index=False)
                    break
                except UnicodeDecodeError:
                    continue
        else:
            write_csv_report(original_path, review_map, output_path)

    # 生成摘要
    summary = generate_summary(review_map)
    summary_path = output_dir / f"{stem}_summary_{ts}.md"
    summary_path.write_text(summary, encoding="utf-8")

    print(f"  评审报告: {output_path}")
    print(f"  评审摘要: {summary_path}")
    print(f"\n{summary}")
    print(f"\n[完成] 报告生成成功")


if __name__ == "__main__":
    main()
