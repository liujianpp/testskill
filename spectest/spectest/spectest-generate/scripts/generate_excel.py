#!/usr/bin/env python3
"""
SpecTest Excel 用例生成脚本：根据 testcases.json 生成多Sheet Excel 文件。

用法：
    python generate_excel_with_sheets.py --input testcases.json --output artifacts/cases.xlsx

生成3个Sheet：
1. 测试用例 - 标准25列格式
2. 功能点覆盖矩阵 - 显示每个功能点的覆盖维度
3. 覆盖率汇总 - 统计测试类型、优先级等分布
"""
import argparse
import json
import os
import sys
from datetime import datetime
from collections import defaultdict


# 覆盖维度定义
COVERAGE_DIMS = [
    "正常流程", "数据展示", "边界条件",
    "异常流程", "空数据", "权限控制", "业务规则", "数据一致性"
]

# 关键词 → 维度映射
DIM_KEYWORDS = {
    "正常流程": ["正向", "正常", "成功", "主流程", "主成功"],
    "数据展示": ["展示", "显示", "列表", "详情", "查看", "数据准确"],
    "边界条件": ["边界", "最小", "最大", "空", "最长", "超长", "limit"],
    "异常流程": ["异常", "错误", "失败", "exception", "超时", "网络"],
    "空数据": ["空数据", "无数据", "没有数据", "空结果", "空状态", "无结果"],
    "权限控制": ["权限", "越权", "未登录", "角色", "permission", "auth"],
    "业务规则": ["业务规则", "约束", "限制", "规则", "判定"],
    "数据一致性": ["一致", "验证SQL", "数据库", "DB", "sql"],
}


def get_field(tc, field_name):
    """获取测试用例字段，支持多种字段名映射（包括中文字段名）。"""
    field_mappings = {
        "title": ["name", "用例标题"],
        "test_type": ["type", "用例类型"],
        "expected_result": ["expected", "预期结果"],
        "preconditions": ["precondition", "前置条件"],
        "db_tables": ["database_tables", "涉及相关数据库表"],
        "steps": ["test_steps", "测试步骤"],
        "validation_sql": ["verify_sql", "验证SQL"],
        "test_progress": ["progress", "测试进度"],
        "case_type": ["testcase_type", "用例类型"],
        "project": ["系统/项目"],
        "module": ["模块"],
        "feature": ["功能"],
        "test_item": ["测试项"],
        "test_data": ["测试数据准备"],
        "actual_result": ["实际结果"],
        "is_passed": ["是否通过"],
        "estimated_hours": ["预估工时"],
        "execution_time": ["执行时间"],
        "priority": ["用例优先级"],
        "is_regression": ["是否回归用例"],
        "is_blocking": ["是否阻塞上线"],
        "requirement_id": ["关联需求ID"],
        "api_url": ["API URL"],
        "bug_count": ["BUG数"],
        "unresolved_bug_count": ["BUG未解决数"],
        "version": ["用例版本"]
    }

    if field_name in tc and tc[field_name]:
        return tc[field_name]

    if field_name in field_mappings:
        for mapped_name in field_mappings[field_name]:
            if mapped_name in tc and tc[mapped_name]:
                return tc[mapped_name]

    return ""


def normalize_test_type(test_type: str) -> str:
    """标准化测试类型：移除"测试"后缀，统一格式。"""
    if not test_type:
        return "正向"
    # 移除"测试"、"用例"等后缀
    normalized = test_type.replace("测试", "").replace("用例", "").strip()
    return normalized or "正向"


def infer_coverage_dims(case: dict) -> list[str]:
    """从用例内容推断覆盖的维度"""
    text = " ".join([
        str(get_field(case, "title")),
        str(case.get("description", "")),
        str(normalize_test_type(get_field(case, "test_type"))),
        str(case.get("design_method", "")),
        str(get_field(case, "expected_result")),
        str(case.get("notes", "")),
    ]).lower()

    dims = []
    for dim, keywords in DIM_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            dims.append(dim)
    return dims


def _make_border():
    """创建细边框样式"""
    from openpyxl.styles import Side, Border
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)


