# Task 2 Brief: 汇总器 aggregate_reports.py

（摘自 e:/AI/skills/docs/superpowers/plans/2026-08-24-testflow.md 的 Task 2 全文，逐字为准）

## Global Constraints（对本任务生效的摘录）

- 工作区 `e:/AI/skills/` **不是 git 仓库**：**无 commit 步骤**，以「验证产物存在/测试通过」收尾
- 平台 win32 + bash：路径用正斜杠；Python 命令用 `python`（不是 `python3`/`uv run`）
- 依赖：openpyxl、pytest（Task 1 已验证可用）
- 25 列标准表头（**逐字使用**）：`系统/项目, 模块, 功能, 测试项/测试点, 用例标题, 前置条件, 涉及相关数据库表, 测试数据准备, 测试步骤, 预期结果, 验证SQL, 实际结果, 是否通过, 预估工时, 执行时间, 测试进度, 用例类型, 用例优先级, 是否回归用例, 是否阻塞上线, 关联需求ID, API URL, BUG数, BUG未解决数, 用例版本`
- 25 列 Excel 数据 Sheet 名：`测试用例`（首行表头）
- 统计口径：通过率 = 通过/(通过+失败)，**阻塞不进分母**
- 中文为主体语言；脚本文件名、CLI 参数用英文

## 来自 Task 1 的重要经验（控制器补充，优先级高于简报逐字代码）

Task 1 发现计划逐字代码存在真实笔误，本任务同样可能遇到。规则调整：
- **「逐字使用」降级为「意图一致」**：如果逐字代码在本机测试红灯且根因是代码/断言缺陷，做最小修复并在报告中记录（位置/根因/修复三要素），不再视为违反约束
- 已知的 openpyxl 陷阱：(1) `iter_rows(values_only=True)` 返回 **tuple**，与 list 比较恒 False——断言用 `list(...)` 包一层；(2) **空字符串写盘后读回是 `None`**——断言用 `in ("", None)`
- 严格 TDD 不变：Step 2 红灯 → Step 4 实现 → Step 5 全绿

## Files

- Create: `e:/AI/skills/testflow/scripts/aggregate_reports.py`
- Test: `e:/AI/skills/testflow/scripts/tests/test_aggregate_reports.py`

## Interfaces

- Consumes: 25 列 xlsx（`实际结果`/`是否通过`/`执行时间`/`关联需求ID` 列）、allure-results 目录（`*-result.json`）、case-runner MD 报告（`RESULT: PASS|FAIL|BLOCKED` 行）
- Produces（Task 3 的 SKILL.md 引用此 CLI，签名不得变）:
  - CLI: `python aggregate_reports.py --excel <path> [--allure-dir <path>] [--ui-report <path>] [--output <path>]`
  - Python API:
    - `read_excel_rows(path: str) -> list[dict]`，元素键：`title, module, req_id, is_passed, executed, actual`（`is_passed: bool|None`，`executed: bool`）
    - `read_allure_results(dirpath: str) -> list[dict]`，元素键：`name, status, message`
    - `read_ui_results(path: str) -> list[dict]`，元素键：`result, line`
    - `build_report(excel_rows, allure_rows, ui_rows) -> str`（Markdown 全文）
    - `main() -> int`

## Steps

### Step 1: 写失败的单测

创建 `e:/AI/skills/testflow/scripts/tests/test_aggregate_reports.py`，完整代码如下（意图为准，注意 tuple/None 陷阱）：

