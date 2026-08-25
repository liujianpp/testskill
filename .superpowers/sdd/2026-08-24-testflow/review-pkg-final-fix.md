# Final Fix Re-Review Package

## 修复报告

# Final Fix Report: 最终审查修复执行报告

日期：2026-08-24 | 依据：final-fix-brief.md（控制器裁定版） | 结果：**全部完成，双目录测试全绿**

## 修复清单（6 Fix，4 文件 + 1 测试文件）

### Fix 1（Critical）: aggregate_reports.py UI 正则 — 已修复
- 文件：`e:/AI/skills/testflow/scripts/aggregate_reports.py` :24
- 改动：`UI_RESULT_RE` 由 `RESULT[:：]\s*\**\s*(PASS|FAIL|BLOCKED)` 改为 `(?:RESULT|结果)\**[:：]\s*\**\s*(PASS|FAIL|BLOCKED)`（IGNORECASE）
- 效果：同时匹配终端格式 `[TC-001] RESULT: PASS` 与 case-runner MD 报告模板 `- **结果**: PASS`（中文键 + `**` 在冒号前），并兼容冒号两侧的 `**`。已核对无报：`- **预期结果**: 登录成功` 不含状态关键字，不会误匹配。
- 新增测试：`test_read_ui_results_md_report_format`（MD 模板格式 PASS/FAIL/BLOCKED 三态全解析）

### Fix 2（Important）: aggregate_reports.py FAIL_TOKENS 补「未通过」— 已修复
- 文件：同上 :23
- 改动：`FAIL_TOKENS` 集合加入 `"未通过"`（对齐 spectest 值字典文档口径 `通过/未通过/阻塞`）。「阻塞」归待执行展示为已裁定遗留，未加计数器。
- 新增测试：`test_read_excel_rows_weitongguo`（`is_passed is False and executed is True`）

### Fix 3（Important）: aggregate_reports.py --excel 默认推导 — 已修复
- 文件：同上 main()
- 改动：
  - `--excel` 由 `required=True` 改为 `default=None`，help 更新为「默认: cwd 的 artifacts/ 下首个 *_testcases.xlsx」
  - main 中 `args.excel` 为 None 时：glob cwd 本身 + cwd 的 `artifacts/` 子目录下 `*_testcases.xlsx`，排序后取字典序首个（确定性）；找不到则 `ap.error("--excel 未提供且 artifacts/ 下无 *_testcases.xlsx")`（退出码 2）；推导成功打印 `使用推导 Excel: <路径>`
  - **陷阱规避**：`output` 默认推导依赖 `args.excel` 的 parent，已移到 excel 推导分支之后计算（简报预警的真实陷阱，已在代码中加注释标明）
- 新增测试：`test_main_cli_excel_default_derived`（monkeypatch.chdir + artifacts/demo_testcases.xlsx，`--output` 单独传参，验证 rc=0 且输出含推导行数据）

### Fix 4（Minor）: convert_25col_to_ui_xlsx.py --types 归一化 — 已修复
- 文件：`e:/AI/skills/testflow/scripts/convert_25col_to_ui_xlsx.py` main()
- 改动：白名单构造由 `{t.strip() ...}` 改为 `{normalize_type(t) for t in args.types.split(",") if t.strip()}`，消除「`--types 功能测试` 过滤掉所有行」的静默偏差；help 示例由「如: 正向,边界」改为「如: 功能,UI」
- 附验：命令行实测 `normalize_type('功能测试') == '功能'`，与行值归一化口径一致