def _write_coverage_matrix(ws, cases, border, data_font):
    """功能点 × 覆盖维度矩阵"""
    from openpyxl.styles import PatternFill, Font, Alignment

    # 按「模块/功能」分组
    feature_groups = defaultdict(list)
    for c in cases:
        module = get_field(c, "module") or "未知"
        feature = get_field(c, "feature") or "未知"
        key = f"{module}/{feature}"
        feature_groups[key].append(c)

    title_font = Font(name="微软雅黑", bold=True, size=12)
    hdr_font = Font(name="微软雅黑", bold=True, color="FFFFFF", size=10)
    check_font = Font(name="微软雅黑", size=11, color="375623")

    ws.cell(1, 1, "功能点覆盖维度矩阵").font = title_font
    ws.cell(2, 1, f"共 {len(feature_groups)} 个功能点  |  {len(cases)} 条用例")

    # 表头行
    header_row = 4
    ws.cell(header_row, 1, "功能点（模块/功能）").font = hdr_font
    ws.cell(header_row, 1).fill = PatternFill("solid", fgColor="2E75B6")
    ws.cell(header_row, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions["A"].width = 30

    for di, dim in enumerate(COVERAGE_DIMS, 2):
        c = ws.cell(header_row, di, dim)
        c.font = hdr_font
        c.fill = PatternFill("solid", fgColor="2E75B6")
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[_get_col_letter(di)].width = 12

    ws.column_dimensions[_get_col_letter(len(COVERAGE_DIMS) + 2)].width = 8
    cell = ws.cell(header_row, len(COVERAGE_DIMS) + 2, "用例数")
    cell.font = hdr_font
    cell.fill = PatternFill("solid", fgColor="2E75B6")
    cell.alignment = Alignment(horizontal="center", vertical="center")

    covered_fill = PatternFill("solid", fgColor="E2EFDA")
    miss_fill = PatternFill("solid", fgColor="FCE4D6")

    for ri, (feat_key, feat_cases) in enumerate(feature_groups.items(), header_row + 1):
        all_dims_covered = set()
        for c in feat_cases:
            all_dims_covered.update(infer_coverage_dims(c))

        ws.cell(ri, 1, feat_key).font = data_font
        ws.cell(ri, 1).alignment = Alignment(horizontal="left", vertical="center")

        for di, dim in enumerate(COVERAGE_DIMS, 2):
            if dim in all_dims_covered:
                cell = ws.cell(ri, di, "✓")
                cell.fill = covered_fill
                cell.font = check_font
            else:
                cell = ws.cell(ri, di, "")
                cell.fill = miss_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        cell = ws.cell(ri, len(COVERAGE_DIMS) + 2, len(feat_cases))
        cell.font = data_font
        cell.alignment = Alignment(horizontal="center")


def _write_stats_sheet(ws, cases, border, data_font):
    """覆盖率汇总 Sheet"""
    from openpyxl.styles import Font, PatternFill, Alignment

    title_font = Font(name="微软雅黑", bold=True, size=13)
    sub_font = Font(name="微软雅黑", bold=True, size=11)

    ws.cell(1, 1, "测试用例覆盖率汇总").font = title_font
    ws.cell(2, 1, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 12

    total = len(cases)
    item_counts = {}  # 按测试类型统计
    module_counts = {}
    feature_counts = {}

    for c in cases:
        ct_raw = get_field(c, "test_type") or "未知"
        ct = normalize_test_type(ct_raw)
        item_counts[ct] = item_counts.get(ct, 0) + 1
        mod = get_field(c, "module") or "未知"
        module_counts[mod] = module_counts.get(mod, 0) + 1
        feat_mod = get_field(c, "module") or ""
        feat_feat = get_field(c, "feature") or ""
        feat = f"{feat_mod}/{feat_feat}"
        feature_counts[feat] = feature_counts.get(feat, 0) + 1

    row = 4
    ws.cell(row, 1, "一、测试类型分布").font = sub_font
    row += 1
    ws.cell(row, 1, "测试类型")
    ws.cell(row, 2, "数量")
    ws.cell(row, 3, "占比")
    ws.cell(row, 4, "目标")
    row += 1
    targets = {"正向": "≥40%", "负向": "≥30%", "边界": "≥20%", "安全": "≥10%", "异常": "≥10%"}
    for ct, cnt in sorted(item_counts.items()):
        ws.cell(row, 1, ct)
        ws.cell(row, 2, cnt)
        ws.cell(row, 3, f"{cnt/total*100:.1f}%" if total else "0%")
        ws.cell(row, 4, targets.get(ct, "-"))
        row += 1
    ws.cell(row, 1, "合计")
    ws.cell(row, 2, total)
    row += 2

    ws.cell(row, 1, "二、模块用例分布").font = sub_font
    row += 1
    ws.cell(row, 1, "模块")
    ws.cell(row, 2, "用例数")
    row += 1
    for mod, cnt in sorted(module_counts.items(), key=lambda x: -x[1]):
        ws.cell(row, 1, mod)
        ws.cell(row, 2, cnt)
        row += 1
    row += 1

    ws.cell(row, 1, "三、功能点用例数分布").font = sub_font
    row += 1
    ws.cell(row, 1, "功能点")
    ws.cell(row, 2, "用例数")
    row += 1
    for feat, cnt in sorted(feature_counts.items(), key=lambda x: -x[1]):
        ws.cell(row, 1, feat)
        ws.cell(row, 2, cnt)
        row += 1
    row += 1

    ws.cell(row, 1, "四、按优先级统计").font = sub_font
    row += 1
    ws.cell(row, 1, "优先级")
    ws.cell(row, 2, "用例数")
    ws.cell(row, 3, "占比")
    row += 1

    # 统计优先级
    priority_counts = {}
    for c in cases:
        priority = get_field(c, "priority") or "P1"
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    # 按优先级顺序排序（P0 > P1 > P2）
    for priority in ["P0", "P1", "P2"]:
        if priority in priority_counts:
            cnt = priority_counts[priority]
            ws.cell(row, 1, priority)
            ws.cell(row, 2, cnt)
            ws.cell(row, 3, f"{cnt/total*100:.0f}%" if total else "0%")
            row += 1

    # 合计行
    ws.cell(row, 1, "合计")
    ws.cell(row, 2, total)


def _get_col_letter(idx):
    """获取列字母（A, B, ..., Z, AA, AB, ...）"""
    result = ""
    while idx > 0:
        idx -= 1
        result = chr(idx % 26 + ord('A')) + result
        idx //= 26
    return result


def create_excel_with_openpyxl(test_cases: list, output_path: str) -> None:
    """使用 openpyxl 创建包含3个Sheet的Excel文件。"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        print("错误：需要安装 openpyxl，请运行：pip install openpyxl", file=sys.stderr)
        sys.exit(1)

    wb = Workbook()

    # ══════════════════════════════════════════════════════════
    # Sheet 1：测试用例
    # ══════════════════════════════════════════════════════════
    sheet = wb.active
    sheet.title = "测试用例"

    # 标准 25 列表头
    headers = [
        "系统/项目", "模块", "功能", "测试项/测试点", "用例标题",
        "前置条件", "涉及相关数据库表", "测试数据准备", "测试步骤", "预期结果",
        "验证SQL", "实际结果", "是否通过", "预估工时", "执行时间",
        "测试进度", "用例类型", "用例优先级", "是否回归用例", "是否阻塞上线",
        "关联需求ID", "API URL", "BUG数", "BUG未解决数", "用例版本"
    ]

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    data_font = Font(name="微软雅黑", size=10)
    border = _make_border()

    # 写入表头
    for col_idx, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_idx)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

    # 设置列宽
    column_widths = [15, 20, 15, 25, 35, 25, 30, 30, 40, 30,
                     35, 20, 10, 10, 15, 12, 12, 10, 12, 12,
                     15, 35, 10, 15, 12]
    for col_idx, width in enumerate(column_widths, 1):
        sheet.column_dimensions[get_column_letter(col_idx)].width = width

    # 冻结首行
    sheet.freeze_panes = "A2"

    # 写入数据
    for row_idx, tc in enumerate(test_cases, 2):
        # 根据测试类型设置行背景色
        tc_type_raw = get_field(tc, "test_type") or "正向"
        tc_type = normalize_test_type(tc_type_raw)
        type_fills = {
            "正向": "FFFFFF",
            "负向": "FCE4D6",
            "边界": "FFF2CC",
            "安全": "E2EFDA",
            "异常": "FCE4D6"
        }
        fill_color = type_fills.get(tc_type, "FFFFFF")
        row_fill = PatternFill("solid", fgColor=fill_color)

        sheet.cell(row=row_idx, column=1, value=get_field(tc, "project"))
        sheet.cell(row=row_idx, column=2, value=get_field(tc, "module"))
        sheet.cell(row=row_idx, column=3, value=get_field(tc, "feature"))
        sheet.cell(row=row_idx, column=4, value=get_field(tc, "test_item"))
        sheet.cell(row=row_idx, column=5, value=get_field(tc, "title"))
        sheet.cell(row=row_idx, column=6, value=get_field(tc, "preconditions"))
        sheet.cell(row=row_idx, column=7, value=get_field(tc, "db_tables"))
        sheet.cell(row=row_idx, column=8, value=get_field(tc, "test_data"))
        sheet.cell(row=row_idx, column=9, value=get_field(tc, "steps"))
        sheet.cell(row=row_idx, column=10, value=get_field(tc, "expected_result"))
        sheet.cell(row=row_idx, column=11, value=get_field(tc, "validation_sql"))
        sheet.cell(row=row_idx, column=12, value=get_field(tc, "actual_result"))
        sheet.cell(row=row_idx, column=13, value=get_field(tc, "is_passed"))
        sheet.cell(row=row_idx, column=14, value=get_field(tc, "estimated_hours"))
        sheet.cell(row=row_idx, column=15, value=get_field(tc, "execution_time"))
        sheet.cell(row=row_idx, column=16, value=get_field(tc, "test_progress"))
        sheet.cell(row=row_idx, column=17, value=get_field(tc, "case_type"))
        sheet.cell(row=row_idx, column=18, value=get_field(tc, "priority") or "P1")
        sheet.cell(row=row_idx, column=19, value=get_field(tc, "is_regression"))
        sheet.cell(row=row_idx, column=20, value=get_field(tc, "is_blocking"))
        sheet.cell(row=row_idx, column=21, value=get_field(tc, "requirement_id"))
        sheet.cell(row=row_idx, column=22, value=get_field(tc, "api_url"))
        sheet.cell(row=row_idx, column=23, value=get_field(tc, "bug_count") or 0)
        sheet.cell(row=row_idx, column=24, value=get_field(tc, "unresolved_bug_count") or 0)
        sheet.cell(row=row_idx, column=25, value=get_field(tc, "version"))

        # 应用样式
        for col_idx in range(1, 26):
            cell = sheet.cell(row=row_idx, column=col_idx)
            cell.fill = row_fill
            cell.font = data_font
            cell.border = border
            if col_idx in [6, 8, 9, 10]:  # 前置条件、测试数据、测试步骤、预期结果
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # ══════════════════════════════════════════════════════════
    # Sheet 2：功能点覆盖矩阵
    # ══════════════════════════════════════════════════════════
    ws2 = wb.create_sheet("功能点覆盖矩阵")
    _write_coverage_matrix(ws2, test_cases, border, data_font)

    # ══════════════════════════════════════════════════════════
    # Sheet 3：覆盖率汇总
    # ══════════════════════════════════════════════════════════
    ws3 = wb.create_sheet("覆盖率汇总")
    _write_stats_sheet(ws3, test_cases, border, data_font)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    wb.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate Excel test cases from JSON")
    parser.add_argument("--input", "-i", required=True, help="Path to testcases.json")
    parser.add_argument("--output", "-o", required=True, help="Output .xlsx path")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8-sig") as f:
        data = json.load(f)

    # 支持两种格式：
    # 1. 直接数组：[{...}, {...}]
    # 2. 包裹格式：{"testcases": [{...}, {...}]}
    if isinstance(data, list):
        test_cases = data
    elif isinstance(data, dict) and "testcases" in data:
        test_cases = data["testcases"]
    else:
        print("错误：JSON 格式应为用例数组或 {\"testcases\": [...]} 格式", file=sys.stderr)
        sys.exit(1)

    create_excel_with_openpyxl(test_cases, args.output)
    print(f"已生成：{args.output}")
    print(f"共 {len(test_cases)} 条测试用例")
    print(f"包含3个Sheet：测试用例、功能点覆盖矩阵、覆盖率汇总")


if __name__ == "__main__":
    main()
