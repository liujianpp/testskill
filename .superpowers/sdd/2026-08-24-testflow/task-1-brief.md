# Task 1 Brief: 转换器 convert_25col_to_ui_xlsx.py

（摘自 e:/AI/skills/docs/superpowers/plans/2026-08-24-testflow.md 的 Task 1 全文，逐字为准）

## Global Constraints（对本任务生效的摘录）

- 工作区 `e:/AI/skills/` **不是 git 仓库**：**无 commit 步骤**，以「验证产物存在/测试通过」收尾
- 平台 win32 + bash：路径用正斜杠；Python 命令用 `python`（不是 `python3`/`uv run`）
- 依赖：`python -m pip install openpyxl pytest`（若缺失先安装）
- 25 列标准表头（**逐字使用**）：`系统/项目, 模块, 功能, 测试项/测试点, 用例标题, 前置条件, 涉及相关数据库表, 测试数据准备, 测试步骤, 预期结果, 验证SQL, 实际结果, 是否通过, 预估工时, 执行时间, 测试进度, 用例类型, 用例优先级, 是否回归用例, 是否阻塞上线, 关联需求ID, API URL, BUG数, BUG未解决数, 用例版本`
- 25 列 Excel 数据 Sheet 名：`测试用例`（首行表头）
- runner 8 列输出表头（**逐字使用**）：`用例编号, 用例名称, 功能模块, 优先级, 前置条件, 测试步骤, 测试数据, 预期结果`
- 中文为主体语言；脚本文件名、CLI 参数用英文

## Files

- Create: `e:/AI/skills/testflow/scripts/convert_25col_to_ui_xlsx.py`
- Test: `e:/AI/skills/testflow/scripts/tests/test_convert_25col_to_ui_xlsx.py`

## Interfaces

- Consumes: 25 列 `*_testcases.xlsx`（Sheet `测试用例`）
- Produces（Task 3 的 SKILL.md 引用此 CLI，签名不得变）:
  - CLI: `python convert_25col_to_ui_xlsx.py -i <input.xlsx> -o <output.xlsx> [--sheet 测试用例] [--types 正向,边界]`
  - Python API: `convert(input_path: str, output_path: str, sheet_name: str = "测试用例", include_types: set[str] | None = None) -> dict`，返回 `{"total": int, "exported": int, "skipped_api": int, "skipped_type": int, "skipped_dup": int, "skipped_empty": int}`
  - 常量: `RUNNER_HEADERS: list[str]`（8 列输出表头）

## Steps

### Step 1: 确保依赖可用

Run: `python -c "import openpyxl, pytest; print('ok')"`
Expected: 输出 `ok`。若报 ModuleNotFoundError，先运行 `python -m pip install openpyxl pytest`

### Step 2: 写失败的单测

创建 `e:/AI/skills/testflow/scripts/tests/test_convert_25col_to_ui_xlsx.py`，完整代码如下（逐字使用）：

