#!/usr/bin/env python3
"""
测试用例格式转换脚本
将不同表头的 Excel 测试用例文件转换为统一标准表头（25列）的 Excel 文件
"""

import sys
import os
import re
import argparse
import json
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas 未安装，请运行: pip install pandas --break-system-packages")
    sys.exit(1)

try:
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("ERROR: openpyxl 未安装，请运行: pip install openpyxl --break-system-packages")
    sys.exit(1)

# ============================================================
# 标准25列定义（按顺序）
# ============================================================
STANDARD_HEADERS = [
    ("project",          "系统/项目"),
    ("module",           "模块"),
    ("feature",          "功能"),
    ("test_item",        "测试项"),
    ("title",            "用例标题"),
    ("preconditions",    "前置条件"),
    ("db_tables",        "涉及到数据库表"),
    ("test_data",        "测试数据"),
    ("steps",            "测试步骤"),
    ("expected_result",  "预期结果"),
    ("validation_sql",   "验证SQL"),
    ("actual_result",    "实际结果"),
    ("is_passed",        "是否通过"),
    ("estimated_hours",  "预计工时(h)"),
    ("execute_date",     "执行时间(年月日)"),
    ("test_progress",    "测试进度(%)"),
    ("case_type",        "用例类型"),
    ("priority",         "用例优先级"),
    ("is_regression",    "是否回归用例"),
    ("is_blocker",       "是否阻塞上线"),
    ("requirement_id",   "关联需求ID"),
    ("api_url",          "API URL"),
    ("bug_count",        "BUG数"),
    ("bug_unresolved",   "BUG未解决数"),
    ("case_version",     "用例版本"),
]

STANDARD_KEYS = [k for k, _ in STANDARD_HEADERS]
STANDARD_NAMES = [n for _, n in STANDARD_HEADERS]

# ============================================================
# 层级列：这些列在源文件中常被合并单元格，需向下填充（forward-fill）
# 覆盖：系统/项目、模块、功能、测试项
# ============================================================
FFILL_KEYS = {"project", "module", "feature", "test_item"}

# ============================================================
# 列名映射规则（源列名 → 标准key）
# 支持模糊匹配，先精确，再关键词
# ============================================================
MAPPING_RULES = {
    # 系统/项目
    "project":         ["系统/项目", "项目", "系统", "归属", "所属系统", "project", "system"],
    # 模块
    "module":          ["模块", "系统模块", "module", "一级模块", "功能模块", "父模块"],
    # 功能
    "feature":         ["功能", "功能点", "feature", "子功能", "功能名称", "二级功能"],
    # 测试项
    "test_item":       ["测试项", "test_item", "检查项", "测试子项"],
    # 用例标题
    "title":           ["用例标题", "测试用例名称", "用例名称", "标题", "title", "用例名", "case_name", "用例title", "testcase"],
    # 前置条件
    "preconditions":   ["前置条件", "preconditions", "前提条件", "预置条件", "先决条件"],
    # 数据库表
    "db_tables":       ["涉及到数据库表", "数据库表", "db_tables", "db表", "database_table", "涉及表"],
    # 测试数据
    "test_data":       ["测试数据", "test_data", "输入数据", "数据", "data"],
    # 测试步骤
    "steps":           ["测试步骤", "步骤", "steps", "操作步骤", "执行步骤", "step"],
    # 预期结果
    "expected_result": ["预期结果", "预期", "expected_result", "期望结果", "expected", "预期输出"],
    # 验证SQL
    "validation_sql":  ["验证sql", "validation_sql", "sql", "验证语句", "check_sql", "数据库验证"],
    # 实际结果
    "actual_result":   ["实际结果", "actual_result", "实际", "actual", "执行结果"],
    # 是否通过
    "is_passed":       ["是否通过", "状态", "is_passed", "通过", "pass", "测试结果", "result", "用例结果"],
    # 预计工时
    "estimated_hours": ["预计工时", "工时", "estimated_hours", "预计时长", "时长"],
    # 执行时间
    "execute_date":    ["执行时间", "测试时间", "execute_date", "执行日期", "date", "时间"],
    # 测试进度
    "test_progress":   ["测试进度", "test_progress", "进度", "progress"],
    # 用例类型
    "case_type":       ["用例类型", "case_type", "测试类型", "type"],
    # 优先级
    "priority":        ["用例优先级", "优先级", "priority", "级别", "p级别"],
    # 是否回归
    "is_regression":   ["是否回归用例", "回归用例", "is_regression", "是否回归", "regression"],
    # 是否阻塞上线
    "is_blocker":      ["是否阻塞上线", "阻塞上线", "is_blocker", "是否阻塞", "blocker"],
    # 关联需求ID
    "requirement_id":  ["关联需求id", "需求id", "requirement_id", "需求编号", "禅道需求", "需求", "requirement"],
    # API URL
    "api_url":         ["api url", "api_url", "接口url", "接口地址", "url", "接口路径", "path"],
    # BUG数
    "bug_count":       ["bug数", "bug_count", "bug数量", "缺陷数", "defect_count"],
    # BUG未解决数
    "bug_unresolved":  ["bug未解决数", "bug_unresolved", "未解决bug", "未关闭bug"],
    # 用例版本
    "case_version":    ["用例版本", "case_version", "版本", "version", "用例v"],
}