```python
import json
import sys
from pathlib import Path

from openpyxl import Workbook

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from aggregate_reports import (build_report, main, read_allure_results,
                               read_excel_rows, read_ui_results)

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
    base = {h: "" for h in HEADERS_25}
    base.update(kw)
    return [base[h] for h in HEADERS_25]


def test_read_excel_rows(tmp_path):
    src = tmp_path / "in.xlsx"
    build_25col(src, [
        row_for(**{"用例标题": "已执行通过", "是否通过": "是", "实际结果": "符合预期", "关联需求ID": "REQ-1", "模块": "登录"}),
        row_for(**{"用例标题": "已执行失败", "是否通过": "否", "实际结果": "报错", "关联需求ID": "REQ-1", "模块": "登录"}),
        row_for(**{"用例标题": "未执行", "关联需求ID": "REQ-2", "模块": "查询"}),
    ])
    rows = read_excel_rows(str(src))
    assert len(rows) == 3
    assert rows[0]["is_passed"] is True and rows[0]["executed"] is True
    assert rows[1]["is_passed"] is False and rows[1]["executed"] is True
    assert rows[2]["is_passed"] is None and rows[2]["executed"] is False
    assert rows[0]["req_id"] == "REQ-1"


def test_read_allure_results(tmp_path):
    d = tmp_path / "allure-results"
    d.mkdir()
    (d / "001-result.json").write_text(json.dumps(
        {"name": "TC_API_001", "status": "passed"}, ensure_ascii=False), encoding="utf-8")
    (d / "002-result.json").write_text(json.dumps(
        {"name": "TC_API_002", "status": "failed",
         "statusDetails": {"message": "预期200实际404"}}, ensure_ascii=False), encoding="utf-8")
    rows = read_allure_results(str(d))
    assert len(rows) == 2
    by_name = {r["name"]: r for r in rows}
    assert by_name["TC_API_001"]["status"] == "passed"
    assert by_name["TC_API_002"]["message"] == "预期200实际404"


def test_read_ui_results(tmp_path):
    md = tmp_path / "case-run-x.md"
    md.write_text(
        "# UI 执行报告\n\n"
        "## TC-001 登录\n[TC-001] START\nSTATE: 登录页已打开\n[TC-001] RESULT: PASS\n\n"
        "## TC-002 查询\n[TC-002] RESULT: FAIL\n\n"
        "## TC-003 验证码\n[TC-003] RESULT: BLOCKED\n", encoding="utf-8")
    rows = read_ui_results(str(md))
    assert [r["result"] for r in rows] == ["PASS", "FAIL", "BLOCKED"]


def test_build_report_structure_and_pass_rate(tmp_path):
    excel_rows = [
        {"title": "用例A", "module": "登录", "req_id": "REQ-1", "is_passed": True, "executed": True, "actual": "ok"},
        {"title": "用例B", "module": "登录", "req_id": "REQ-1", "is_passed": False, "executed": True, "actual": "bad"},
        {"title": "用例C", "module": "查询", "req_id": "REQ-2", "is_passed": None, "executed": False, "actual": ""},
    ]
    allure_rows = [
        {"name": "TC_API_001", "status": "passed", "message": ""},
        {"name": "TC_API_002", "status": "failed", "message": "预期200实际404"},
        {"name": "TC_API_003", "status": "broken", "message": "连接超时"},
    ]
    ui_rows = [
        {"result": "PASS", "line": "[TC-001] RESULT: PASS"},
        {"result": "FAIL", "line": "[TC-002] RESULT: FAIL"},
        {"result": "BLOCKED", "line": "[TC-003] RESULT: BLOCKED"},
    ]
    report = build_report(excel_rows, allure_rows, ui_rows)
    # 结构：四个章节标题
    assert "# 测试统一报告" in report
    assert "## 1. 执行总览" in report
    assert "## 2. 需求覆盖对照" in report
    assert "## 3. 执行明细" in report
    assert "## 4. 风险与建议" in report
    # 通过率口径：阻塞不进分母 → UI 支线 1/(1+1)=50%
    assert "50.0%" in report or "50%" in report
    # 人工用例：1/2
    assert "待执行" in report          # 用例C 未执行
    assert "REQ-1" in report and "REQ-2" in report
    # Allure 失败明细含根因
    assert "预期200实际404" in report
    # 阻塞单列
    assert "阻塞" in report


def test_build_report_all_sources_missing(tmp_path):
    report = build_report([], [], [])
    assert "# 测试统一报告" in report
    assert "待执行" in report or "未生成" in report


def test_main_cli(tmp_path, capsys):
    excel = tmp_path / "tc.xlsx"
    build_25col(excel, [
        row_for(**{"用例标题": "通过行", "是否通过": "是", "关联需求ID": "REQ-1"}),
    ])
    out = tmp_path / "unified.md"
    rc = main([
        "--excel", str(excel),
        "--output", str(out),
    ])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "# 测试统一报告" in text
    assert "通过行" in text
```

### Step 2: 运行测试确认失败

Run: `cd e:/AI/skills/testflow/scripts && python -m pytest tests/test_aggregate_reports.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'aggregate_reports'`）

### Step 3: 写实现

创建 `e:/AI/skills/testflow/scripts/aggregate_reports.py`，完整代码如下（意图为准）：

