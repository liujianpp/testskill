#!/usr/bin/env python3
"""25列测试用例 Excel → browser-use-case-runner 规范 xlsx 转换器。

用法:
    python convert_25col_to_ui_xlsx.py -i artifacts/xx_testcases.xlsx -o artifacts/ui_cases.xlsx

规则:
    - 默认排除「API URL」列非空的行（API 用例走 ApiAutoTest 支线）
    - --types 按覆盖维度（正向/负向/边界/安全）可选过滤，归一化后匹配
    - 用例编号取「测试项/测试点」，为空时按「模块-功能-行号」生成
    - 同编号只保留首行
"""
import argparse

from openpyxl import Workbook, load_workbook

# runner 8 列输出表头 → 25 列来源列名
HEADER_MAP = {
    "用例编号": "测试项/测试点",
    "用例名称": "用例标题",
    "功能模块": "模块",
    "优先级": "用例优先级",
    "前置条件": "前置条件",
    "测试步骤": "测试步骤",
    "测试数据": "测试数据准备",
    "预期结果": "预期结果",
}
RUNNER_HEADERS = list(HEADER_MAP.keys())
SOURCE_COLS = list(HEADER_MAP.values())


def normalize_type(value) -> str:
    """与 spectest-generate 一致的类型归一化：去「测试/用例」后缀。"""
    return str(value or "").replace("测试", "").replace("用例", "").strip()


def cell_str(v) -> str:
    return "" if v is None else str(v).strip()


def convert(input_path, output_path, sheet_name="测试用例", include_types=None):
    """执行转换，返回统计 dict。"""
    wb = load_workbook(input_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise SystemExit(f"错误: Sheet '{sheet_name}' 不存在，可用 Sheet: {wb.sheetnames}")
    ws = wb[sheet_name]

    headers = [cell_str(c.value) for c in ws[1]]
    needed = set(SOURCE_COLS) | {"API URL", "用例类型", "功能"}  # 「功能」用于回退编号生成
    col_idx = {h: headers.index(h) + 1 for h in needed if h in headers}

    stats = {"total": 0, "exported": 0, "skipped_api": 0,
             "skipped_type": 0, "skipped_dup": 0, "skipped_empty": 0}
    seen_ids = set()
    out_rows = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if all(cell_str(v) == "" for v in row):
            stats["skipped_empty"] += 1
            continue
        stats["total"] += 1

        def src(col_name, _row=row):
            i = col_idx.get(col_name)
            return cell_str(_row[i - 1]) if i else ""

        if src("API URL"):
            stats["skipped_api"] += 1
            continue
        if include_types is not None and normalize_type(src("用例类型")) not in include_types:
            stats["skipped_type"] += 1
            continue

        case_id = src("测试项/测试点") or f"{src('模块')}-{src('功能')}-{stats['total']}"
        if case_id in seen_ids:
            stats["skipped_dup"] += 1
            continue
        seen_ids.add(case_id)

        row_out = [src(c) for c in SOURCE_COLS]
        row_out[0] = case_id  # 回退生成的编号必须写入输出（源「测试项/测试点」为空）
        out_rows.append(row_out)
        stats["exported"] += 1

    out_wb = Workbook()
    out_ws = out_wb.active
    out_ws.title = "UI用例"
    out_ws.append(RUNNER_HEADERS)
    for r in out_rows:
        out_ws.append(r)
    out_wb.save(output_path)
    return stats


def main():
    ap = argparse.ArgumentParser(description="25列测试用例 → runner 规范 xlsx 转换器")
    ap.add_argument("-i", "--input", required=True, help="25列 testcases.xlsx 路径")
    ap.add_argument("-o", "--output", required=True, help="输出 ui_cases.xlsx 路径")
    ap.add_argument("--sheet", default="测试用例", help="数据 Sheet 名（默认: 测试用例）")
    ap.add_argument("--types", default=None,
                    help="用例类型白名单（逗号分隔，归一化后匹配），如: 功能,UI。留空不过滤")
    args = ap.parse_args()

    include_types = {normalize_type(t) for t in args.types.split(",") if t.strip()} if args.types else None
    stats = convert(args.input, args.output, args.sheet, include_types)

    print(f"输入: {args.input}")
    print(f"输出: {args.output}")
    print(f"总行数: {stats['total']} | 导出: {stats['exported']} | "
          f"跳过: API用例 {stats['skipped_api']}, 类型不符 {stats['skipped_type']}, "
          f"重复编号 {stats['skipped_dup']}, 空行 {stats['skipped_empty']}")


if __name__ == "__main__":
    main()
