#!/usr/bin/env python3
"""按「是否回归用例」列分拣 spectest 25 列用例 Excel 到测试资产库（P1-3）。

用法：
    python scripts/promote_cases.py --input <25列.xlsx> --version 2026Q4-xxx [--dry-run]

分拣规则（见仓库 README「分拣规则」）：
- 回归用例（是否回归用例=是）且 API URL 非空 → 追加到 cases/main/api/<模块>.xlsx
- 回归用例且 API URL 为空                   → 追加到 cases/main/web/<模块>.xlsx
- 非回归用例                                → 落 cases/iterations/<version>/<原文件名>.xlsx
- 追加按（模块 + 用例标题）去重，已存在则跳过并计数；模块名清洗为安全文件名。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook

REPO_ROOT = Path(__file__).resolve().parents[1]
SHEET_NAME = "测试用例"
COL_MODULE = "模块"
COL_TITLE = "用例标题"
COL_REGRESSION = "是否回归用例"
COL_API = "API URL"
YES_VALUES = {"是", "y", "yes", "true", "1"}


def cell_str(v) -> str:
    return "" if v is None else str(v).strip()


def _safe_name(name: str, fallback: str) -> str:
    name = re.sub(r'[\/:*?"<>|\s]+', "-", name).strip("-")
    return name or fallback


def load_rows(path: Path):
    wb = load_workbook(path, read_only=False, data_only=True)
    ws = wb[SHEET_NAME] if SHEET_NAME in wb.sheetnames else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []
    header = [cell_str(c) for c in rows[0]]
    return header, rows[1:]


def _col_idx(header: list, name: str) -> int:
    try:
        return header.index(name)
    except ValueError:
        sys.exit(f"错误：表头缺少必需列「{name}」（实际表头：{header}）")


def _is_regression(val: str) -> bool:
    return val.strip().lower() in YES_VALUES


def append_rows(target: Path, header: list, new_rows: list, dry: bool) -> tuple:
    """把 new_rows 追加到 target（不存在则新建）。返回 (追加数, 跳过数)。"""
    if not new_rows:
        return 0, 0
    existing_keys = set()
    wb = None
    ws = None
    if target.is_file():
        wb = load_workbook(target)
        ws = wb.worksheets[0]
        old = list(ws.iter_rows(values_only=True))
        t_header = [cell_str(c) for c in old[0]]
        if t_header != header:
            sys.exit(f"错误：{target} 表头与源不一致，拒绝合并")
        i_m, i_t = _col_idx(t_header, COL_MODULE), _col_idx(t_header, COL_TITLE)
        for r in old[1:]:
            if any(c is not None and str(c).strip() for c in r):
                existing_keys.add((cell_str(r[i_m]), cell_str(r[i_t])))
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = SHEET_NAME
        ws.append(header)

    i_m, i_t = _col_idx(header, COL_MODULE), _col_idx(header, COL_TITLE)
    added = skipped = 0
    for row in new_rows:
        key = (cell_str(row[i_m]), cell_str(row[i_t]))
        if key in existing_keys:
            skipped += 1
            continue
        if not dry:
            ws.append(list(row))
        existing_keys.add(key)
        added += 1
    if not dry and added:
        target.parent.mkdir(parents=True, exist_ok=True)
        wb.save(target)
    return added, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description="25 列用例分拣 → cases/main|iterations")
    ap.add_argument("--input", required=True, help="spectest 25 列用例 xlsx 路径")
    ap.add_argument("--version", default=None, help="迭代版本号（如 2026Q4-xxx）；有非回归行时必填")
    ap.add_argument("--repo-root", default=str(REPO_ROOT), help="测试资产库根目录（默认脚本所在仓库）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不写文件")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.is_file():
        sys.exit(f"错误：文件不存在：{src}")
    root = Path(args.repo_root)
    header, rows = load_rows(src)
    i_m = _col_idx(header, COL_MODULE)
    i_r = _col_idx(header, COL_REGRESSION)
    i_a = _col_idx(header, COL_API)

    main_api, main_web, iter_rows = [], [], []
    for row in rows:
        if not any(c is not None and str(c).strip() for c in row):
            continue
        if _is_regression(cell_str(row[i_r])):
            (main_api if cell_str(row[i_a]) else main_web).append(row)
        else:
            iter_rows.append(row)

    tag = "[dry-run] " if args.dry_run else ""
    total_added = total_skipped = 0
    for sub, group in (("api", main_api), ("web", main_web)):
        if not group:
            continue
        modules = sorted({cell_str(r[i_m]) or "未分模块" for r in group})
        for mod in modules:
            mod_rows = [r for r in group if (cell_str(r[i_m]) or "未分模块") == mod]
            target = root / "cases" / "main" / sub / f"{_safe_name(mod, '未分模块')}.xlsx"
            added, skipped = append_rows(target, header, mod_rows, args.dry_run)
            total_added += added
            total_skipped += skipped
            print(f"{tag}{target.relative_to(root)}  <- 模块「{mod}」追加 {added} 行，去重跳过 {skipped} 行")

    if iter_rows:
        if not args.version:
            sys.exit("错误：存在非回归用例行，需 --version 指定迭代版本号")
        dst = root / "cases" / "iterations" / args.version / src.name
        if args.dry_run:
            print(f"{tag}{dst.relative_to(root)}  <- 新建（非回归 {len(iter_rows)} 行）")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"{dst.relative_to(root)}  <- 新建（非回归 {len(iter_rows)} 行，整表副本供迭代评审）")

    print(f"完成：main 追加 {total_added} 行（跳过重复 {total_skipped}），迭代 {len(iter_rows)} 行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
