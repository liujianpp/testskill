#!/usr/bin/env python3
"""
从当前变更目录的 artifacts/*.xlsx 中读取「执行结果」列，汇总通过/失败/阻塞/未执行，
输出 JSON 供 opentest-report 编写报告使用。

用法：
    python read_execution_results.py --change-dir opentest/changes/<name>
    或
    python read_execution_results.py --xlsx path/to/artifacts/xxx_cases.xlsx
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Optional


EXEC_COLUMN = "执行结果"
MODULE_COLUMN = "功能模块"
# 规范化的执行结果取值（与 Excel 中用户填写一致）
PASS = "通过"
FAIL = "失败"
BLOCKED = "阻塞"
OTHER = "未执行"


# 执行结果同义词：归一化为 通过/失败/阻塞/未执行
_PASS_VARIANTS = (
    PASS, "已通过", "✓", "√", "✔", "☑",
    "pass", "PASS", "Pass", "passed", "PASSED", "Passed",
    "OK", "ok", "成功", "Yes", "yes",
)
_FAIL_VARIANTS = (
    FAIL, "不通过", "✗", "×", "✘", "❌",
    "fail", "FAIL", "Fail", "failed", "FAILED", "Failed",
    "NG", "ng", "否", "No", "no", "N",
)
_BLOCKED_VARIANTS = (
    BLOCKED, "阻塞", "阻塞中",
    "block", "Block", "BLOCK", "blocked", "Blocked", "BLOCKED",
    "跳过", "skip", "Skip", "SKIP", "暂不执行", "无法执行",
)
_OTHER_VARIANTS = (
    OTHER, "未执行", "待执行", "未测", "待定", "TBD",
    "Pending", "pending", "PENDING", "-", "--", "/",
)


def normalize_result(value: str) -> str:
    """将单元格内容规范为 通过/失败/阻塞/未执行。"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return OTHER
    v = str(value).strip()
    if v in _PASS_VARIANTS:
        return PASS
    if v in _FAIL_VARIANTS:
        return FAIL
    if v in _BLOCKED_VARIANTS:
        return BLOCKED
    if v in _OTHER_VARIANTS:
        return OTHER
    return OTHER


def read_xlsx_execution(xlsx_path: str) -> dict:
    """读取 xlsx 中「测试用例」工作表的执行结果列，返回汇总统计。"""
    try:
        from openpyxl import load_workbook
    except ImportError:
        print('{"error": "需要安装 openpyxl: pip install openpyxl"}', file=sys.stderr)
        sys.exit(1)

    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    if "测试用例" not in wb.sheetnames:
        ws = wb.active
    else:
        ws = wb["测试用例"]

    # 找表头列索引（第一行）
    headers = []
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        headers.append(cell.value)
    try:
        exec_col = headers.index(EXEC_COLUMN) + 1
    except ValueError:
        exec_col = 9  # 默认第 9 列
    try:
        module_col = headers.index(MODULE_COLUMN) + 1
    except ValueError:
        module_col = 3

    total = 0
    counts = {PASS: 0, FAIL: 0, BLOCKED: 0, OTHER: 0}
    by_module = defaultdict(lambda: {PASS: 0, FAIL: 0, BLOCKED: 0, OTHER: 0})

    for row in range(2, ws.max_row + 1):
        exec_val = ws.cell(row=row, column=exec_col).value
        module_val = ws.cell(row=row, column=module_col).value
        module_name = str(module_val).strip() if module_val else "未分类"
        result = normalize_result(exec_val)
        total += 1
        counts[result] += 1
        by_module[module_name][result] += 1

    wb.close()
    return {
        "total": total,
        "通过": counts[PASS],
        "失败": counts[FAIL],
        "阻塞": counts[BLOCKED],
        "未执行": counts[OTHER],
        "by_module": {k: dict(v) for k, v in sorted(by_module.items())},
    }


def find_xlsx_in_change_dir(change_dir: str) -> Optional[str]:
    """在变更目录的 artifacts/ 下查找 *_cases.xlsx。"""
    artifacts = os.path.join(change_dir, "artifacts")
    if not os.path.isdir(artifacts):
        return None
    for name in os.listdir(artifacts):
        if name.endswith("_cases.xlsx") or name.endswith(".xlsx"):
            return os.path.join(artifacts, name)
    return None


def main():
    parser = argparse.ArgumentParser(description="Read execution results from Excel for report")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--change-dir", "-C", help="Change directory (e.g. opentest/changes/xxx)")
    group.add_argument("--xlsx", "-x", help="Path to *_cases.xlsx")
    parser.add_argument("--json", action="store_true", help="Output JSON (default)")
    args = parser.parse_args()

    xlsx_path = None
    if args.xlsx:
        xlsx_path = args.xlsx
    else:
        xlsx_path = find_xlsx_in_change_dir(args.change_dir)

    if not xlsx_path or not os.path.isfile(xlsx_path):
        out = {"error": "未找到用例 Excel", "path": xlsx_path or args.change_dir}
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(1)

    try:
        stats = read_xlsx_execution(xlsx_path)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "path": xlsx_path}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