```python
#!/usr/bin/env python3
"""三源执行结果汇总 → 统一 Markdown 报告。

源（缺哪个跳过哪个）:
    1. 25列 testcases.xlsx   —— 人工执行结果（实际结果/是否通过/执行时间/关联需求ID）
    2. allure-results 目录    —— 接口自动化（*-result.json 的 status）
    3. case-runner MD 报告    —— UI 执行（RESULT: PASS|FAIL|BLOCKED 行）

用法:
    python aggregate_reports.py --excel artifacts/xx_testcases.xlsx \
        [--allure-dir allure-results] [--ui-report reports/case-run-x.md] \
        [--output artifacts/unified-report.md]
"""
import argparse
import glob
import json
import re
from pathlib import Path

from openpyxl import load_workbook

PASS_TOKENS = {"是", "通过", "y", "yes", "pass", "passed", "true", "1"}
FAIL_TOKENS = {"否", "不通过", "失败", "n", "no", "fail", "failed", "false", "0"}
UI_RESULT_RE = re.compile(r"RESULT[:：]\s*\**\s*(PASS|FAIL|BLOCKED)", re.IGNORECASE)


def cell_str(v) -> str:
    return "" if v is None else str(v).strip()


def read_excel_rows(path: str) -> list[dict]:
    """读取 25 列 Excel 的人工执行结果行。"""
    wb = load_workbook(path, data_only=True)
    ws = wb["测试用例"] if "测试用例" in wb.sheetnames else wb[wb.sheetnames[0]]
    headers = [cell_str(c.value) for c in ws[1]]

    def idx(name):
        return headers.index(name) + 1 if name in headers else None

    i_title, i_module = idx("用例标题"), idx("模块")
    i_actual, i_pass, i_req = idx("实际结果"), idx("是否通过"), idx("关联需求ID")

    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if all(cell_str(v) == "" for v in row):
            continue

        def g(i, _row=row):
            return cell_str(_row[i - 1]) if i else ""

        verdict = g(i_pass).lower()
        is_passed = True if verdict in PASS_TOKENS else (False if verdict in FAIL_TOKENS else None)
        rows.append({
            "title": g(i_title), "module": g(i_module), "req_id": g(i_req),
            "actual": g(i_actual), "is_passed": is_passed, "executed": is_passed is not None,
        })
    return rows


def read_allure_results(dirpath: str) -> list[dict]:
    """读取 allure-results 下的 *-result.json。"""
    rows = []
    for f in sorted(glob.glob(str(Path(dirpath) / "*-result.json"))):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        rows.append({
            "name": str(d.get("name", "")),
            "status": str(d.get("status", "unknown")),
            "message": str((d.get("statusDetails") or {}).get("message", "")),
        })
    return rows


def read_ui_results(path: str) -> list[dict]:
    """解析 case-runner MD 报告中的 RESULT 行。"""
    rows = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = UI_RESULT_RE.search(line)
        if m:
            rows.append({"result": m.group(1).upper(), "line": line.strip()})
    return rows


def _rate(p: int, f: int) -> str:
    """通过率 = 通过/(通过+失败)，分母为 0 时显示 '-'。"""
    return f"{p / (p + f) * 100:.1f}%" if (p + f) else "-"


def build_report(excel_rows, allure_rows, ui_rows) -> str:
    # ── 统计 ──
    manual_pass = sum(1 for r in excel_rows if r["is_passed"] is True)
    manual_fail = sum(1 for r in excel_rows if r["is_passed"] is False)
    manual_pending = sum(1 for r in excel_rows if not r["executed"])

    allure_pass = sum(1 for r in allure_rows if r["status"] == "passed")
    allure_fail = sum(1 for r in allure_rows if r["status"] in ("failed", "broken"))

    ui_pass = sum(1 for r in ui_rows if r["result"] == "PASS")
    ui_fail = sum(1 for r in ui_rows if r["result"] == "FAIL")
    ui_blocked = sum(1 for r in ui_rows if r["result"] == "BLOCKED")

    lines = ["# 测试统一报告", "", "## 1. 执行总览", ""]
    lines.append("| 来源 | 用例数 | 通过 | 失败 | 阻塞 | 待执行 | 通过率 |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append(f"| 人工用例(25列Excel) | {len(excel_rows)} | {manual_pass} | {manual_fail} | - | {manual_pending} | {_rate(manual_pass, manual_fail)} |")
    lines.append(f"| 接口自动化(Allure) | {len(allure_rows)} | {allure_pass} | {allure_fail} | - | - | {_rate(allure_pass, allure_fail)} |")
    lines.append(f"| UI执行(case-runner) | {len(ui_rows)} | {ui_pass} | {ui_fail} | {ui_blocked} | - | {_rate(ui_pass, ui_fail)} |")
    lines.append("")
    lines.append("> 通过率 = 通过/(通过+失败)；阻塞单列不计入分母。")
    lines.append("")

    # ── 需求覆盖 ──
    lines += ["## 2. 需求覆盖对照", ""]
    reqs = {}
    for r in excel_rows:
        key = r["req_id"] or "（未关联）"
        reqs.setdefault(key, []).append(r)
    if reqs:
        lines.append("| 需求ID | 用例数 | 通过 | 失败 | 待执行 | 通过率 |")
        lines.append("|---|---|---|---|---|---|")
        for key in sorted(reqs):
            group = reqs[key]
            p = sum(1 for r in group if r["is_passed"] is True)
            f = sum(1 for r in group if r["is_passed"] is False)
            pending = sum(1 for r in group if not r["executed"])
            lines.append(f"| {key} | {len(group)} | {p} | {f} | {pending} | {_rate(p, f)} |")
    else:
        lines.append("（无 25 列 Excel 数据，需求覆盖待执行）")
    lines.append("")

    # ── 明细 ──
    lines += ["## 3. 执行明细", ""]
    lines += ["### 3.1 人工用例（25列 Excel）", ""]
    if not excel_rows:
        lines.append("（未提供 25 列 Excel）")
    else:
        lines.append("| 用例标题 | 模块 | 需求ID | 结果 | 实际结果 |")
        lines.append("|---|---|---|---|---|")
        for r in excel_rows:
            verdict = "待执行" if not r["executed"] else ("通过" if r["is_passed"] else "失败")
            lines.append(f"| {r['title']} | {r['module']} | {r['req_id'] or '-'} | {verdict} | {r['actual'] or '-'} |")
    lines.append("")

    lines += ["### 3.2 接口自动化（Allure）", ""]
    if not allure_rows:
        lines.append("（未提供 allure-results 目录或无结果文件）")
    else:
        failed = [r for r in allure_rows if r["status"] in ("failed", "broken")]
        lines.append(f"共 {len(allure_rows)} 条，失败/中断 {len(failed)} 条。失败明细：")
        lines.append("")
        for r in failed:
            lines.append(f"- **{r['name']}** [{r['status']}]：{r['message'] or '（无失败信息）'}")
    lines.append("")

    lines += ["### 3.3 UI 执行（case-runner）", ""]
    if not ui_rows:
        lines.append("（UI 报告未生成）")
    else:
        for r in ui_rows:
            lines.append(f"- {r['result']}：{r['line']}")
    lines.append("")

    # ── 风险与建议 ──
    lines += ["## 4. 风险与建议", ""]
    risks = []
    if manual_fail:
        mods = {r["module"] for r in excel_rows if r["is_passed"] is False and r["module"]}
        risks.append(f"- 人工用例失败 {manual_fail} 条，集中在模块：{', '.join(sorted(mods)) or '-'}")
    if allure_fail:
        names = [r["name"] for r in allure_rows if r["status"] in ("failed", "broken")]
        risks.append(f"- 接口自动化失败 {allure_fail} 条：{', '.join(names[:10])}{'…' if len(names) > 10 else ''}")
    if ui_fail or ui_blocked:
        risks.append(f"UI 执行失败 {ui_fail} 条、阻塞 {ui_blocked} 条（详见截图与报告）")
    weak = [k for k, g in reqs.items() if k != "（未关联）" and all(not r["executed"] or r["is_passed"] is False for r in g)]
    if weak:
        risks.append(f"覆盖薄弱需求（无用例通过）：{', '.join(sorted(weak))}")
    if manual_pending:
        risks.append(f"尚有 {manual_pending} 条人工用例待执行")
    lines.extend(risks if risks else ["- 暂无显著风险"])

    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="三源执行结果汇总 → 统一 Markdown 报告")
    ap.add_argument("--excel", required=True, help="25列 testcases.xlsx 路径")
    ap.add_argument("--allure-dir", default=None, help="allure-results 目录（缺省则跳过该节）")
    ap.add_argument("--ui-report", default=None, help="case-runner MD 报告路径（缺省则跳过该节）")
    ap.add_argument("--output", default=None, help="输出路径（默认: Excel 同目录 unified-report.md）")
    args = ap.parse_args(argv)

    excel_rows = read_excel_rows(args.excel)
    allure_rows = read_allure_results(args.allure_dir) if args.allure_dir else []
    ui_rows = read_ui_results(args.ui_report) if args.ui_report and Path(args.ui_report).exists() else []

    report = build_report(excel_rows, allure_rows, ui_rows)

    output = args.output or str(Path(args.excel).parent / "unified-report.md")
    Path(output).write_text(report, encoding="utf-8")
    print(f"统一报告已生成: {output}")
    print(f"  人工用例: {len(excel_rows)} 行 | Allure: {len(allure_rows)} 条 | UI: {len(ui_rows)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Step 4: 运行测试确认全部通过

Run: `cd e:/AI/skills/testflow/scripts && python -m pytest tests/test_aggregate_reports.py -v`
Expected: 6 passed

### Step 5: 跑全部测试

Run: `cd e:/AI/skills/testflow/scripts && python -m pytest tests/ -v`
Expected: 14 passed（Task 1 的 8 个 + Task 2 的 6 个）