```python
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from convert_25col_to_ui_xlsx import RUNNER_HEADERS, convert

HEADERS_25 = [
    "系统/项目", "模块", "功能", "测试项/测试点", "用例标题",
    "前置条件", "涉及相关数据库表", "测试数据准备", "测试步骤", "预期结果",
    "验证SQL", "实际结果", "是否通过", "预估工时", "执行时间",
    "测试进度", "用例类型", "用例优先级", "是否回归用例", "是否阻塞上线",
    "关联需求ID", "API URL", "BUG数", "BUG未解决数", "用例版本",
]


def build_25col(path, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "测试用例"
    ws.append(HEADERS_25)
    for r in rows:
        ws.append(r)
    wb.save(path)


def row_for(**kw):
    """构造一行 25 列数据，未给字段的列留空。"""
    base = {h: "" for h in HEADERS_25}
    base.update(kw)
    return [base[h] for h in HEADERS_25]


def load_out(path):
    wb = load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    return rows[0], rows[1:]


def test_standard_mapping(tmp_path):
    src = tmp_path / "in.xlsx"
    out = tmp_path / "out.xlsx"
    build_25col(src, [
        row_for(**{
            "模块": "登录", "功能": "账号登录", "测试项/测试点": "TC-001",
            "用例标题": "正确账号密码登录", "用例优先级": "P0",
            "前置条件": "账号已注册", "测试步骤": "1.打开登录页\n2.输入账号密码\n3.点击登录",
            "测试数据准备": "user=admin", "预期结果": "登录成功跳转首页",
            "用例类型": "正向",
        }),
    ])
    stats = convert(str(src), str(out))
    headers, rows = load_out(out)
    assert headers == RUNNER_HEADERS == [
        "用例编号", "用例名称", "功能模块", "优先级", "前置条件",
        "测试步骤", "测试数据", "预期结果",
    ]
    assert len(rows) == 1
    r = rows[0]
    assert r[0] == "TC-001"           # 用例编号 ← 测试项/测试点
    assert r[1] == "正确账号密码登录"   # 用例名称 ← 用例标题
    assert r[2] == "登录"              # 功能模块 ← 模块
    assert r[3] == "P0"               # 优先级 ← 用例优先级
    assert r[4] == "账号已注册"
    assert r[5] == "1.打开登录页\n2.输入账号密码\n3.点击登录"  # 换行保留
    assert r[6] == "user=admin"       # 测试数据 ← 测试数据准备
    assert r[7] == "登录成功跳转首页"
    assert stats == {"total": 1, "exported": 1, "skipped_api": 0,
                     "skipped_type": 0, "skipped_dup": 0, "skipped_empty": 0}


def test_api_url_rows_excluded(tmp_path):
    src, out = tmp_path / "in.xlsx", tmp_path / "out.xlsx"
    build_25col(src, [
        row_for(**{"测试项/测试点": "TC-A", "用例标题": "UI用例"}),
        row_for(**{"测试项/测试点": "TC-B", "用例标题": "API用例", "API URL": "/api/login"}),
    ])
    stats = convert(str(src), str(out))
    _, rows = load_out(out)
    assert [r[0] for r in rows] == ["TC-A"]
    assert stats["skipped_api"] == 1
    assert stats["exported"] == 1


def test_fallback_id_generation(tmp_path):
    src, out = tmp_path / "in.xlsx", tmp_path / "out.xlsx"
    build_25col(src, [
        row_for(**{"模块": "登录", "功能": "账号登录", "用例标题": "无编号用例"}),
    ])
    convert(str(src), str(out))
    _, rows = load_out(out)
    assert rows[0][0] == "登录-账号登录-1"   # 模块-功能-行号


def test_dedup_keeps_first(tmp_path):
    src, out = tmp_path / "in.xlsx", tmp_path / "out.xlsx"
    build_25col(src, [
        row_for(**{"测试项/测试点": "TC-DUP", "用例标题": "第一条"}),
        row_for(**{"测试项/测试点": "TC-DUP", "用例标题": "第二条"}),
    ])
    stats = convert(str(src), str(out))
    _, rows = load_out(out)
    assert len(rows) == 1
    assert rows[0][1] == "第一条"
    assert stats["skipped_dup"] == 1


def test_types_filter_on_coverage_dim(tmp_path):
    src, out = tmp_path / "in.xlsx", tmp_path / "out.xlsx"
    build_25col(src, [
        row_for(**{"测试项/测试点": "TC-1", "用例标题": "正向", "用例类型": "正向"}),
        row_for(**{"测试项/测试点": "TC-2", "用例标题": "安全", "用例类型": "安全"}),
    ])
    stats = convert(str(src), str(out), include_types={"正向"})
    _, rows = load_out(out)
    assert [r[0] for r in rows] == ["TC-1"]
    assert stats["skipped_type"] == 1


def test_missing_source_column_no_crash(tmp_path):
    """缺「测试数据准备」列时该输出列留空，不报错。"""
    src, out = tmp_path / "in.xlsx", tmp_path / "out.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "测试用例"
    heads = [h for h in HEADERS_25 if h != "测试数据准备"]
    ws.append(heads)
    base = {h: "" for h in heads}
    base.update({"测试项/测试点": "TC-X", "用例标题": "缺列用例"})
    ws.append([base[h] for h in heads])
    wb.save(src)
    convert(str(src), str(out))
    _, rows = load_out(out)
    assert rows[0][0] == "TC-X"
    assert rows[0][6] == ""


def test_empty_rows_skipped(tmp_path):
    src, out = tmp_path / "in.xlsx", tmp_path / "out.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "测试用例"
    ws.append(HEADERS_25)
    ws.append([""] * 25)
    ws.append(row_for(**{"测试项/测试点": "TC-E", "用例标题": "有效行"}))
    wb.save(src)
    stats = convert(str(src), str(out))
    assert stats["skipped_empty"] == 1
    assert stats["exported"] == 1


def test_wrong_sheet_errors(tmp_path):
    src, out = tmp_path / "in.xlsx", tmp_path / "out.xlsx"
    wb = Workbook()
    wb.active.title = "别的"
    wb.save(src)
    with pytest.raises(SystemExit, match="测试用例"):
        convert(str(src), str(out))
```

### Step 3: 运行测试确认失败

Run: `cd e:/AI/skills/testflow/scripts && python -m pytest tests/test_convert_25col_to_ui_xlsx.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'convert_25col_to_ui_xlsx'`）

### Step 4: 写实现

创建 `e:/AI/skills/testflow/scripts/convert_25col_to_ui_xlsx.py`，完整代码如下（逐字使用）：

