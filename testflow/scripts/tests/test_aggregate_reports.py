import json
import sys
from pathlib import Path

from openpyxl import Workbook

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from aggregate_reports import (build_report, main, read_allure_results,
                               read_excel_rows, read_mp_results,
                               read_playwright_results, read_ui_results)

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


def test_read_ui_results_md_report_format(tmp_path):
    """case-runner MD 报告模板格式：`- **结果**: PASS`（中文键，** 在冒号前）。"""
    md = tmp_path / "case-run-md.md"
    md.write_text(
        "# 浏览器用例执行报告\n\n"
        "## TC-LOGIN-001 页面展示与标题\n\n"
        "- **结果**: PASS\n- **依据**: state 中出现标题「用户登录」\n\n"
        "## TC-LOGIN-002 登录失败提示\n\n"
        "- **结果**: FAIL\n\n"
        "## TC-003 验证码\n\n"
        "- **结果**: BLOCKED\n", encoding="utf-8")
    rows = read_ui_results(str(md))
    assert [r["result"] for r in rows] == ["PASS", "FAIL", "BLOCKED"]


def test_read_excel_rows_weitongguo(tmp_path):
    src = tmp_path / "in.xlsx"
    build_25col(src, [
        row_for(**{"用例标题": "文档口径失败", "是否通过": "未通过", "模块": "登录"}),
    ])
    rows = read_excel_rows(str(src))
    assert rows[0]["is_passed"] is False and rows[0]["executed"] is True


def test_main_cli_excel_default_derived(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "artifacts").mkdir()
    build_25col(tmp_path / "artifacts" / "demo_testcases.xlsx", [
        row_for(**{"用例标题": "推导行", "是否通过": "是", "关联需求ID": "REQ-1"}),
    ])
    out = tmp_path / "unified.md"
    rc = main(["--output", str(out)])
    assert rc == 0
    assert "推导行" in out.read_text(encoding="utf-8")


# ── miniprogram 支线（3C）──

MP_LEDGER_MD = (
    "# 台账\n\n"
    "## Session 20260916-100000\n\n"
    "- **TC-MP-001** | PASS | exit=0 | spec=`miniprogram/tests/auth/auth.spec.js`\n"
    "- **TC-MP-002** | FAIL | exit=1 | spec=`miniprogram/tests/auth/auth.spec.js`\n"
    "\n"
    "## Session 20260917-120000\n\n"
    "- **TC-MP-001** | PASS | exit=0 | spec=`miniprogram/tests/auth/auth.spec.js`\n"
    "- **TC-MP-002** | PASS | exit=0 | spec=`miniprogram/tests/auth/auth.spec.js`\n"
    "- **TC-MP-003** | FAIL | exit=1 | spec=`miniprogram/tests/home/home.spec.js`\n"
)

MP_SESSION_MD = (
    "# 小程序自动化测试报告\n\n"
    "## 执行顺序\n\n"
    "1. `miniprogram/tests/auth/auth.spec.js` — PASS\n"
    "2. `miniprogram/tests/home/home.spec.js` — FAIL\n"
    "3. `miniprogram/tests/profile/profile.spec.js` — NOT_RUN\n"
)


def test_read_mp_results_ledger(tmp_path):
    """台账格式：取最后一个 Session 段，label 为用例 ID。"""
    md = tmp_path / "miniprogram-executions.md"
    md.write_text(MP_LEDGER_MD, encoding="utf-8")
    rows = read_mp_results(str(md))
    assert [(r["label"], r["result"]) for r in rows] == [
        ("TC-MP-001", "PASS"),
        ("TC-MP-002", "PASS"),
        ("TC-MP-003", "FAIL"),
    ]


def test_read_mp_results_session_report(tmp_path):
    """Session 批量报告格式：label 为 spec 路径，含 NOT_RUN（全角破折号）。"""
    md = tmp_path / "miniprogram-report-20260917-120000.md"
    md.write_text(MP_SESSION_MD, encoding="utf-8")
    rows = read_mp_results(str(md))
    assert [(r["result"]) for r in rows] == ["PASS", "FAIL", "NOT_RUN"]
    assert rows[0]["label"] == "miniprogram/tests/auth/auth.spec.js"