### Fix 5（Important，文档）: SKILL.md 四处 — 已修复
- 文件：`e:/AI/skills/testflow/SKILL.md`
  1. Step 1 恢复表：`artifacts/api/cases.json | 阶段 3A 已有产物` → `artifacts/api/ 下有说明文件（如 allure_path.txt） | 阶段 3A 已执行`（对齐 3A 产物落目标项目 docs/ 的套件约定）
  2. Step 2 第 3 点：改为「暂存评审报告路径；在 Step 3 的 spectest-new 创建变更目录并生成 proposal.md 后，将报告路径补记入 proposal.md（作为输入附件）」，消除时序矛盾
  3. Step 3 标题行加括注：「（report/archive 两步由本流程的阶段 4/5 承接；每步都是独立技能，依次移交）」
  4. frontmatter 之后加 blockquote：`> 本文件中 <testflow-skill-dir> 指本 SKILL.md 所在技能目录（部署后为 C:\Users\admin\.claude\skills\testflow）。`
- 注：第 3 处括注与原有「每步都是独立技能，依次移交」合并为一行括注，语义不变。

### Fix 6（Minor）: sync_skills.ps1 头注释 — 已修复
- 文件：`e:/AI/skills/spectest/spectest/sync_skills.ps1` :2
- 改动：注释路径 `E:\AI\spectest\spectest\` → `E:\AI\skills\spectest\spectest\`（与 $SourceDir 一致），未动其他内容
- **UTF-8 BOM 保留验证**：修改后 `head -c 3 | xxd` = `ef bb bf`，BOM 完好

## 测试与部署验证（三步全过）

### 1. 开发目录测试（e:/AI/skills/testflow/scripts）
```
python -m pytest tests/ -v
============================= 17 passed in 3.27s ==============================
```
原 14 + 新增 3（test_read_ui_results_md_report_format / test_read_excel_rows_weitongguo / test_main_cli_excel_default_derived），全部通过，无跳过无失败。

### 2. 重新部署（sync_skills.ps1）
```
powershell -ExecutionPolicy Bypass -File e:/AI/skills/spectest/spectest/sync_skills.ps1
EXIT_CODE=0
... 处理: testflow → scripts/ 已同步, references/ 已同步, SKILL.md 已同步, testflow 同步完成
```
（bash 调用下中文输出乱码属预期，以退出码 0 与关键行为准；spectest 9 技能 + testflow 均同步。）

### 3. 部署目录测试（C:/Users/admin/.claude/skills/testflow/scripts）
```
python -m pytest tests/ -v
============================= 17 passed in 1.05s ==============================
```
另 grep 验证部署版 SKILL.md 含全部 4 处 Fix 5 文案（命中 5 行，含括注合并行）。

## 遗留与说明
- 无阻塞遗留。「阻塞」值计数、report/archive 承接细节均为控制器已裁定不在本次范围。
- Fix 4 的新行为（CLI 层 --types 归一化）由命令行实测验证；现有 convert() 层测试 `test_types_filter_on_coverage_dim` 继续通过。

## 修复后 aggregate_reports.py

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
FAIL_TOKENS = {"否", "不通过", "未通过", "失败", "n", "no", "fail", "failed", "false", "0"}
UI_RESULT_RE = re.compile(r"(?:RESULT|结果)\**[:：]\s*\**\s*(PASS|FAIL|BLOCKED)", re.IGNORECASE)


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
        risks.append(f"- UI 执行失败 {ui_fail} 条、阻塞 {ui_blocked} 条（详见截图与报告）")
    weak = [k for k, g in reqs.items() if k != "（未关联）" and all(not r["executed"] or r["is_passed"] is False for r in g)]
    if weak:
        risks.append(f"- 覆盖薄弱需求（无用例通过）：{', '.join(sorted(weak))}")
    if manual_pending:
        risks.append(f"- 尚有 {manual_pending} 条人工用例待执行")
    lines.extend(risks if risks else ["- 暂无显著风险"])

    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="三源执行结果汇总 → 统一 Markdown 报告")
    ap.add_argument("--excel", default=None, help="25列 testcases.xlsx 路径（默认: cwd 的 artifacts/ 下首个 *_testcases.xlsx）")
    ap.add_argument("--allure-dir", default=None, help="allure-results 目录（缺省则跳过该节）")
    ap.add_argument("--ui-report", default=None, help="case-runner MD 报告路径（缺省则跳过该节）")
    ap.add_argument("--output", default=None, help="输出路径（默认: Excel 同目录 unified-report.md）")
    args = ap.parse_args(argv)

    # --excel 未提供时，从 cwd 的 artifacts/ 子目录（含 cwd 本身）推导
    if not args.excel:
        candidates = sorted(
            list(Path.cwd().glob("*_testcases.xlsx"))
            + list((Path.cwd() / "artifacts").glob("*_testcases.xlsx"))
        )
        if not candidates:
            ap.error("--excel 未提供且 artifacts/ 下无 *_testcases.xlsx")
        args.excel = str(candidates[0])
        print(f"使用推导 Excel: {args.excel}")

    excel_rows = read_excel_rows(args.excel)
    allure_rows = read_allure_results(args.allure_dir) if args.allure_dir else []
    ui_rows = read_ui_results(args.ui_report) if args.ui_report and Path(args.ui_report).exists() else []

    report = build_report(excel_rows, allure_rows, ui_rows)

    # 注意：output 默认依赖 args.excel 的 parent，必须在 excel 推导之后计算
    output = args.output or str(Path(args.excel).parent / "unified-report.md")
    Path(output).write_text(report, encoding="utf-8")
    print(f"统一报告已生成: {output}")
    print(f"  人工用例: {len(excel_rows)} 行 | Allure: {len(allure_rows)} 条 | UI: {len(ui_rows)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

## 修复后 SKILL.md

---
name: testflow
description: >-
  测试全生命周期调度：需求评审(prd-review) → 用例设计(spectest) → 双支线执行
  (ApiAutoTest2.0 接口 / browser-use-case-runner UI) → 统一报告汇总。
  Use when the user asks for 完整测试流程、从需求到报告、testflow、端到端测试工作流,
  or wants to chain 需求评审/用例设计/用例执行/统一报告 in one run.
---

> 本文件中 <testflow-skill-dir> 指本 SKILL.md 所在技能目录（部署后为 C:\Users\admin\.claude\skills\testflow）。

# testflow：测试全生命周期调度

本技能是「地图 + 转换器 + 汇总器」，**不实现任何测试能力**。各阶段技能独立可用；
执行到某阶段时读取对应技能的 SKILL.md 并完整移交控制权，阶段结束后收回。

## 全景流程

阶段图与各阶段入口技能详见 [references/workflow-map.md](references/workflow-map.md)。

```
阶段1          阶段2            阶段3                阶段4        阶段5
需求评审   →   用例设计      →  执行（双支线）     →  统一报告  →  归档
prd-review     spectest 8步      3A 接口(可选)        汇总脚本     spectest-archive
                                 3B UI(默认)
