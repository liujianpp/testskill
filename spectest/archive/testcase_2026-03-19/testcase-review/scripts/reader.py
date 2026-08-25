#!/usr/bin/env python3
"""
Step 2: Excel/CSV 智能解析
自动识别表头，将测试用例转换为结构化 JSON
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("缺少依赖：pip install pandas openpyxl", file=sys.stderr)
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

SKILL_DIR = Path(__file__).parent.parent

# 常见表头字段的标准化映射（中英文均支持）
FIELD_ALIASES = {
    # 以「测试用例管理.xlsx」的表头为基准，同时保留常见别名保持兼容性
    "system":       ["系统/项目", "system", "project"],
    "module":       ["模块", "module"],
    "function":     ["功能", "function"],
    "test_item":    ["测试项", "test_item"],
    "title":        ["用例标题", "title"],
    "precondition": ["前置条件", "预置条件", "precondition", "pre_condition", "前提", "先决条件"],
    "tables":       ["涉及到数据库表", "涉及表", "相关表", "数据库表", "表名", "table", "tables", "db_table"],
    "test_data":    ["测试数据", "test_data", "测试入参", "入参", "请求数据"],
    "steps":        ["测试步骤", "操作步骤", "步骤", "steps", "step", "操作", "测试操作"],
    "expected":     ["预期结果", "期望结果", "期望", "expected", "expected_result", "预期", "期望值"],
    "validation_sql": ["验证SQL", "验证sql", "validation_sql", "校验SQL", "checkSQL"],
    "actual":       ["实际结果", "实际", "actual", "actual_result"],
    "status":       ["是否通过", "测试结果", "通过/失败", "状态", "status", "result", "pass/fail"],
    "work_hours":   ["预计工时(h)", "预计工时", "工时", "work_hours"],
    "exec_time":    ["执行时间(年月日)", "exec_time"],
    "progress":     ["测试进度(%)", "测试进度", "进度", "progress"],
    "case_type":    ["用例类型", "类型", "case_type", "type"],
    "priority":     ["用例优先级", "优先级", "级别", "priority", "level", "重要程度"],
    "is_regression":["是否回归用例", "回归用例", "是否回归", "is_regression"],
    "is_blocking":  ["是否阻塞上线", "阻塞上线", "is_blocking"],
    "api_url":      ["API URL", "api_url", "接口地址", "接口URL", "接口路径", "api_path"],
    "bug_count":    ["BUG数", "bug数", "bug_count", "缺陷数"],
    "bug_unresolved":["BUG未解决数", "bug未解决数", "bug_unresolved", "未解决缺陷数"],
    "requirement_id":["关联需求ID", "关联需求", "需求ID", "requirement_id", "requirement_ref", "需求编号"],
    "case_version": ["用例版本", "case_version", "版本", "version"],
    # 保留兼容旧格式
    "id":           ["用例编号", "编号", "id", "case_id", "用例id", "序号", "no.", "no", "#"],
    "remark":       ["备注", "remark", "comment", "note", "说明"],
}


def normalize_columns(df: pd.DataFrame) -> dict[str, str]:
    """返回 {标准字段名: 原始列名} 的映射"""
    col_map = {}
    raw_cols_lower = {c.strip().lower(): c for c in df.columns}
    for std_field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias.lower() in raw_cols_lower:
                col_map[std_field] = raw_cols_lower[alias.lower()]
                break
    return col_map


def detect_sheet(file_path: Path) -> str | int:
    """自动识别包含测试用例的 Sheet（优先匹配名称，否则取数据最多的）"""
    xl = pd.ExcelFile(file_path)
    sheet_names = xl.sheet_names
    if len(sheet_names) == 1:
        return sheet_names[0]

    print(f"  发现多个 Sheet: {sheet_names}")
    # 优先按名称匹配
    keywords = ["用例", "testcase", "test case", "测试", "cases", "sheet1"]
    for name in sheet_names:
        if any(kw in str(name).lower() for kw in keywords):
            print(f"  自动选择 Sheet: {name}")
            return name

    # 取行数最多的 Sheet（跳过空 Sheet）
    best = sheet_names[0]
    best_rows = 0
    for name in sheet_names:
        try:
            df_tmp = pd.read_excel(file_path, sheet_name=name, dtype=str, nrows=5)
            rows = len(df_tmp)
            if rows > best_rows:
                best_rows = rows
                best = name
        except Exception:
            pass
    print(f"  自动选择数据最多的 Sheet: {best}")
    return best


def read_testcases(file_path: Path, sheet: str | int | None = None) -> tuple[list[dict], str | int, dict]:
    """返回 (testcases列表, 实际使用的sheet名, col_map)"""
    suffix = file_path.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        chosen_sheet = sheet if sheet is not None else detect_sheet(file_path)
        df = pd.read_excel(file_path, sheet_name=chosen_sheet, dtype=str)
    elif suffix == ".csv":
        chosen_sheet = None
        # 尝试多种编码
        for enc in ["utf-8", "gbk", "gb2312"]:
            try:
                df = pd.read_csv(file_path, dtype=str, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            df = pd.read_csv(file_path, dtype=str, encoding="utf-8", errors="replace")
    else:
        print(f"不支持的文件格式: {suffix}，仅支持 .xlsx/.xls/.csv", file=sys.stderr)
        sys.exit(1)

    # 清理列名（去除首尾空格、NaN 列名）
    df.columns = [str(c).strip() if not pd.isna(c) else f"列{i}" for i, c in enumerate(df.columns)]
    # 过滤全空行
    df = df.dropna(how="all").reset_index(drop=True)

    col_map = normalize_columns(df)
    print(f"  识别到的字段映射: {col_map}")

    testcases = []
    for idx, row in df.iterrows():
        # _row_index 对应 Excel 中的数据行（0-based，不含表头）
        tc = {"_row_index": int(idx), "_raw_columns": list(df.columns)}
        # 保留原始所有字段
        for col in df.columns:
            val = row[col]
            tc[col] = "" if pd.isna(val) else str(val).strip()
        # 添加标准化字段（方便后续处理）
        tc["_normalized"] = {
            std: str(row.get(orig, "")).strip()
            for std, orig in col_map.items()
            if not pd.isna(row.get(orig, float("nan")))
        }
        testcases.append(tc)

    return testcases, chosen_sheet, col_map


def main():
    parser = argparse.ArgumentParser(description="解析测试用例文件")
    parser.add_argument("--input", required=True, help="测试用例文件路径")
    parser.add_argument("--sheet", default=None, help="指定 Excel Sheet 名称（默认自动识别）")
    parser.add_argument("--output", default=None, help="输出JSON路径（默认: testcase/parsed_testcases.json）")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = SKILL_DIR / input_path

    output_path = Path(args.output) if args.output else SKILL_DIR / "testcase" / "parsed_testcases.json"

    print(f"\n=== Step 2: 解析测试用例 ===")
    print(f"  输入文件: {input_path}")

    testcases, used_sheet, col_map = read_testcases(input_path, sheet=args.sheet)
    if used_sheet is not None:
        print(f"  使用 Sheet: {used_sheet}")
    print(f"  解析完成: 共 {len(testcases)} 条测试用例")

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total": len(testcases),
                "source_file": str(input_path),
                "sheet": used_sheet,
                "col_map": col_map,
                "testcases": testcases,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"  输出文件: {output_path}")
    print(f"[完成] 测试用例解析成功，共 {len(testcases)} 条")


if __name__ == "__main__":
    main()
