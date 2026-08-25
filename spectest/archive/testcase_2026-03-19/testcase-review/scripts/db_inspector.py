#!/usr/bin/env python3
"""
Step 3: 动态获取数据库表结构
根据测试用例中提到的表名，从配置的数据库中获取实际表结构
"""
import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
DB_CONFIG_PATH = SKILL_DIR / "db_config" / "db_config.json"


def load_db_config() -> dict:
    if not DB_CONFIG_PATH.exists():
        print(f"  [跳过] 数据库配置文件不存在: {DB_CONFIG_PATH}", file=sys.stderr)
        return {}
    with open(DB_CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_mysql_schema(config: dict, table_names: list[str]) -> dict[str, list]:
    """获取MySQL/Doris表结构"""
    try:
        import pymysql
    except ImportError:
        print("  [警告] 缺少 pymysql，跳过MySQL表结构获取", file=sys.stderr)
        return {}

    schemas = {}
    try:
        conn = pymysql.connect(
            host=config["host"],
            port=config.get("port", 3306),
            user=config["user"],
            password=config["password"],
            database=config.get("database", ""),
            charset=config.get("charset", "utf8mb4"),
            connect_timeout=5,
        )
        with conn.cursor() as cur:
            # 如果没有指定数据库，先获取当前数据库
            db = config.get("database", "")
            for table in table_names:
                try:
                    sql = f"DESCRIBE `{table}`" if db else f"SHOW COLUMNS FROM `{table}`"
                    cur.execute(sql)
                    rows = cur.fetchall()
                    schemas[table] = [
                        {"field": r[0], "type": r[1], "null": r[2], "key": r[3], "default": r[4], "extra": r[5]}
                        for r in rows
                    ]
                    print(f"  [OK] 获取表结构: {table} ({len(rows)} 列)")
                except Exception as e:
                    print(f"  [警告] 无法获取表 {table} 结构: {e}", file=sys.stderr)
        conn.close()
    except Exception as e:
        print(f"  [警告] 数据库连接失败: {e}", file=sys.stderr)

    return schemas


def get_postgres_schema(config: dict, table_names: list[str]) -> dict[str, list]:
    """获取PostgreSQL表结构"""
    try:
        import psycopg2
    except ImportError:
        print("  [警告] 缺少 psycopg2，跳过PostgreSQL表结构获取", file=sys.stderr)
        return {}

    schemas = {}
    try:
        conn = psycopg2.connect(
            host=config["host"],
            port=config.get("port", 5432),
            user=config["user"],
            password=config["password"],
            dbname=config.get("database", "postgres"),
            connect_timeout=5,
        )
        with conn.cursor() as cur:
            for table in table_names:
                try:
                    cur.execute(
                        """
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = %s
                        ORDER BY ordinal_position
                        """,
                        (table,),
                    )
                    rows = cur.fetchall()
                    schemas[table] = [
                        {"field": r[0], "type": r[1], "null": r[2], "default": str(r[3])}
                        for r in rows
                    ]
                    print(f"  [OK] 获取表结构: {table} ({len(rows)} 列)")
                except Exception as e:
                    print(f"  [警告] 无法获取表 {table} 结构: {e}", file=sys.stderr)
        conn.close()
    except Exception as e:
        print(f"  [警告] 数据库连接失败: {e}", file=sys.stderr)

    return schemas


def extract_table_names(testcases: list[dict]) -> set[str]:
    """从测试用例中提取所有涉及的表名"""
    tables = set()
    for tc in testcases:
        # 检查标准化字段
        normalized = tc.get("_normalized", {})
        if "tables" in normalized and normalized["tables"]:
            for t in normalized["tables"].replace("，", ",").replace("、", ",").split(","):
                t = t.strip()
                if t:
                    tables.add(t)
        # 也检查所有原始字段中可能包含表名的内容
        for col, val in tc.items():
            if col.startswith("_"):
                continue
            col_lower = col.lower()
            if any(kw in col_lower for kw in ["表", "table", "db"]):
                if val and val.strip():
                    for t in val.replace("，", ",").replace("、", ",").split(","):
                        t = t.strip()
                        if t and not any(c in t for c in " \t\n()（）"):
                            tables.add(t)
    return tables


def main():
    parser = argparse.ArgumentParser(description="获取相关数据库表结构")
    parser.add_argument("--testcase", default=None, help="解析后的测试用例JSON路径")
    parser.add_argument("--output", default=None, help="输出JSON路径")
    parser.add_argument("--tables", nargs="*", help="手动指定表名列表")
    args = parser.parse_args()

    print(f"\n=== Step 3: 获取数据库表结构 ===")

    config = load_db_config()
    if not config:
        print("  [跳过] 无数据库配置，跳过本步骤")
        sys.exit(0)

    # 获取需要查询的表名
    if args.tables:
        table_names = list(args.tables)
    elif args.testcase:
        tc_path = Path(args.testcase)
        if not tc_path.is_absolute():
            tc_path = SKILL_DIR / tc_path
        with open(tc_path, encoding="utf-8") as f:
            data = json.load(f)
        table_names = list(extract_table_names(data.get("testcases", [])))
    else:
        print("  请提供 --testcase 或 --tables 参数", file=sys.stderr)
        sys.exit(1)

    if not table_names:
        print("  [信息] 测试用例中未找到涉及的表名，跳过本步骤")
        sys.exit(0)

    print(f"  需要查询的表: {table_names}")

    db_type = config.get("type", "mysql").lower()
    if db_type in ("mysql", "doris"):
        schemas = get_mysql_schema(config, table_names)
    elif db_type in ("postgresql", "postgres"):
        schemas = get_postgres_schema(config, table_names)
    else:
        print(f"  [警告] 不支持的数据库类型: {db_type}", file=sys.stderr)
        schemas = {}

    output_path = Path(args.output) if args.output else SKILL_DIR / "testcase" / "db_schemas.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schemas, f, ensure_ascii=False, indent=2)

    print(f"  输出文件: {output_path}")
    print(f"[完成] 获取到 {len(schemas)} 个表结构")


if __name__ == "__main__":
    main()