```

**默认链路：1 → 2 → 3B → 4**。3A 需用户显式要求或有后端源码且用户确认才启动。
阶段 0（api-doc-generator 预热）仅在「只有源码、没有需求文档」时使用。

## Task Progress

- [ ] Step 1: 定位状态目录（新建或恢复）
- [ ] Step 2: 阶段1 需求评审（prd-review）
- [ ] Step 3: 阶段2 用例设计（spectest new→analysis→points→generate→review→fix）
- [ ] Step 4: 阶段3B UI 支线（转换 + browser-use-case-runner）
- [ ] Step 5:（可选）阶段3A 接口支线（ApiAutoTest2.0）
- [ ] Step 6: 阶段4 统一报告（aggregate_reports.py）
- [ ] Step 7: 阶段5 归档（spectest-archive；可选 operation-manual）

## Step 1：定位状态目录

状态根 = **目标项目**的 `spectest/changes/<name>/`（复用 spectest 约定，不另起炉灶）。

- 用户给了变更名 → 检查 `spectest/changes/<name>/` 是否存在
- **已存在** → 按产物存在性判断进度，向用户复述「已完成阶段 X，可从 X+1 继续」：
  | 产物 | 说明阶段 |
  |---|---|
  | `artifacts/*_testcases.xlsx` | 阶段 2 已完成 |
  | `artifacts/ui_cases.xlsx` | 阶段 3B 转换已完成 |
  | UI MD 报告（case-runner 产物） | 阶段 3B 已执行 |
  | `artifacts/api/ 下有说明文件（如 allure_path.txt）` | 阶段 3A 已执行 |
  | `artifacts/unified-report.md` | 阶段 4 已完成 |
- **不存在** → 走 Step 2 从头开始
- 每完成一个阶段，向用户复述（产物路径 + 统计 + 下一步选项），**用户确认后才推进**

## Step 2：阶段1 需求评审

1. 调用 **prd-review** 技能（读取其 SKILL.md 并移交控制权），输入需求文档
2. 产出 5 维评审报告（MD）
3. 暂存评审报告路径；在 Step 3 的 spectest-new 创建变更目录并生成 proposal.md 后，将报告路径补记入 proposal.md（作为输入附件）

## Step 3：阶段2 用例设计

调用 **spectest** 8 步（report/archive 两步由本流程的阶段 4/5 承接；每步都是独立技能，依次移交）：
`spectest-new` → `spectest-analysis` → `spectest-points` → `spectest-generate` → `spectest-review` → `spectest-fix`

关键产物：`artifacts/<name>_testcases.xlsx`（25 列，Sheet「测试用例」）。

**分流判断**：25 列中「API URL」列非空的行是 API 用例（线索供 3A 参考）；
其余为 UI/功能用例 → 3B。

## Step 4：阶段3B UI 支线（默认）

1. **转换**（在 `spectest/changes/<name>/` 下执行）：

   ```bash
   python <testflow-skill-dir>/scripts/convert_25col_to_ui_xlsx.py \
     -i artifacts/<name>_testcases.xlsx \
     -o artifacts/ui_cases.xlsx
   ```

   检查自检输出（总行数/导出/跳过分类）。导出 0 行时停下询问用户。
2. 调用 **browser-use-case-runner** 技能执行 `artifacts/ui_cases.xlsx`（需向用户确认被测 URL 与会话策略）
3. 记录其 MD 报告与截图目录路径（供 Step 6 汇总）

## Step 5：（可选）阶段3A 接口支线

**启动条件**（二选一，且需用户确认）：用户显式要求接口自动化；目标项目有后端源码且用户同意。

依次调用：**api-doc-generator** → **api-scenario-generator** → **api-test-generator** → **api-test-runner**（各为独立技能，依次移交）。

- 产物按各套件自身约定落在目标项目 `docs/`；allure-results 路径记录到 `artifacts/api/` 下的说明文件（如 `allure_path.txt`），供 Step 6 读取
- **api-test-runner 只执行不修改**的原则不变

## Step 6：阶段4 统一报告

```bash
python <testflow-skill-dir>/scripts/aggregate_reports.py \
  --excel artifacts/<name>_testcases.xlsx \
  [--allure-dir <当轮 allure-results 路径>] \
  [--ui-report <case-runner MD 报告路径>] \
  --output artifacts/unified-report.md
```

三源缺哪个跳过哪个。注意：`--ui-report` 路径不存在时该节静默跳过（报告显示「UI 报告未生成」），不报错——若用户预期有 UI 报告，应先核对路径再汇总。生成后向用户展示报告摘要（总览表 + 风险条目）。

## Step 7：阶段5 归档

- 调用 **spectest-archive** 归档变更
- 用户需要手册时，调用 **operation-manual**（可选）

## 硬性规则

- 不修改现有各技能的内部逻辑与产物格式
- 不做 testcases.json ↔ cases.json 互转（两链路独立，仅在报告汇合）
- 每阶段结束必须向用户复述并等确认，不自动串联
- UI 执行遇验证码/人工介入，遵循 browser-use-case-runner 自身的停等规则

## 修复后测试文件（两个）

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
    assert list(headers) == RUNNER_HEADERS == [
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
    assert rows[0][6] in ("", None)  # openpyxl 不持久化空串，读回为 None


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
