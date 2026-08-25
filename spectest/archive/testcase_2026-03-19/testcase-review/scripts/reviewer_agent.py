#!/usr/bin/env python3
"""
Step 4: 并行 Sub-Agent 评审核心
将测试用例分成3批，并行启动3个Claude Sub-Agent进行评审
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


def load_context(skill_dir: Path) -> dict:
    """加载所有上下文文档"""
    context = {
        "project_docs": [],
        "api_docs": [],
        "review_criteria": "",
        "db_schemas": {},
    }

    # 加载评审标准
    criteria_path = skill_dir / "references" / "review_criteria.md"
    if criteria_path.exists():
        context["review_criteria"] = criteria_path.read_text(encoding="utf-8")

    # 加载项目文档
    for f in (skill_dir / "project_info").glob("*"):
        if f.is_file() and f.suffix.lower() in (".md", ".txt", ".pdf", ".docx"):
            try:
                if f.suffix.lower() in (".md", ".txt"):
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    context["project_docs"].append({"name": f.name, "content": content[:10000]})
            except Exception:
                pass

    # 加载API文档
    for f in (skill_dir / "api_docs").glob("*"):
        if f.is_file() and f.suffix.lower() in (".md", ".txt", ".json"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                context["api_docs"].append({"name": f.name, "content": content[:10000]})
            except Exception:
                pass

    # 加载数据库表结构
    db_schema_path = skill_dir / "testcase" / "db_schemas.json"
    if db_schema_path.exists():
        with open(db_schema_path, encoding="utf-8") as f:
            context["db_schemas"] = json.load(f)

    return context


def build_system_prompt(context: dict) -> str:
    parts = [
        "你是一位经验丰富的软件测试专家，专注于测试用例评审。请根据提供的业务文档、API文档、数据库表结构，"
        "对每条测试用例进行专业评审，给出具体、可操作的评审意见。\n"
        "评审要点：完整性、准确性、覆盖度、可执行性、可维护性。\n"
        "如果用例本身质量很高，评审意见留空字符串''。\n"
    ]

    if context["review_criteria"]:
        parts.append(f"\n## 评审标准\n{context['review_criteria'][:3000]}")

    if context["project_docs"]:
        parts.append("\n## 项目文档")
        for doc in context["project_docs"][:3]:
            parts.append(f"\n### {doc['name']}\n{doc['content'][:2000]}")

    if context["api_docs"]:
        parts.append("\n## API接口文档")
        for doc in context["api_docs"][:3]:
            parts.append(f"\n### {doc['name']}\n{doc['content'][:2000]}")

    if context["db_schemas"]:
        parts.append("\n## 数据库表结构")
        for table, columns in list(context["db_schemas"].items())[:10]:
            parts.append(f"\n### 表：{table}")
            for col in columns:
                parts.append(f"  - {col.get('field', '')} ({col.get('type', '')})")

    return "\n".join(parts)


def review_batch(batch: list[dict], batch_id: int, context: dict) -> list[dict]:
    """评审一批测试用例"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    system_prompt = build_system_prompt(context)

    results = []
    for tc in batch:
        # 构建用例描述
        normalized = tc.get("_normalized", {})
        tc_info = []
        for field, std_key in [
            ("系统/项目", "system"),
            ("模块", "module"),
            ("功能", "function"),
            ("测试项", "test_item"),
            ("用例标题", "title"),
            ("用例优先级", "priority"),
            ("用例类型", "case_type"),
            ("前置条件", "precondition"),
            ("涉及到数据库表", "tables"),
            ("API URL", "api_url"),
            ("测试步骤", "steps"),
            ("预期结果", "expected"),
            ("是否回归用例", "is_regression"),
            ("是否阻塞上线", "is_blocking"),
        ]:
            val = normalized.get(std_key, "")
            if not val:
                # 从原始列中找
                for col in tc.get("_raw_columns", []):
                    if field in col or std_key.lower() in col.lower():
                        val = tc.get(col, "")
                        break
            if val:
                tc_info.append(f"**{field}**: {val}")

        if not tc_info:
            # 直接使用所有非私有字段
            for k, v in tc.items():
                if not k.startswith("_") and v:
                    tc_info.append(f"**{k}**: {v}")

        tc_text = "\n".join(tc_info)

        user_msg = f"""请评审以下测试用例，给出简洁、专业的评审意见。
若用例质量优秀无需修改，请返回空字符串。
返回格式：仅返回评审意见文本，不要任何额外说明。

---
{tc_text}
---"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_msg}],
            )
            review_comment = response.content[0].text.strip()
            # 如果模型返回了"无"、"通过"、"优秀"等表示无问题的词，置为空
            if review_comment.lower() in ("", "无", "通过", "优秀", "无问题", "none", "n/a", "ok"):
                review_comment = ""
        except Exception as e:
            review_comment = f"[评审失败: {e}]"

        result = dict(tc)
        result["评审意见"] = review_comment
        results.append(result)
        print(f"  [Batch{batch_id}] 用例 {tc.get('_row_index', '?')+1} 评审完成")

    return results


def main():
    parser = argparse.ArgumentParser(description="并行评审测试用例")
    parser.add_argument("--testcase", required=True, help="解析后的测试用例JSON路径")
    parser.add_argument("--db_schema", default=None, help="数据库表结构JSON路径（可选）")
    parser.add_argument("--skill_dir", default=str(SKILL_DIR), help="技能工作目录")
    parser.add_argument("--workers", type=int, default=3, help="并行子agent数量（默认3）")
    parser.add_argument("--output", default=None, help="输出JSON路径")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)

    print(f"\n=== Step 4: 并行评审测试用例 ===")
    print(f"  并行Worker数: {args.workers}")

    # 加载测试用例
    tc_path = Path(args.testcase)
    if not tc_path.is_absolute():
        tc_path = skill_dir / tc_path
    with open(tc_path, encoding="utf-8") as f:
        data = json.load(f)

    testcases = data.get("testcases", [])
    print(f"  共 {len(testcases)} 条测试用例")

    # 加载上下文
    context = load_context(skill_dir)

    # 分批
    n = args.workers
    batch_size = math.ceil(len(testcases) / n)
    batches = [testcases[i:i + batch_size] for i in range(0, len(testcases), batch_size)]
    actual_workers = min(n, len(batches))
    print(f"  分成 {len(batches)} 批，每批约 {batch_size} 条，启动 {actual_workers} 个并行Worker")

    # 并行评审
    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=actual_workers) as executor:
        futures = {
            executor.submit(review_batch, batch, i + 1, context): i
            for i, batch in enumerate(batches)
        }
        # 按原始顺序收集结果
        batch_results = [None] * len(batches)
        for future in concurrent.futures.as_completed(futures):
            batch_idx = futures[future]
            try:
                batch_results[batch_idx] = future.result()
                print(f"  [完成] Batch {batch_idx + 1} 评审完成")
            except Exception as e:
                print(f"  [错误] Batch {batch_idx + 1} 失败: {e}", file=sys.stderr)
                batch_results[batch_idx] = batches[batch_idx]  # 原样保留

    for br in batch_results:
        if br:
            all_results.extend(br)

    # 统计
    total = len(all_results)
    reviewed = sum(1 for r in all_results if r.get("评审意见", "").strip())
    print(f"\n  评审统计: 总 {total} 条 | 有问题 {reviewed} 条 | 通过 {total - reviewed} 条")

    # 从 parsed_testcases.json 继承 sheet 信息，供 output_writer 使用
    sheet = data.get("sheet")

    # 输出
    output_path = Path(args.output) if args.output else skill_dir / "testcase" / "review_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total": total,
                "reviewed_at": datetime.now().isoformat(),
                "has_issues": reviewed,
                "passed": total - reviewed,
                "sheet": sheet,
                "results": all_results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"  输出文件: {output_path}")
    print(f"[完成] 评审完成")


if __name__ == "__main__":
    main()
