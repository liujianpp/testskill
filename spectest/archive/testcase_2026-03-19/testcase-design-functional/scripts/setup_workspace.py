#!/usr/bin/env python3
"""
setup_workspace.py
创建带时间戳的工作区，复制用户提供的文件到对应目录。
"""

import argparse
import shutil
import json
import os
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
WORKSPACES_DIR = SKILL_DIR / "workspaces"

SUBDIRS = [
    "project_info",       # 功能清单、需求文档、业务逻辑
    "api_docs",           # API 接口文档（可选）
    "testcase",           # 已有测试用例
    "db_info",            # 数据库连接配置
    "testcase_template",  # 标准表头参考
    "output",             # 输出目录
]

# 默认 DB 配置：优先读取技能目录的 db_config.json，便于用户统一修改
_SKILL_DB_CONFIG_FILE = SKILL_DIR / "db_config.json"

def _load_default_db_config() -> dict:
    if _SKILL_DB_CONFIG_FILE.exists():
        with open(_SKILL_DB_CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    # 兜底硬编码（db_config.json 不存在时使用）
    return {
        "测试mysql": {
            "type": "mysql",
            "host": "192.168.1.31",
            "port": 13306,
            "user": "ethan",
            "password": "ethan263*2",
            "database": None,
            "charset": "utf8mb4",
            "description": "测试 MySQL，可访问多个数据库"
        }
    }

TEMPLATE_HEADERS = {
    "columns": [
        {"key": "case_id",          "name": "用例编号",   "width": 12},
        {"key": "module",           "name": "所属模块",   "width": 15},
        {"key": "feature",          "name": "功能点",     "width": 15},
        {"key": "title",            "name": "用例标题",   "width": 30},
        {"key": "description",      "name": "用例描述",   "width": 40},
        {"key": "preconditions",    "name": "前置条件",   "width": 30},
        {"key": "steps",            "name": "测试步骤",   "width": 55},
        {"key": "test_data",        "name": "测试数据",   "width": 35},
        {"key": "expected_result",  "name": "预期结果",   "width": 55},
        {"key": "validation_sql",   "name": "验证SQL",    "width": 60},
        {"key": "case_type",        "name": "用例类型",   "width": 10},
        {"key": "priority",         "name": "优先级",     "width": 8},
        {"key": "design_method",    "name": "设计方法",   "width": 18},
        {"key": "tech_stack",       "name": "技术栈",     "width": 20},
        {"key": "requirement_ref",  "name": "关联需求",   "width": 15},
        {"key": "status",           "name": "状态",       "width": 8},
        {"key": "notes",            "name": "备注",       "width": 30},
    ]
}


def create_workspace() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ws = WORKSPACES_DIR / timestamp
    for subdir in SUBDIRS:
        (ws / subdir).mkdir(parents=True, exist_ok=True)
    return ws


def copy_file(src: str, dest_dir: Path, label: str) -> str:
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(f"[{label}] 文件不存在: {src}")
    dest = dest_dir / src_path.name
    shutil.copy2(src_path, dest)
    return str(dest)


def copy_dir_contents(src: str, dest_dir: Path, label: str) -> str:
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(f"[{label}] 目录不存在: {src}")
    copied = 0
    for item in src_path.iterdir():
        if item.is_file():
            shutil.copy2(item, dest_dir / item.name)
            copied += 1
    return f"{dest_dir}（{copied} 个文件）"


def main():
    parser = argparse.ArgumentParser(description="创建 design-functional-cases 工作区")
    parser.add_argument("--feature_list",  required=True, help="功能清单 Markdown 文件路径（必填）")
    parser.add_argument("--requirement",   default=None,  help="需求文档路径（可选）")
    parser.add_argument("--api_doc",       default=None,  help="OpenAPI JSON 文件路径（可选）")
    parser.add_argument("--testcase",      default=None,  help="已有测试用例 Excel 路径（可选）")
    parser.add_argument("--project_info",  default=None,  help="项目资料目录路径（可选）")
    parser.add_argument("--business_doc",  default=None,  help="业务逻辑文档路径（可选）")
    parser.add_argument("--db_info",       default=None,  help="数据库配置 JSON 文件路径（可选）")
    args = parser.parse_args()

    ws = create_workspace()
    print(f"✅ 工作区已创建: {ws}")

    copied = {}

    # 功能清单 → project_info/
    try:
        p = copy_file(args.feature_list, ws / "project_info", "功能清单")
        copied["feature_list"] = p
        copied["feature_list_filename"] = Path(args.feature_list).name
        print(f"   📋 功能清单 → {p}")
    except FileNotFoundError as e:
        print(f"   ❌ {e}")

    # 需求文档 → project_info/
    if args.requirement:
        try:
            p = copy_file(args.requirement, ws / "project_info", "需求文档")
            copied["requirement"] = p
            print(f"   📄 需求文档 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # API 文档 → api_docs/
    if args.api_doc:
        try:
            p = copy_file(args.api_doc, ws / "api_docs", "API文档")
            copied["api_doc"] = p
            print(f"   🔌 API文档 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # 已有测试用例 → testcase/
    if args.testcase:
        try:
            p = copy_file(args.testcase, ws / "testcase", "已有测试用例")
            copied["testcase"] = p
            copied["testcase_filename"] = Path(args.testcase).name
            print(f"   📊 已有用例 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # 项目资料目录 → project_info/
    if args.project_info:
        try:
            desc = copy_dir_contents(args.project_info, ws / "project_info", "项目资料")
            copied["project_info"] = str(ws / "project_info")
            print(f"   📁 项目资料 → {desc}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # 业务逻辑文档 → project_info/
    if args.business_doc:
        try:
            p = copy_file(args.business_doc, ws / "project_info", "业务逻辑文档")
            copied["business_doc"] = p
            print(f"   📝 业务文档 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # 数据库配置
    if args.db_info:
        try:
            p = copy_file(args.db_info, ws / "db_info", "数据库配置")
            copied["db_info"] = p
            print(f"   🗄️  数据库配置 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}，将使用默认配置")
            _write_default_db(ws)
            copied["db_info"] = str(ws / "db_info" / "db_config.json")
    else:
        _write_default_db(ws)
        copied["db_info"] = str(ws / "db_info" / "db_config.json")
        print(f"   🗄️  默认DB配置 → {copied['db_info']}")

    # 标准表头模板
    tp = ws / "testcase_template" / "template_headers.json"
    with open(tp, "w", encoding="utf-8") as f:
        json.dump(TEMPLATE_HEADERS, f, ensure_ascii=False, indent=2)
    print(f"   📋 标准表头模板 → {tp}")

    # workspace_info.json
    info = {
        "workspace": str(ws),
        "created_at": datetime.now().isoformat(),
        "skill": "design-functional-cases",
        "files": copied,
    }
    info_path = ws / "workspace_info.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 工作区初始化完成！路径: {ws}")
    print(f"   工作区信息: {info_path}")
    return str(ws)


def _write_default_db(ws: Path):
    db_path = ws / "db_info" / "db_config.json"
    config = _load_default_db_config()
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
