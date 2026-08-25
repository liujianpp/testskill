#!/usr/bin/env python3
"""
Step 4b: 并行用例完善 Agent
读取评审结果，对有评审意见的用例调用 Claude 进行内容完善，
输出 fixed_testcases.json（保留原始结构，仅更新有问题的字段）
"""
import argparse
import json
import os
import sys
import math
import concurrent.futures
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent

try:
    import anthropic
except ImportError:
    print("缺少依赖: pip install anthropic", file=sys.stderr)
    sys.exit(1)


import re


def _extract_json(raw: str) -> dict:
    """从模型输出中提取 JSON 对象，兼容 markdown 代码块和含真实换行的字符串"""
    # 去除 markdown 代码块
    if "```" in raw:
        parts = raw.split("```")
        # 取第一个代码块内容（位于偶数索引的元素）
        for i, part in enumerate(parts):
            if i % 2 == 1:
                raw = part.lstrip("json").strip()
                break

    raw = raw.strip()

    # 先直接尝试
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        pass

    # 提取 {...} 范围
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        return {}

    candidate = match.group(0)

    # 尝试修复：将字符串值中的真实换行替换为 \n
    # 策略：在 JSON 字符串内（"..."之间）将换行转义
    def escape_newlines_in_strings(s: str) -> str:
        result = []
        in_string = False
        escape_next = False
        for ch in s:
            if escape_next:
                result.append(ch)
                escape_next = False
            elif ch == '\\':
                result.append(ch)
                escape_next = True
            elif ch == '"':
                in_string = not in_string
                result.append(ch)
            elif in_string and ch == '\n':
                result.append('\\n')
            elif in_string and ch == '\r':
                result.append('\\r')
            else:
                result.append(ch)
        return ''.join(result)

    try:
        fixed = escape_newlines_in_strings(candidate)
        obj = json.loads(fixed)
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


# 标准字段名 → 中文标签（用于 prompt 显示）
STD_FIELD_LABELS = {
    "system":           "系统/项目",
    "module":           "模块",
    "function":         "功能",
    "test_item":        "测试项",
    "title":            "用例标题",
    "priority":         "用例优先级",
    "case_type":        "用例类型",
    "precondition":     "前置条件",
    "tables":           "涉及到数据库表",
    "test_data":        "测试数据",
    "api_url":          "API URL",
    "steps":            "测试步骤",
    "expected":         "预期结果",
    "validation_sql":   "验证SQL",
    "is_regression":    "是否回归用例",
    "is_blocking":      "是否阻塞上线",
}

# 可被完善的字段（不包括只读的 id/status/统计类字段）
FIXABLE_FIELDS = {"title", "precondition", "test_data", "steps", "expected", "validation_sql", "case_type", "priority"}


def build_fix_prompt(tc: dict, review_comment: str) -> str:
    """构建完善用例的 prompt"""
    normalized = tc.get("_normalized", {})
    raw_cols = tc.get("_raw_columns", [])

    lines = []
    for std_key, label in STD_FIELD_LABELS.items():
        val = normalized.get(std_key, "")
        if not val:
            # 从原始列中回退查找
            for col in raw_cols:
                if label in col or std_key.lower() in col.lower():
                    val = tc.get(col, "")
                    break
        if val:
            lines.append(f"**{label}**: {val}")

    if not lines:
        for k, v in tc.items():
            if not k.startswith("_") and k != "评审意见" and v:
                lines.append(f"**{k}**: {v}")

    tc_text = "\n".join(lines)

    fixable_list = "、".join(
        STD_FIELD_LABELS[f] for f in FIXABLE_FIELDS if f in STD_FIELD_LABELS
    )

    return f"""你是一位资深测试工程师，请根据评审意见对以下测试用例进行完善和补充。

## 当前测试用例
{tc_text}

## 评审意见
{review_comment}

## 要求
- 根据评审意见，完善需要改进的字段：{fixable_list}
- 只修改有问题的字段，无需改动的字段不要出现在返回结果中
- 步骤要编号清晰（1. 2. 3.），预期结果要具体可验证
- 返回严格的 JSON 对象，key 使用以下标准英文字段名：
  title, precondition, test_data, steps, expected, validation_sql, case_type, priority
- 只返回 JSON，不要任何说明文字

重要：JSON 字符串中的换行必须用 \\n 表示，不能直接换行。

示例返回格式：
{{"steps": "1. 登录系统\\n2. 进入XXX页面\\n3. 执行操作", "expected": "1. 页面显示XXX\\n2. 数据库记录更新", "validation_sql": "SELECT COUNT(*) FROM xxx WHERE id=1;"}}"""


