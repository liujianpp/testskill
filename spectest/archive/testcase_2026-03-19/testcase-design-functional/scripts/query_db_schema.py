#!/usr/bin/env python3
"""
query_db_schema.py
根据表名关键词查询 MySQL 数据库表结构，供子 Agent 在设计用例时使用。
"""

import argparse
import json
import re
from pathlib import Path

try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False


def load_db_config(config_path: str) -> dict:
    """加载数据库配置文件"""
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def get_mysql_tables(config: dict, database: str = None) -> list[str]:
    """列出所有表名"""
    target_db = database or config.get("database")
    conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=target_db,
        charset=config.get("charset", "utf8mb4"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES")
            rows = cur.fetchall()
            return [list(r.values())[0] for r in rows]
    finally:
        conn.close()


def get_mysql_table_struct(config: dict, table_name: str, database: str = None) -> list[dict]:
    """获取指定表的列结构"""
    target_db = database or config.get("database")
    conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=target_db,
        charset=config.get("charset", "utf8mb4"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COLUMN_NAME    as column_name,
                    COLUMN_TYPE    as column_type,
                    IS_NULLABLE    as is_nullable,
                    COLUMN_KEY     as column_key,
                    COLUMN_DEFAULT as column_default,
                    EXTRA          as extra,
                    COLUMN_COMMENT as column_comment
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (target_db, table_name))
            return cur.fetchall()
    finally:
        conn.close()


def list_databases(config: dict) -> list[str]:
    """列出可访问的所有数据库"""
    conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        charset=config.get("charset", "utf8mb4"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW DATABASES")
            rows = cur.fetchall()
            exclude = {"information_schema", "performance_schema", "mysql", "sys"}
            return [list(r.values())[0] for r in rows if list(r.values())[0] not in exclude]
    finally:
        conn.close()


def keyword_to_tablenames(keywords: list[str]) -> list[str]:
    """
    从关键词推断可能的表名变体（驼峰↔下划线 等）
    例: 'addressSuburb' → ['address_suburb', 'lsp_address_suburb', 'addressSuburb']
    """
    variants = set()
    for kw in keywords:
        kw = kw.strip()
        variants.add(kw)
        # 驼峰 → 下划线
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', kw).lower()
        variants.add(snake)
        variants.add(f"lsp_{snake}")
        # 去掉前缀
        parts = kw.split("_")
        if len(parts) > 1:
            variants.add("_".join(parts[1:]))
    return list(variants)


def search_tables_by_keywords(config: dict, keywords: list[str], database: str = None) -> dict[str, list]:
    """在数据库中查找匹配关键词的表，返回表结构信息"""
    if not HAS_PYMYSQL:
        return {"error": "未安装 pymysql（pip install pymysql）"}

    result = {}
    try:
        # 如果没有指定 database 且配置中也没有，则列出所有库并逐个搜索
        if not database and not config.get("database"):
            all_dbs = list_databases(config)
            schema_by_table = {}
            for db in all_dbs:
                try:
                    tables = get_mysql_tables(config, database=db)
                    for t in tables:
                        schema_by_table[t] = (db, t)
                except Exception:
                    pass
        else:
            target_db = database or config.get("database")
            tables = get_mysql_tables(config, database=target_db)
            schema_by_table = {t: (target_db, t) for t in tables}

        # 关键词变体匹配
        variants = keyword_to_tablenames(keywords)
        matched_tables = set()
        for variant in variants:
            for tname in schema_by_table:
                if variant.lower() in tname.lower() or tname.lower() in variant.lower():
                    matched_tables.add(tname)

        if not matched_tables:
            return {"warning": f"未找到匹配关键词 {keywords} 的表", "all_keywords_tried": variants}

        # 获取每个匹配表的列结构
        for tname in matched_tables:
            db_name, _ = schema_by_table[tname]
            try:
                cols = get_mysql_table_struct(config, tname, database=db_name)
                result[tname] = {
                    "database": db_name,
                    "columns": cols,
                    "column_count": len(cols),
                }
            except Exception as e:
                result[tname] = {"error": str(e)}

    except Exception as e:
        result["error"] = f"连接失败: {e}"

    return result


def format_schema(schema_result: dict) -> str:
    """格式化表结构，方便子 Agent 阅读"""
    lines = []
    for table, info in schema_result.items():
        if "error" in info and isinstance(info, dict) and set(info.keys()) == {"error"}:
            lines.append(f"\n❌ 表 {table}: {info['error']}")
            continue
        if "warning" in info:
            lines.append(f"\n⚠️  {info['warning']}")
            continue
        lines.append(f"\n📋 表：{info.get('database', '?')}.{table}（{info.get('column_count', 0)} 列）")
        lines.append("-" * 80)
        lines.append(f"  {'列名':<30} {'类型':<20} {'可空':<8} {'键':<8} {'注释'}")
        lines.append(f"  {'-'*30} {'-'*20} {'-'*8} {'-'*8} {'-'*20}")
        for col in info.get("columns", []):
            nullable = "NULL" if col.get("is_nullable") == "YES" else "NOT NULL"
            key = col.get("column_key", "")
            comment = col.get("column_comment", "")
            lines.append(
                f"  {col['column_name']:<30} {col['column_type']:<20} "
                f"{nullable:<8} {key:<8} {comment}"
            )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="根据关键词查询 MySQL 表结构")
    parser.add_argument("--db_config",       required=True, help="db_config.json 路径")
    parser.add_argument("--db_name",         default=None,  help="指定使用哪个数据库配置（配置名称）")
    parser.add_argument("--database",        default=None,  help="指定要搜索的数据库名（Schema）")
    parser.add_argument("--table_keywords",  required=True, help="逗号分隔的表名关键词，如 address,suburb")
    parser.add_argument("--output",          default=None,  help="输出 JSON 路径")
    args = parser.parse_args()

    if not HAS_PYMYSQL:
        print("❌ 请先安装 pymysql：pip install pymysql")
        return

    # 加载配置
    all_configs = load_db_config(args.db_config)
    config_name = args.db_name or list(all_configs.keys())[0]
    config = all_configs.get(config_name)
    if not config:
        print(f"❌ 未找到配置 '{config_name}'，可用配置: {list(all_configs.keys())}")
        return

    print(f"🔌 使用数据库配置: {config_name} ({config['host']}:{config['port']})")

    keywords = [k.strip() for k in args.table_keywords.split(",") if k.strip()]
    print(f"🔍 搜索关键词: {keywords}")

    schema_result = search_tables_by_keywords(config, keywords, database=args.database)

    print(format_schema(schema_result))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(schema_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✅ 表结构已保存: {args.output}")

    return schema_result


if __name__ == "__main__":
    main()
