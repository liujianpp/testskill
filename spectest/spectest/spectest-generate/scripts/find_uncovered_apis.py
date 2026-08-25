#!/usr/bin/env python3
"""
find_uncovered_apis.py
解析 OpenAPI JSON，对比已有测试用例，找出还没有覆盖的 API。
输出：api_list_to_design.json（待设计用例的 API 列表）
"""

import argparse
import json
import re
from pathlib import Path

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


def parse_openapi(api_doc_path: str) -> list[dict]:
    """从 OpenAPI JSON 中提取所有 API 端点"""
    with open(api_doc_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    apis = []
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, detail in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options"):
                continue
            apis.append({
                "method": method.upper(),
                "path": path,
                "summary": detail.get("summary", ""),
                "description": detail.get("description", ""),
                "operation_id": detail.get("operationId", ""),
                "tags": detail.get("tags", []),
                "api_key": f"{method.upper()} {path}",
            })

    print(f"📖 解析 API 文档完成，共发现 {len(apis)} 个 API 端点")
    return apis


def extract_covered_apis_from_excel(testcase_path: str) -> set[str]:
    """
    从已有测试用例 Excel 中提取已覆盖的 API 路径。
    识别常见表头关键词：接口路径、API路径、api_path、URL、路径 等。
    """
    if not testcase_path or not Path(testcase_path).exists():
        return set()

    if not HAS_OPENPYXL:
        print("⚠️  未安装 openpyxl，跳过已有用例对比（pip install openpyxl）")
        return set()

    wb = openpyxl.load_workbook(testcase_path, read_only=True, data_only=True)
    covered = set()

    # 识别"接口路径"相关列的关键词
    API_COL_KEYWORDS = ["接口路径", "api路径", "api_path", "接口", "url", "路径", "endpoint"]

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue

        # 从前3行中找表头行（含 API 路径相关列名）
        header_row_idx = None
        api_col_idx = None
        for i, row in enumerate(rows[:5]):
            for j, cell in enumerate(row):
                if cell and any(kw in str(cell).lower().replace(" ", "") for kw in API_COL_KEYWORDS):
                    header_row_idx = i
                    api_col_idx = j
                    break
            if header_row_idx is not None:
                break

        if api_col_idx is None:
            # 没找到接口路径列，尝试全文搜索 /xxx/yyy 路径格式
            for row in rows[1:]:
                for cell in row:
                    if cell and isinstance(cell, str):
                        matches = re.findall(r"(GET|POST|PUT|PATCH|DELETE)\s+(/[^\s]+)", str(cell).upper())
                        for m, p in matches:
                            covered.add(f"{m} {p}")
            continue

        # 读取该列所有值，提取 API 路径
        for row in rows[header_row_idx + 1:]:
            if api_col_idx < len(row) and row[api_col_idx]:
                cell_val = str(row[api_col_idx]).strip()
                # 尝试解析 "POST /xxx/xxx" 格式
                m = re.match(r"(GET|POST|PUT|PATCH|DELETE|HEAD)\s+(/\S+)", cell_val, re.IGNORECASE)
                if m:
                    covered.add(f"{m.group(1).upper()} {m.group(2)}")
                elif cell_val.startswith("/"):
                    # 只有路径，不知道 method，按路径模糊匹配
                    covered.add(cell_val)

    wb.close()
    print(f"📊 已有测试用例中发现 {len(covered)} 个已覆盖的 API")
    return covered


def find_uncovered(all_apis: list[dict], covered: set[str]) -> list[dict]:
    """找出 all_apis 中没有被 covered 覆盖的 API"""
    uncovered = []
    for api in all_apis:
        api_key = api["api_key"]  # "POST /address/search"
        path_only = api["path"]

        # 精确匹配 或 路径模糊匹配
        is_covered = (
            api_key in covered or
            api_key.split(" ", 1)[-1] in covered or  # 只有路径
            path_only in covered
        )
        if not is_covered:
            uncovered.append(api)

    return uncovered


def main():
    parser = argparse.ArgumentParser(description="找出 API 文档中没有测试用例的 API")
    parser.add_argument("--api_doc",  required=True, help="OpenAPI JSON 文件路径")
    parser.add_argument("--testcase", default=None,  help="已有测试用例 Excel 路径（可选）")
    parser.add_argument("--output",   default=None,  help="输出 JSON 文件路径（默认同 api_doc 目录）")
    parser.add_argument("--target_apis", default=None,
                        help="逗号分隔的目标 API（如 'POST /address/search,GET /carrier'），指定后直接返回这些 API")
    args = parser.parse_args()

    # 1. 解析 API 文档
    all_apis = parse_openapi(args.api_doc)

    # 2. 如果用户指定了目标 API，直接筛选
    if args.target_apis:
        targets = [t.strip().upper() for t in args.target_apis.split(",")]
        result_apis = [a for a in all_apis if a["api_key"].upper() in targets or
                       a["path"] in targets or
                       any(t in a["api_key"].upper() for t in targets)]
        print(f"🎯 用户指定目标 API，匹配到 {len(result_apis)} 个")
    else:
        # 3. 提取已有用例覆盖的 API
        covered = extract_covered_apis_from_excel(args.testcase)

        # 4. 找出未覆盖的 API
        if covered:
            result_apis = find_uncovered(all_apis, covered)
            print(f"\n🔍 未被覆盖的 API: {len(result_apis)} 个（共 {len(all_apis)} 个）")
        else:
            result_apis = all_apis
            print(f"\n📋 未提供已有用例，将对所有 {len(all_apis)} 个 API 设计用例")

    # 5. 输出结果
    output_path = args.output
    if not output_path:
        output_path = str(Path(args.api_doc).parent.parent / "api_list_to_design.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_apis, f, ensure_ascii=False, indent=2)

    # 6. 打印汇总表格
    print(f"\n{'='*70}")
    print(f"{'#':<4} {'方法':<8} {'路径':<40} {'摘要'}")
    print(f"{'-'*70}")
    for i, api in enumerate(result_apis, 1):
        print(f"{i:<4} {api['method']:<8} {api['path']:<40} {api['summary'][:20]}")
    print(f"{'='*70}")
    print(f"\n✅ 待设计用例的 API 列表已保存: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