```python
#!/usr/bin/env python3
"""25列测试用例 Excel → browser-use-case-runner 规范 xlsx 转换器。

用法:
    python convert_25col_to_ui_xlsx.py -i artifacts/xx_testcases.xlsx -o artifacts/ui_cases.xlsx

规则:
    - 默认排除「API URL」列非空的行（API 用例走 ApiAutoTest 支线）
    - --types 按覆盖维度（正向/负向/边界/安全）可选过滤，归一化后匹配
    - 用例编号取「测试项/测试点」，为空时按「模块-功能-行号」生成
    - 同编号只保留首行
"""
import argparse

from openpyxl import Workbook, load_workbook

# runner 8 列输出表头 → 25 列来源列名
HEADER_MAP = {
    "用例编号": "测试项/测试点",
    "用例名称": "用例标题",
    "功能模块": "模块",
    "优先级": "用例优先级",
    "前置条件": "前置条件",
    "测试步骤": "测试步骤",
    "测试数据": "测试数据准备",
    "预期结果": "预期结果",
}
RUNNER_HEADERS = list(HEADER_MAP.keys())
SOURCE_COLS = list(HEADER_MAP.values())


def normalize_type(value) -> str:
    """与 spectest-generate 一致的类型归一化：去「测试/用例」后缀。"""
    return str(value or "").replace("测试", "").replace("用例", "").strip()


def cell_str(v) -> str:
    return "" if v is None else str(v).strip()


def convert(input_path, output_path, sheet_name="测试用例", include_types=None):
    """执行转换，返回统计 dict。"""
    wb = load_workbook(input_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise SystemExit(f"错误: Sheet '{sheet_name}' 不存在，可用 Sheet: {wb.sheetnames}")
    ws = wb[sheet_name]

    headers = [cell_str(c.value) for c in ws[1]]
    needed = set(SOURCE_COLS) | {"API URL", "用例类型"}
    col_idx = {h: headers.index(h) + 1 for h in needed if h in headers}

    stats = {"total": 0, "exported": 0, "skipped_api": 0,
             "skipped_type": 0, "skipped_dup": 0, "skipped_empty": 0}
    seen_ids = set()
    out_rows = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if all(cell_str(v) == "" for v in row):
            stats["skipped_empty"] += 1
            continue
        stats["total"] += 1

        def src(col_name, _row=row):
            i = col_idx.get(col_name)
            return cell_str(_row[i - 1]) if i else ""

        if src("API URL"):
            stats["skipped_api"] += 1
            continue
        if include_types is not None and normalize_type(src("用例类型")) not in include_types:
            stats["skipped_type"] += 1
            continue

        case_id = src("测试项/测试点") or f"{src('模块')}-{src('功能')}-{stats['total']}"
        if case_id in seen_ids:
            stats["skipped_dup"] += 1
            continue
        seen_ids.add(case_id)

        out_rows.append([src(c) for c in SOURCE_COLS])
        stats["exported"] += 1

    out_wb = Workbook()
    out_ws = out_wb.active
    out_ws.title = "UI用例"
    out_ws.append(RUNNER_HEADERS)
    for r in out_rows:
        out_ws.append(r)
    out_wb.save(output_path)
    return stats


def main():
    ap = argparse.ArgumentParser(description="25列测试用例 → runner 规范 xlsx 转换器")
    ap.add_argument("-i", "--input", required=True, help="25列 testcases.xlsx 路径")
    ap.add_argument("-o", "--output", required=True, help="输出 ui_cases.xlsx 路径")
    ap.add_argument("--sheet", default="测试用例", help="数据 Sheet 名（默认: 测试用例）")
    ap.add_argument("--types", default=None,
                    help="用例类型白名单（逗号分隔，归一化后匹配），如: 正向,边界。留空不过滤")
    args = ap.parse_args()

    include_types = {t.strip() for t in args.types.split(",") if t.strip()} if args.types else None
    stats = convert(args.input, args.output, args.sheet, include_types)

    print(f"输入: {args.input}")
    print(f"输出: {args.output}")
    print(f"总行数: {stats['total']} | 导出: {stats['exported']} | "
          f"跳过: API用例 {stats['skipped_api']}, 类型不符 {stats['skipped_type']}, "
          f"重复编号 {stats['skipped_dup']}, 空行 {stats['skipped_empty']}")


if __name__ == "__main__":
    main()
```

### Step 5: 运行测试确认全部通过

Run: `cd e:/AI/skills/testflow/scripts && python -m pytest tests/test_convert_25col_to_ui_xlsx.py -v`
Expected: 8 passed

### Step 6: 用真实产物冒烟验证（可选，若有现成 25 列 Excel）

Run: `ls e:/AI/skills/spectest/*.xlsx 2>/dev/null`
若有文件（如 `test_output.xlsx`）：
Run: `cd e:/AI/skills/testflow/scripts && python convert_25col_to_ui_xlsx.py -i e:/AI/skills/spectest/test_output.xlsx -o /tmp/ui_cases_smoke.xlsx && python -c "from openpyxl import load_workbook; wb=load_workbook('/tmp/ui_cases_smoke.xlsx'); print([c.value for c in wb.active[1]])"`
Expected: 打印 8 个 runner 表头；无文件则跳过此步
