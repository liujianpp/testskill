#!/usr/bin/env python3
"""
一键启动：测试用例评审 / 评审+完善 完整流程

Usage（仅评审）:
  python scripts/start.py --testcase <路径>

Usage（评审+完善）:
  python scripts/start.py --testcase <路径> --fix
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"


def run(cmd: list[str], step: str) -> int:
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=str(SKILL_DIR))
    if result.returncode != 0:
        print(f"\n[错误] {step} 失败，退出码: {result.returncode}", file=sys.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="测试用例评审一键启动",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 仅评审，输出有评审意见的文档
  python scripts/start.py --testcase ~/Downloads/testcases.xlsx

  # 评审+完善，输出评审文档 + 完善文档（共2份）
  python scripts/start.py --testcase ~/Downloads/testcases.xlsx --fix
        """,
    )
    parser.add_argument("--testcase", required=True, help="测试用例文件路径 (.xlsx/.xls/.csv)")
    parser.add_argument("--requirement", default=None, help="需求文档路径（可选）")
    parser.add_argument("--business", default=None, help="业务逻辑文档路径（可选）")
    parser.add_argument("--api_doc", default=None, help="API接口文档路径（可选）")
    parser.add_argument("--workers", type=int, default=3, help="并行Worker数（默认3）")
    parser.add_argument("--fix", action="store_true", help="评审完成后自动完善有问题的测试用例，输出2份文档")
    parser.add_argument("--sheet", default=None, help="指定 Excel Sheet 名称（默认自动识别）")
    args = parser.parse_args()

    testcase_path = Path(args.testcase).expanduser().resolve()

    print("\n" + "="*60)
    mode = "评审 + 完善" if args.fix else "仅评审"
    print(f"  测试用例评审系统 - 启动（{mode}模式）")
    print("="*60)
    print(f"  测试用例: {testcase_path}")
    if args.requirement:
        print(f"  需求文档: {args.requirement}")
    if args.business:
        print(f"  业务文档: {args.business}")
    if args.api_doc:
        print(f"  API文档:  {args.api_doc}")
    print(f"  并行数量: {args.workers} 个Worker")

    # Step 1: 初始化环境
    setup_cmd = [sys.executable, str(SCRIPTS_DIR / "setup_env.py"), "--testcase", str(testcase_path)]
    if args.requirement:
        setup_cmd += ["--requirement", args.requirement]
    if args.business:
        setup_cmd += ["--business", args.business]
    if args.api_doc:
        setup_cmd += ["--api_doc", args.api_doc]

    if run(setup_cmd, "Step 1: 环境初始化") != 0:
        sys.exit(1)

    # 获取复制后的文件名
    tc_filename = testcase_path.name
    tc_in_dir = SKILL_DIR / "testcase" / tc_filename

    # Step 2: 解析测试用例
    reader_cmd = [sys.executable, str(SCRIPTS_DIR / "reader.py"), "--input", str(tc_in_dir)]
    if args.sheet:
        reader_cmd += ["--sheet", args.sheet]
    if run(reader_cmd, "Step 2: 解析测试用例") != 0:
        sys.exit(1)

    # Step 3: 获取数据库表结构（可选）
    db_config = SKILL_DIR / "db_config" / "db_config.json"
    if db_config.exists():
        run(
            [sys.executable, str(SCRIPTS_DIR / "db_inspector.py"),
             "--testcase", str(SKILL_DIR / "testcase" / "parsed_testcases.json")],
            "Step 3: 获取数据库表结构",
        )
    else:
        print("\n[跳过] Step 3: 未配置数据库，跳过表结构获取")

    # Step 4: 并行评审
    review_cmd = [
        sys.executable, str(SCRIPTS_DIR / "reviewer_agent.py"),
        "--testcase", str(SKILL_DIR / "testcase" / "parsed_testcases.json"),
        "--skill_dir", str(SKILL_DIR),
        "--workers", str(args.workers),
    ]
    db_schema = SKILL_DIR / "testcase" / "db_schemas.json"
    if db_schema.exists():
        review_cmd += ["--db_schema", str(db_schema)]

    if run(review_cmd, "Step 4: 并行评审") != 0:
        sys.exit(1)

    # Step 5: 生成评审报告（含评审意见列）
    if run(
        [
            sys.executable, str(SCRIPTS_DIR / "output_writer.py"),
            "--original", str(tc_in_dir),
            "--review", str(SKILL_DIR / "testcase" / "review_results.json"),
            "--output", str(SKILL_DIR / "output"),
        ],
        "Step 5: 生成评审报告",
    ) != 0:
        sys.exit(1)

    if args.fix:
        # Step 4b: 并行完善有问题的用例
        if run(
            [
                sys.executable, str(SCRIPTS_DIR / "fixer_agent.py"),
                "--review", str(SKILL_DIR / "testcase" / "review_results.json"),
                "--parsed", str(SKILL_DIR / "testcase" / "parsed_testcases.json"),
                "--skill_dir", str(SKILL_DIR),
                "--workers", str(args.workers),
            ],
            "Step 4b: 并行完善测试用例",
        ) != 0:
            sys.exit(1)

        # Step 5b: 生成完善后的文档
        if run(
            [
                sys.executable, str(SCRIPTS_DIR / "fixed_writer.py"),
                "--original", str(tc_in_dir),
                "--fixed", str(SKILL_DIR / "testcase" / "fixed_testcases.json"),
                "--output", str(SKILL_DIR / "output"),
            ],
            "Step 5b: 生成完善后的用例文档",
        ) != 0:
            sys.exit(1)

        print("\n" + "="*60)
        print("  评审+完善完成！output/ 目录包含 2 份文档：")
        print("  ├── *_reviewed_*.xlsx  — 带评审意见（红/绿高亮）")
        print("  └── *_fixed_*.xlsx    — 完善后用例（黄色高亮改动处）")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("  评审完成！结果文件位于: output/")
        print("="*60)


if __name__ == "__main__":
    main()
