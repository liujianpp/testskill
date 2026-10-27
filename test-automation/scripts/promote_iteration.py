#!/usr/bin/env python3
"""迭代 → 主干晋级（README「晋级规则」的脚本化，P1-4）。

用法：
    python scripts/promote_iteration.py --version 2026Q4-xxx [--confirm]

默认 dry-run 只列计划；--confirm 才执行。前置条件（人工确认）：功能已上线且回归 2 轮全绿。
动作：
1. cases/iterations/<ver>/*.xlsx 按 API URL 归属 api/web、按「模块」并入 cases/main 合表（含去重）
2. api/iterations/<ver>/**.py 移入 api/main/（conftest 在 api/ 根，fixture 引用不受层级影响）
3. web/iterations/<ver>/**.spec.ts 移入 web/main/tests/，并把 '../../main/' 引用改写为 '../'
4. 小程序清单合并为人工步骤（见 miniprogram/README.md）
5. 完成后 iterations/<ver> 归档到 cases/iterations/_promoted/<ver>-<日期>，并追加 reports/promote-log.md
安全：目标同名文件已存在时拒绝搬移该文件（不覆盖），列出待人工处理。
"""
from __future__ import annotations

import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path

from openpyxl import load_workbook

from promote_cases import COL_API, COL_MODULE, SHEET_NAME, _col_idx, _safe_name, append_rows, cell_str

REPO_ROOT = Path(__file__).resolve().parents[1]
SHEET_NAME = "测试用例"
COL_API = "API URL"


def cell_str(v) -> str:
    return "" if v is None else str(v).strip()


def merge_cases(iter_dir: Path, root: Path, confirm: bool) -> None:
    """迭代用例并入主干合表：按 API URL 归属 api/web，按「模块」合并到 <模块>.xlsx（含去重）。"""
    for row_file in sorted(iter_dir.glob("*.xlsx")):
        if row_file.name.startswith("~$"):
            continue
        wb = load_workbook(row_file, data_only=True)
        ws = wb[SHEET_NAME] if SHEET_NAME in wb.sheetnames else wb.worksheets[0]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            continue
        header = [cell_str(c) for c in rows[0]]
        i_a = _col_idx(header, COL_API)
        i_m = _col_idx(header, COL_MODULE)
        body = [r for r in rows[1:] if any(c is not None and str(c).strip() for c in r)]
        for sub, group in (
            ("api", [r for r in body if cell_str(r[i_a])]),
            ("web", [r for r in body if not cell_str(r[i_a])]),
        ):
            if not group:
                continue
            for mod in sorted({cell_str(r[i_m]) or "未分模块" for r in group}):
                mod_rows = [r for r in group if (cell_str(r[i_m]) or "未分模块") == mod]
                target = root / "cases" / "main" / sub / f"{_safe_name(mod, '未分模块')}.xlsx"
                added, skipped = append_rows(target, header, mod_rows, not confirm)
                tag = "" if confirm else "[dry-run] "
                print(f"{tag}合并 {row_file.name} 模块「{mod}」→ {target.relative_to(root)}（追加 {added}，跳过 {skipped}）")


def move_files(src_dir: Path, target_dir: Path, pattern: str, rewrite: dict, confirm: bool, root: Path) -> list:
    """把 src_dir 下匹配文件移入 target_dir（扁平化），文本做 rewrite 替换。返回冲突描述。"""
    conflicts = []
    if src_dir.is_dir():
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in sorted(src_dir.rglob(pattern)):
            dst = target_dir / f.name
            tag = "" if confirm else "[dry-run] "
            if dst.exists():
                conflicts.append(f"{f.name}（目标已存在）")
                continue
            print(f"{tag}移动 {f.relative_to(root)} → {target_dir.relative_to(root)}/{f.name}")
            if confirm:
                text = f.read_text(encoding="utf-8")
                for old, new in rewrite.items():
                    text = text.replace(old, new)
                dst.write_text(text, encoding="utf-8", newline="\n")
                f.unlink()
    return conflicts


def main() -> int:
    ap = argparse.ArgumentParser(description="迭代 → 主干晋级")
    ap.add_argument("--version", required=True, help="迭代版本号，如 2026Q4-xxx")
    ap.add_argument("--repo-root", default=str(REPO_ROOT))
    ap.add_argument("--confirm", action="store_true", help="实际执行（默认 dry-run）")
    args = ap.parse_args()

    root = Path(args.repo_root)
    ver = args.version
    if not re.fullmatch(r"[0-9A-Za-z_.\-]+", ver):
        sys.exit(f"错误：版本号含不安全字符：{ver}")

    case_iter = root / "cases" / "iterations" / ver
    api_iter = root / "api" / "iterations" / ver
    web_iter = root / "web" / "iterations" / ver
    if not any(p.is_dir() for p in (case_iter, api_iter, web_iter)):
        sys.exit(f"错误：找不到迭代目录 (cases|api|web)/iterations/{ver} 之一")

    print(f"=== 晋级 {ver}（{'执行' if args.confirm else 'dry-run'}）===")
    if case_iter.is_dir():
        merge_cases(case_iter, root, args.confirm)
    for c in move_files(api_iter, root / "api" / "main", "*.py", {}, args.confirm, root):
        print(f"⚠️ 冲突未搬移：{c}")
    for c in move_files(web_iter, root / "web" / "main" / "tests", "*.spec.ts",
                        {"../../main/": "../"}, args.confirm, root):
        print(f"⚠️ 冲突未搬移：{c}")
    print("提示：小程序清单合并为人工步骤（miniprogram/README.md）")

    if args.confirm:
        stamp = datetime.date.today().strftime("%Y%m%d")
        promoted_root = root / "cases" / "iterations" / "_promoted" / f"{ver}-{stamp}"
        promoted_root.mkdir(parents=True, exist_ok=True)
        for label, src in (("cases", case_iter), ("api", api_iter), ("web", web_iter)):
            if not src.is_dir():
                continue
            if any(src.iterdir()):
                dst = promoted_root / label
                shutil.move(str(src), str(dst))
                print(f"归档 {src.relative_to(root)} → {dst.relative_to(root)}")
            else:
                shutil.rmtree(src)
        log = root / "reports" / "promote-log.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"- {datetime.datetime.now().isoformat(timespec='seconds')} 晋级 {ver} → main\n")
        print("晋级完成，log：reports/promote-log.md")
    else:
        print("（dry-run 未做任何修改；确认后加 --confirm 执行）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
