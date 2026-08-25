#!/usr/bin/env python3
"""
parse_feature_list.py
解析 Markdown 格式功能清单，提取结构化功能点列表。

功能清单格式：
  # 模块名（一级标题）
  ## 功能点名（二级标题）
  功能描述(用户故事)：...
  设计数据库表：库名.表名,...
  技术栈：前端vue, 后端springboot
  关联接口：/api/xxx（可选）
  业务规则：...（可选）
"""

import argparse
import json
import re
from pathlib import Path


# ── 字段解析规则：字段名 → 目标 key，支持多种写法 ──────────────────
FIELD_PATTERNS = [
    # db_tables
    (r"^(?:设计数据库表|涉及数据库表|关联数据库表|数据库表|db_tables?)\s*[：:]\s*(.+)$",
     "db_tables_raw"),
    # description（用户故事/功能描述）
    (r"^(?:功能描述|用户故事|功能描述[\(（]用户故事[\)）]|描述)\s*[：:]\s*(.+)$",
     "description"),
    # tech_stack
    (r"^(?:技术栈|tech_?stack|技术|架构)\s*[：:]\s*(.+)$",
     "tech_stack"),
    # related_api
    (r"^(?:关联接口|关联API|接口|api)\s*[：:]\s*(.+)$",
     "related_api"),
    # business_rules
    (r"^(?:业务规则|业务逻辑|特殊规则|约束)\s*[：:]\s*(.+)$",
     "business_rules"),
    # priority_hint
    (r"^(?:优先级|priority)\s*[：:]\s*(.+)$",
     "priority_hint"),
]


def parse_db_tables(raw: str) -> list[str]:
    """解析数据库表字段，返回表名列表，支持 lsp_dev.lsp_address_suburb 格式"""
    tables = []
    for part in re.split(r"[,，;；\s]+", raw.strip()):
        part = part.strip()
        if part:
            tables.append(part)
    return tables


def extract_table_keywords(tables: list[str]) -> list[str]:
    """从 db.table 格式中提取表名关键词（去掉库名前缀）"""
    keywords = []
    for t in tables:
        if "." in t:
            keywords.append(t.split(".", 1)[-1])  # 取表名部分
        else:
            keywords.append(t)
    return list(set(keywords))


def parse_feature_list(md_path: str) -> list[dict]:
    """解析 Markdown 功能清单，返回结构化功能点列表"""
    content = Path(md_path).read_text(encoding="utf-8")
    lines = content.splitlines()

    features = []
    current_module = ""
    current_feature = ""
    current_fields: dict = {}
    current_extra_desc: list[str] = []
    in_feature = False

    def flush_feature():
        """保存当前功能点"""
        nonlocal current_fields, current_extra_desc
        if not current_feature or not current_module:
            return
        desc = current_fields.get("description", "")
        if current_extra_desc:
            desc = desc + "\n" + "\n".join(current_extra_desc) if desc else "\n".join(current_extra_desc)

        db_tables_raw = current_fields.get("db_tables_raw", "")
        db_tables = parse_db_tables(db_tables_raw) if db_tables_raw else []
        table_keywords = extract_table_keywords(db_tables)

        feat = {
            "module": current_module.strip(),
            "feature": current_feature.strip(),
            "description": desc.strip(),
            "db_tables": db_tables,
            "table_keywords": table_keywords,
            "tech_stack": current_fields.get("tech_stack", "").strip(),
            "related_api": current_fields.get("related_api", "").strip(),
            "business_rules": current_fields.get("business_rules", "").strip(),
            "priority_hint": current_fields.get("priority_hint", "").strip(),
            "feature_key": f"{current_module.strip()}/{current_feature.strip()}",
        }
        features.append(feat)
        current_fields = {}
        current_extra_desc = []

    for line in lines:
        # 一级标题 → 模块
        m1 = re.match(r"^#\s+(.+)$", line)
        if m1:
            flush_feature()
            current_module = m1.group(1).strip()
            current_feature = ""
            in_feature = False
            continue

        # 二级标题 → 功能点
        m2 = re.match(r"^##\s+(.+)$", line)
        if m2:
            flush_feature()
            current_feature = m2.group(1).strip()
            in_feature = True
            current_fields = {}
            current_extra_desc = []
            continue

        if not in_feature:
            continue

        # 三级及以上标题跳过（不支持三级嵌套）
        if re.match(r"^#{3,}", line):
            continue

        # 尝试匹配已知字段
        matched = False
        for pattern, key in FIELD_PATTERNS:
            m = re.match(pattern, line.strip(), re.IGNORECASE)
            if m:
                # 允许同一字段追加（多行描述）
                existing = current_fields.get(key, "")
                current_fields[key] = (existing + " " + m.group(1).strip()).strip()
                matched = True
                break

        if not matched and line.strip() and not line.startswith("#"):
            # 未命中字段的非空行，追加到 description
            current_extra_desc.append(line.strip())

    # 收尾：保存最后一个功能点
    flush_feature()

    return features


def print_feature_table(features: list[dict]):
    """打印功能点摘要表"""
    print(f"\n{'='*70}")
    print(f"{'#':<4} {'模块':<15} {'功能点':<20} {'相关表':<25} {'技术栈'}")
    print(f"{'-'*70}")
    for i, f in enumerate(features, 1):
        tables_str = ", ".join(f["db_tables"])[:24] if f["db_tables"] else "（无）"
        tech = f["tech_stack"][:15] if f["tech_stack"] else "（未标注）"
        print(f"{i:<4} {f['module']:<15} {f['feature']:<20} {tables_str:<25} {tech}")
    print(f"{'='*70}")
    print(f"共解析到 {len(features)} 个功能点\n")


def main():
    parser = argparse.ArgumentParser(description="解析 Markdown 功能清单")
    parser.add_argument("--feature_list", required=True, help="功能清单 .md 文件路径")
    parser.add_argument("--output",       default=None,  help="输出 JSON 文件路径")
    args = parser.parse_args()

    features = parse_feature_list(args.feature_list)

    if not features:
        print("⚠️  未解析到任何功能点，请检查 Markdown 格式是否符合规范（# 模块 / ## 功能点）")
        return

    print_feature_table(features)

    output_path = args.output
    if not output_path:
        output_path = str(Path(args.feature_list).parent / "feature_list.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(features, f, ensure_ascii=False, indent=2)

    print(f"✅ 功能点列表已保存: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
