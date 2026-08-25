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

# 工作区固定子目录
SUBDIRS = [
    "project_info",     # 项目资料：需求文档、用户手册、业务逻辑
    "api_docs",         # API 接口文档（OpenAPI JSON）
    "testcase",         # 已有测试用例文档
    "db_info",          # 数据库连接配置
    "testcase_template",# 测试用例表头参考
    "output",           # 输出目录
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
        {"key": "project",         "name": "系统/项目",        "width": 12},
        {"key": "module",          "name": "模块",             "width": 15},
        {"key": "feature",         "name": "功能",             "width": 15},
        {"key": "test_item",       "name": "测试项",           "width": 25},
        {"key": "title",           "name": "用例标题",         "width": 30},
        {"key": "preconditions",   "name": "前置条件",         "width": 30},
        {"key": "db_tables",       "name": "涉及到数据库表",   "width": 20},
        {"key": "test_data",       "name": "测试数据",         "width": 35},
        {"key": "steps",           "name": "测试步骤",         "width": 55},
        {"key": "expected_result", "name": "预期结果",         "width": 55},
        {"key": "validation_sql",  "name": "验证SQL",          "width": 60},
        {"key": "actual_result",   "name": "实际结果",         "width": 20},
        {"key": "is_passed",       "name": "是否通过",         "width": 10},
        {"key": "estimated_hours", "name": "预计工时(h)",      "width": 12},
        {"key": "execute_date",    "name": "执行时间(年月日)", "width": 15},
        {"key": "test_progress",   "name": "测试进度(%)",      "width": 12},
        {"key": "case_type",       "name": "用例类型",         "width": 10},
        {"key": "priority",        "name": "用例优先级",       "width": 8},
        {"key": "is_regression",   "name": "是否回归用例",     "width": 12},
        {"key": "is_blocker",      "name": "是否阻塞上线",     "width": 12},
        {"key": "requirement_id",  "name": "关联需求ID",       "width": 15},
        {"key": "api_url",         "name": "API URL",          "width": 25},
        {"key": "bug_count",       "name": "BUG数",            "width": 8},
        {"key": "bug_unresolved",  "name": "BUG未解决数",      "width": 10},
        {"key": "case_version",    "name": "用例版本",         "width": 10},
    ]
}


def create_workspace() -> Path:
    """创建带时间戳的工作区目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ws = WORKSPACES_DIR / timestamp
    for subdir in SUBDIRS:
        (ws / subdir).mkdir(parents=True, exist_ok=True)
    return ws


def copy_file_to(src: str, dest_dir: Path, label: str) -> str:
    """复制文件到目标目录，返回目标路径"""
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(f"[{label}] 文件不存在: {src}")
    dest_path = dest_dir / src_path.name
    shutil.copy2(src_path, dest_path)
    return str(dest_path)


def copy_dir_to(src: str, dest_dir: Path, label: str) -> str:
    """复制目录内容到目标目录"""
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(f"[{label}] 目录不存在: {src}")
    for item in src_path.iterdir():
        if item.is_file():
            shutil.copy2(item, dest_dir / item.name)
    return str(dest_dir)


def main():
    parser = argparse.ArgumentParser(description="创建 design-api-cases 执行工作区")
    parser.add_argument("--api_doc",      required=True,  help="OpenAPI JSON 文件路径（必填）")
    parser.add_argument("--testcase",     default=None,   help="已有测试用例 Excel 路径（可选）")
    parser.add_argument("--project_info", default=None,   help="项目资料目录路径（可选）")
    parser.add_argument("--business_doc", default=None,   help="业务逻辑文档路径（可选）")
    parser.add_argument("--db_info",      default=None,   help="数据库配置 JSON 文件路径（可选）")
    args = parser.parse_args()

    # 1. 创建工作区
    ws = create_workspace()
    print(f"✅ 工作区已创建: {ws}")

    copied = {}

    # 2. 复制 API 文档
    try:
        p = copy_file_to(args.api_doc, ws / "api_docs", "API文档")
        copied["api_doc"] = p
        print(f"   📄 API文档 → {p}")
    except FileNotFoundError as e:
        print(f"   ❌ {e}")

    # 3. 复制已有测试用例
    if args.testcase:
        try:
            p = copy_file_to(args.testcase, ws / "testcase", "已有测试用例")
            copied["testcase"] = p
            print(f"   📊 已有用例 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # 4. 复制项目资料
    if args.project_info:
        try:
            p = copy_dir_to(args.project_info, ws / "project_info", "项目资料")
            copied["project_info"] = p
            count = len(list((ws / "project_info").iterdir()))
            print(f"   📁 项目资料 → {p}（{count} 个文件）")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # 5. 复制业务逻辑文档
    if args.business_doc:
        try:
            p = copy_file_to(args.business_doc, ws / "project_info", "业务逻辑文档")
            copied["business_doc"] = p
            print(f"   📝 业务文档 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}（已跳过）")

    # 6. 处理数据库配置（用户提供 or 使用默认）
    if args.db_info:
        try:
            p = copy_file_to(args.db_info, ws / "db_info", "数据库配置")
            copied["db_info"] = p
            print(f"   🗄️  数据库配置 → {p}")
        except FileNotFoundError as e:
            print(f"   ⚠️  {e}，将使用默认配置")
            _write_default_db_config(ws)
            copied["db_info"] = str(ws / "db_info" / "db_config.json")
            print(f"   🗄️  默认DB配置已写入: {copied['db_info']}")
    else:
        _write_default_db_config(ws)
        copied["db_info"] = str(ws / "db_info" / "db_config.json")
        print(f"   🗄️  默认DB配置已写入: {copied['db_info']}")

    # 7. 写入标准测试用例表头模板
    template_path = ws / "testcase_template" / "template_headers.json"
    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(TEMPLATE_HEADERS, f, ensure_ascii=False, indent=2)
    print(f"   📋 标准表头模板 → {template_path}")

    # 8. 写入 workspace_info.json（供后续脚本引用）
    info = {
        "workspace": str(ws),
        "created_at": datetime.now().isoformat(),
        "files": copied,
        "api_doc_filename": Path(args.api_doc).name if args.api_doc else None,
        "testcase_filename": Path(args.testcase).name if args.testcase else None,
    }
    info_path = ws / "workspace_info.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 工作区初始化完成！")
    print(f"   路径: {ws}")
    print(f"   信息: {info_path}")
    return str(ws)


def _write_default_db_config(ws: Path):
    db_config_path = ws / "db_info" / "db_config.json"
    config = _load_default_db_config()
    with open(db_config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
