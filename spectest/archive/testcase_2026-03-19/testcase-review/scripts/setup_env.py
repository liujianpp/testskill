#!/usr/bin/env python3
"""
Step 1: 文档收集与目录初始化
将用户提供的文档复制到技能工作目录下对应子目录
"""
import argparse
import shutil
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent


def ensure_dirs():
    for d in ["project_info", "api_docs", "testcase", "output", "db_config"]:
        (SKILL_DIR / d).mkdir(exist_ok=True)


def copy_file(src: str, dest_dir: Path, label: str) -> Path | None:
    if not src:
        return None
    src_path = Path(src).expanduser().resolve()
    if not src_path.exists():
        print(f"  [警告] {label} 文件不存在: {src_path}", file=sys.stderr)
        return None
    dest_path = dest_dir / src_path.name
    shutil.copy2(src_path, dest_path)
    print(f"  [OK] {label}: {src_path.name} -> {dest_dir.relative_to(SKILL_DIR)}/")
    return dest_path


def main():
    parser = argparse.ArgumentParser(description="初始化测试用例评审环境")
    parser.add_argument("--testcase", required=True, help="测试用例文件路径 (Excel/CSV)")
    parser.add_argument("--requirement", help="需求文档路径（可选）")
    parser.add_argument("--business", help="业务逻辑文档路径（可选）")
    parser.add_argument("--api_doc", help="API接口文档路径（可选）")
    args = parser.parse_args()

    print("\n=== Step 1: 环境初始化 ===")
    ensure_dirs()

    # 复制各类文件
    tc_path = copy_file(args.testcase, SKILL_DIR / "testcase", "测试用例文件")
    if tc_path is None:
        print("错误：测试用例文件必须提供", file=sys.stderr)
        sys.exit(1)

    copy_file(args.requirement, SKILL_DIR / "project_info", "需求文档")
    copy_file(args.business, SKILL_DIR / "project_info", "业务逻辑文档")
    copy_file(args.api_doc, SKILL_DIR / "api_docs", "API接口文档")

    # 汇报已加载的资源
    print("\n已加载的上下文资源：")
    for subdir, label in [("project_info", "项目文档"), ("api_docs", "API文档"), ("testcase", "测试用例")]:
        files = list((SKILL_DIR / subdir).glob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith(".")]
        if files:
            print(f"  {label}: {', '.join(f.name for f in files)}")
        else:
            print(f"  {label}: (空)")

    db_cfg = SKILL_DIR / "db_config" / "db_config.json"
    if db_cfg.exists():
        print(f"  数据库配置: db_config.json (已配置)")
    else:
        print(f"  数据库配置: (未配置，跳过表结构获取)")

    print("\n[完成] 环境初始化成功")
    # 输出测试用例文件名供后续步骤使用
    print(f"TESTCASE_FILE={tc_path.name}")


if __name__ == "__main__":
    main()