def normalize(text):
    """规范化列名：去空格、转小写"""
    if not text:
        return ""
    return re.sub(r'\s+', '', str(text)).lower()


def build_mapping(source_columns):
    """
    将源列名映射到标准key。
    返回 dict: { source_col_name: standard_key }，未匹配的列不包含在内。
    同时返回 unmapped 列表。
    """
    mapping = {}          # source_col -> standard_key
    used_keys = set()     # 已被占用的 standard_key

    norm_rules = {key: [normalize(alias) for alias in aliases]
                  for key, aliases in MAPPING_RULES.items()}

    # 第一轮：精确匹配（标准化后完全相同）
    for col in source_columns:
        col_norm = normalize(col)
        for key, aliases in norm_rules.items():
            if key in used_keys:
                continue
            if col_norm in aliases:
                mapping[col] = key
                used_keys.add(key)
                break

    # 第二轮：部分包含匹配（源列名包含alias关键词，或alias包含源列名）
    for col in source_columns:
        if col in mapping:
            continue
        col_norm = normalize(col)
        for key, aliases in norm_rules.items():
            if key in used_keys:
                continue
            for alias in aliases:
                if alias in col_norm or col_norm in alias:
                    mapping[col] = key
                    used_keys.add(key)
                    break
            if col in mapping:
                break

    unmapped = [c for c in source_columns if c not in mapping]
    return mapping, unmapped


def read_excel(file_path):
    """读取 Excel 文件，自动识别表头所在行，返回 DataFrame"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 尝试不同引擎
    engines = []
    suffix = path.suffix.lower()
    if suffix == '.xlsx':
        engines = ['calamine', 'openpyxl']
    elif suffix == '.xls':
        engines = ['xlrd']
    else:
        engines = ['calamine', 'openpyxl']

    df = None
    last_error = None

    for engine in engines:
        try:
            # 先读取所有 sheet 名
            xl = pd.ExcelFile(file_path, engine=engine)
            sheet_names = xl.sheet_names

            # 选择第一个非辅助 sheet
            target_sheet = sheet_names[0]
            for sn in sheet_names:
                if not sn.startswith('WpsReserved') and not sn.startswith('Sheet') and sn != '':
                    target_sheet = sn
                    break

            df = pd.read_excel(file_path, sheet_name=target_sheet, engine=engine, header=0)
            print(f"  [读取] 使用引擎={engine}, sheet='{target_sheet}', 行数={len(df)}, 列数={len(df.columns)}")
            break
        except Exception as e:
            last_error = e
            continue

    if df is None:
        raise RuntimeError(f"无法读取文件: {last_error}")

    # 过滤全空行
    df = df.dropna(how='all')
    # 重置索引，保证 ffill 按顺序填充
    df = df.reset_index(drop=True)
    return df


def write_excel(df_out, output_path):
    """将 DataFrame 写入标准格式的 Excel 文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "测试用例"

    # 样式定义
    header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    data_alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # 写表头
    ws.row_dimensions[1].height = 30
    for col_idx, header_name in enumerate(STANDARD_NAMES, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border

    # 写数据行
    for row_idx, row in enumerate(df_out.itertuples(index=False), start=2):
        ws.row_dimensions[row_idx].height = 65
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value if pd.notna(value) else "")
            cell.alignment = data_alignment
            cell.border = thin_border

    # 列宽设置
    col_widths = {
        1: 12,   # 系统/项目
        2: 14,   # 模块
        3: 14,   # 功能
        4: 20,   # 测试项
        5: 30,   # 用例标题
        6: 30,   # 前置条件
        7: 20,   # 数据库表
        8: 20,   # 测试数据
        9: 40,   # 测试步骤
        10: 40,  # 预期结果
        11: 40,  # 验证SQL
        12: 20,  # 实际结果
        13: 10,  # 是否通过
        14: 10,  # 预计工时
        15: 16,  # 执行时间
        16: 12,  # 测试进度
        17: 12,  # 用例类型
        18: 10,  # 用例优先级
        19: 12,  # 是否回归
        20: 12,  # 是否阻塞
        21: 14,  # 关联需求ID
        22: 30,  # API URL
        23: 8,   # BUG数
        24: 12,  # BUG未解决数
        25: 10,  # 用例版本
    }
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # 冻结首行 & 自动筛选
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(STANDARD_NAMES))}1"

    wb.save(output_path)
    print(f"  [输出] 已保存到: {output_path}")