def fix_batch(batch: list[dict], batch_id: int, col_map: dict) -> list[dict]:
    """完善一批有问题的测试用例"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    results = []

    for tc in batch:
        review_comment = tc.get("评审意见", "").strip()

        if not review_comment:
            # 无评审意见，原样保留，不需要完善
            tc["_improvements"] = {}
            results.append(tc)
            continue

        user_msg = build_fix_prompt(tc, review_comment)

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw = response.content[0].text.strip()
            improvements = _extract_json(raw)
        except Exception as e:
            print(f"  [Batch{batch_id}] 用例 {tc.get('_row_index', '?')+1} 完善失败: {e}")
            improvements = {}

        tc["_improvements"] = improvements

        # 将改进内容写回原始列（通过 col_map 反向映射）
        reverse_map = {v: k for k, v in col_map.items()}  # orig_col → std_field（反转）
        std_to_orig = {v: k for k, v in {v2: k2 for k2, v2 in col_map.items()}.items()}
        # 直接用 col_map: std_field → orig_col
        for std_field, new_val in improvements.items():
            orig_col = col_map.get(std_field)
            if orig_col and orig_col in tc:
                tc[orig_col] = new_val
            elif std_field in tc:
                tc[std_field] = new_val

        improved_count = len([v for v in improvements.values() if v])
        print(f"  [Batch{batch_id}] 用例 {tc.get('_row_index', '?')+1} 完善完成（改进 {improved_count} 个字段）")
        results.append(tc)

    return results


def main():
    parser = argparse.ArgumentParser(description="并行完善测试用例")
    parser.add_argument("--review", required=True, help="评审结果JSON路径（review_results.json）")
    parser.add_argument("--parsed", default=None, help="解析结果JSON路径（parsed_testcases.json，用于获取col_map）")
    parser.add_argument("--skill_dir", default=str(SKILL_DIR), help="技能工作目录")
    parser.add_argument("--workers", type=int, default=3, help="并行Worker数（默认3）")
    parser.add_argument("--output", default=None, help="输出JSON路径")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)

    print(f"\n=== Step 4b: 并行完善测试用例 ===")
    print(f"  并行Worker数: {args.workers}")

    # 加载评审结果
    review_path = Path(args.review)
    if not review_path.is_absolute():
        review_path = skill_dir / review_path
    with open(review_path, encoding="utf-8") as f:
        review_data = json.load(f)

    results = review_data.get("results", [])
    sheet = review_data.get("sheet")

    # 加载 col_map（优先从 parsed_testcases.json 取）
    parsed_path = Path(args.parsed) if args.parsed else skill_dir / "testcase" / "parsed_testcases.json"
    if not parsed_path.is_absolute():
        parsed_path = skill_dir / parsed_path

    col_map = {}
    if parsed_path.exists():
        with open(parsed_path, encoding="utf-8") as f:
            parsed_data = json.load(f)
        col_map = parsed_data.get("col_map", {})
        print(f"  字段映射: {col_map}")
    else:
        print("  [警告] 未找到 parsed_testcases.json，字段反映射可能不完整")

    has_issues = [tc for tc in results if tc.get("评审意见", "").strip()]
    no_issues = [tc for tc in results if not tc.get("评审意见", "").strip()]
    print(f"  共 {len(results)} 条 | 需完善: {len(has_issues)} 条 | 无需修改: {len(no_issues)} 条")

    # 只对有问题的用例分批处理
    if has_issues:
        n = args.workers
        batch_size = math.ceil(len(has_issues) / n)
        batches = [has_issues[i:i + batch_size] for i in range(0, len(has_issues), batch_size)]
        actual_workers = min(n, len(batches))
        print(f"  分成 {len(batches)} 批，每批约 {batch_size} 条，启动 {actual_workers} 个并行Worker")

        fixed_issue_cases = [None] * len(batches)
        with concurrent.futures.ThreadPoolExecutor(max_workers=actual_workers) as executor:
            futures = {
                executor.submit(fix_batch, batch, i + 1, col_map): i
                for i, batch in enumerate(batches)
            }
            for future in concurrent.futures.as_completed(futures):
                batch_idx = futures[future]
                try:
                    fixed_issue_cases[batch_idx] = future.result()
                    print(f"  [完成] Batch {batch_idx + 1} 完善完成")
                except Exception as e:
                    print(f"  [错误] Batch {batch_idx + 1} 失败: {e}", file=sys.stderr)
                    fixed_issue_cases[batch_idx] = batches[batch_idx]

        # 展平
        fixed_issues_flat = []
        for br in fixed_issue_cases:
            if br:
                fixed_issues_flat.extend(br)
    else:
        fixed_issues_flat = []

    # 无问题用例也补上 _improvements 字段
    for tc in no_issues:
        tc["_improvements"] = {}

    # 按原始顺序合并
    all_fixed = fixed_issues_flat + no_issues
    all_fixed.sort(key=lambda x: x.get("_row_index", 0))

    improved_count = sum(1 for tc in all_fixed if tc.get("_improvements"))
    print(f"\n  完善统计: 总 {len(all_fixed)} 条 | 已完善 {improved_count} 条 | 未改动 {len(all_fixed) - improved_count} 条")

    # 输出
    output_path = Path(args.output) if args.output else skill_dir / "testcase" / "fixed_testcases.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total": len(all_fixed),
                "fixed_at": datetime.now().isoformat(),
                "improved": improved_count,
                "sheet": sheet,
                "results": all_fixed,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"  输出文件: {output_path}")
    print(f"[完成] 用例完善完成")


if __name__ == "__main__":
    main()