def test_build_report_with_mp_source(tmp_path):
    mp_rows = [
        {"label": "TC-MP-001", "result": "PASS"},
        {"label": "TC-MP-002", "result": "FAIL"},
        {"label": "TC-MP-003", "result": "NOT_RUN"},
    ]
    report = build_report([], [], [], mp_rows)
    assert "小程序执行(miniprogram)" in report     # 总览行
    assert "### 3.4 小程序执行（miniprogram）" in report
    assert "TC-MP-002" in report                   # 失败用例 ID 出现在明细与风险
    # NOT_RUN 计入待执行列；通过率 = 1/(1+1) = 50%
    assert "| 小程序执行(miniprogram) | 3 | 1 | 1 | - | 1 | 50.0% |" in report
    assert "小程序执行失败 1 条" in report
    assert "小程序有 1 条未执行" in report


def test_main_cli_mp_report(tmp_path, capsys):
    excel = tmp_path / "tc.xlsx"
    build_25col(excel, [
        row_for(**{"用例标题": "通过行", "是否通过": "是", "关联需求ID": "REQ-1"}),
    ])
    mp = tmp_path / "miniprogram-executions.md"
    mp.write_text(MP_LEDGER_MD, encoding="utf-8")
    out = tmp_path / "unified.md"
    rc = main(["--excel", str(excel), "--mp-report", str(mp), "--output", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "小程序执行(miniprogram)" in text
    assert "TC-MP-003" in text
    assert "小程序: 3 条" in capsys.readouterr().out


# ── Playwright JSON 源 ──────────────────────────────────────────────

def _write_playwright_json(tmp_path, statuses):
    """构造 Playwright JSON reporter 结构：suites→specs→tests→results。"""
    tests = []
    for title, status, msg in statuses:
        tests.append({
            "title": title, "ok": status in ("passed", "flaky"),
            "tests": [{
                "file": f"main/tests/{title[:6]}.spec.ts",
                "results": [{"status": status, "error": {"message": msg} if msg else None}],
            }],
        })
    data = {"suites": [{"title": "chromium", "suites": [], "specs": tests}]}
    p = tmp_path / "playwright-results.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def test_read_playwright_results(tmp_path):
    p = _write_playwright_json(tmp_path, [
        ("[CASE:TC-001] 登录成功", "passed", ""),
        ("[CASE:TC-002] 密码错误", "failed", "TimeoutError: locator.click"),
        ("[CASE:TC-003] 过期提示", "skipped", ""),
        ("[CASE:TC-004] flaky用例", "flaky", "first attempt failed"),
    ])
    rows = read_playwright_results(p)
    assert len(rows) == 4
    by_label = {r["label"]: r for r in rows}
    assert by_label["[CASE:TC-001] 登录成功"]["result"] == "PASS"
    assert by_label["[CASE:TC-002] 密码错误"]["result"] == "FAIL"
    assert "TimeoutError" in by_label["[CASE:TC-002] 密码错误"]["message"]
    assert by_label["[CASE:TC-003] 过期提示"]["result"] == "NOT_RUN"
    assert by_label["[CASE:TC-004] flaky用例"]["result"] == "PASS"
    assert by_label["[CASE:TC-004] flaky用例"]["status"] == "flaky"


def test_read_playwright_results_bad_file(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert read_playwright_results(str(bad)) == []


def test_build_report_with_playwright_source(tmp_path):
    p = _write_playwright_json(tmp_path, [
        ("[CASE:TC-001] 登录成功", "passed", ""),
        ("[CASE:TC-002] 密码错误", "failed", "expect failed"),
    ])
    rows = read_playwright_results(p)
    report = build_report([], [], [], [], pw_rows=rows)
    assert "界面自动化(Playwright)" in report
    assert "| 界面自动化(Playwright) | 2 | 1 | 1 | - | 0 | 50.0% |" in report
    assert "### 3.5 界面自动化（Playwright）" in report
    assert "[CASE:TC-002] 密码错误" in report
    assert "界面自动化失败 1 条" in report


def test_main_cli_playwright_json(tmp_path, capsys):
    wb = Workbook(); ws = wb.active; ws.title = "测试用例"
    ws.append(["用例标题", "模块", "实际结果", "是否通过", "关联需求ID"])
    ws.append(["冒烟", "登录", "", "", ""])
    excel = tmp_path / "x_testcases.xlsx"; wb.save(excel)
    p = _write_playwright_json(tmp_path, [("[CASE:TC-001] 登录成功", "passed", "")])
    out = tmp_path / "unified-report.md"
    rc = main(["--excel", str(excel), "--playwright-json", p, "--output", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "界面自动化(Playwright)" in text
    assert "Playwright: 1 条" in capsys.readouterr().out