def convert(input_path, output_path=None):
    """主转换函数"""
    input_path = str(input_path)

    # 生成输出路径
    if output_path is None:
        p = Path(input_path)
        output_path = str(p.parent / f"{p.stem}_标准格式{p.suffix}")

    print(f"\n{'='*60}")
    print(f"测试用例格式转换")
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"{'='*60}")

    # 读取源文件
    df_src = read_excel(input_path)
    source_columns = list(df_src.columns)
    print(f"\n源文件列名({len(source_columns)}列):")
    for i, col in enumerate(source_columns):
        print(f"  [{i}] {col}")

    # 构建列映射
    mapping, unmapped = build_mapping(source_columns)

    print(f"\n列映射结果:")
    for src_col, std_key in mapping.items():
        std_name = next(n for k, n in STANDARD_HEADERS if k == std_key)
        print(f"  '{src_col}' → '{std_name}'({std_key})")

    if unmapped:
        print(f"\n未映射的列（将被忽略）:")
        for col in unmapped:
            print(f"  '{col}'")

    not_found = [k for k in STANDARD_KEYS if k not in mapping.values()]
    if not_found:
        print(f"\n标准列中未找到来源（将为空）:")
        for k in not_found:
            std_name = next(n for key, n in STANDARD_HEADERS if key == k)
            print(f"  '{std_name}'({k})")

    # 反转映射: standard_key -> source_col
    rev_mapping = {v: k for k, v in mapping.items()}

    # --------------------------------------------------------
    # 合并单元格处理：对层级列（project/module/feature/test_item）
    # 做向下填充，修复 Excel 合并单元格读取后只有首行有值的问题
    # --------------------------------------------------------
    ffill_src_cols = [rev_mapping[k] for k in FFILL_KEYS if k in rev_mapping]
    if ffill_src_cols:
        print(f"\n合并单元格填充（向下填充）的列: {ffill_src_cols}")
        df_src[ffill_src_cols] = df_src[ffill_src_cols].ffill()

    # 构建输出 DataFrame
    rows = []
    for _, src_row in df_src.iterrows():
        out_row = {}
        for std_key in STANDARD_KEYS:
            src_col = rev_mapping.get(std_key)
            if src_col and src_col in df_src.columns:
                val = src_row[src_col]
                out_row[std_key] = "" if pd.isna(val) else val
            else:
                out_row[std_key] = ""
        rows.append(out_row)

    df_out = pd.DataFrame(rows, columns=STANDARD_KEYS)

    src_row_count = len(df_src)
    out_row_count = len(df_out)
    print(f"\n转换完成: {out_row_count} 行测试用例")

    # 写输出文件
    write_excel(df_out, output_path)

    # --------------------------------------------------------
    # Double-check：回读输出文件，核对行数是否与源文件一致
    # --------------------------------------------------------
    print(f"\n{'─'*40}")
    print(f"行数校验（Double Check）")
    try:
        df_verify = pd.read_excel(output_path, engine='openpyxl')
        verify_row_count = len(df_verify)
        if verify_row_count == src_row_count:
            print(f"  ✅ 行数一致：源文件 {src_row_count} 行 = 输出文件 {verify_row_count} 行")
            row_check_passed = True
        else:
            print(f"  ❌ 行数不一致！源文件 {src_row_count} 行，输出文件 {verify_row_count} 行")
            print(f"     差异 {abs(src_row_count - verify_row_count)} 行，请检查是否有全空行被过滤")
            row_check_passed = False
    except Exception as e:
        print(f"  ⚠️ 行数校验读取失败: {e}")
        row_check_passed = None
    print(f"{'─'*40}")

    # 输出映射摘要 JSON（供调试）
    summary = {
        "input": input_path,
        "output": output_path,
        "src_row_count": src_row_count,
        "out_row_count": out_row_count,
        "row_check_passed": row_check_passed,
        "ffill_columns": ffill_src_cols,
        "mapping": {src: tgt for src, tgt in mapping.items()},
        "unmapped_source_cols": unmapped,
        "empty_standard_cols": not_found,
    }
    print(f"\n转换摘要:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    return output_path, summary


def main():
    parser = argparse.ArgumentParser(description="测试用例格式转换：将任意表头Excel转为标准25列格式")
    parser.add_argument("input", help="输入Excel文件路径")
    parser.add_argument("-o", "--output", help="输出Excel文件路径（默认：原文件名_标准格式.xlsx）")
    args = parser.parse_args()

    output_path, summary = convert(args.input, args.output)
    print(f"\n✅ 转换成功！输出文件: {output_path}")


if __name__ == "__main__":
    main()
