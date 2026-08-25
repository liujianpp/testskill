# Final Whole-Branch Review Package — testflow 全部四个任务

## 规格文档

# testflow：测试技能全生命周期整合设计

- **日期**：2026-08-24
- **状态**：已与用户逐节确认（4 节全部通过）
- **范围**：把 6 大套件 22 个技能整合为一个端到端测试工作流

## 1. 背景与现状

`e:/AI/skills/` 下有 6 大技能套件，各自独立、仅零星衔接：

| 套件 | 定位 | 产物 | 生命周期位置 |
|------|------|------|------|
| prd-review | 测试视角需求评审（5 维度） | Markdown 评审报告 | ① 需求入口 |
| spectest（8 步） | 用例设计工作流 | 25 列 Excel / XMind / testcases.json | ② 用例设计主轴 |
| ApiAutoTest2.0（6 技能） | 接口自动化管道（代码驱动） | cases.json/xlsx、Allure 报告 | ③-A 接口执行支线 |
| browser-use-case-runner | UI 用例执行（表格/MD/手动） | Markdown 执行报告 + 截图 | ③-B UI 执行支线 |
| browser-use | 浏览器自动化底层 CLI 封装 | —— | 底层能力 |
| operation-manual | 网站操作手册（探索+截图） | 带截图的 Markdown 手册 | 可选附加产物 |

**三个断层**：
1. spectest 25 列 Excel ↔ case-runner 的 xlsx 列格式不一致，UI 支线接不上
2. spectest testcases.json ↔ ApiAutoTest cases.json 协议不同（但两链路源头不同，见决策 3）
3. 执行结果（25 列结果列 / Allure / case-runner MD）无统一汇总

## 2. 已确认的关键决策

| # | 决策 | 用户选择 |
|---|------|---------|
| 1 | 流程范围 | **全生命周期**：需求 → 评审 → 设计 → 双支线执行 → 统一报告；operation-manual 为可选附加产物 |
| 2 | 落地形态 | **新建调度 skill**（testflow），现有 22 个技能零改动，只补衔接层 |
| 3 | 需求驱动（spectest）与代码驱动（ApiAutoTest）链路关系 | **各自独立 + 报告汇合**。spectest 从需求文档出发，ApiAutoTest 从源码扫接口出发，互不转换，仅在统一报告处汇合 |
| 4 | UI 支线用例来源 | **从 25 列转换**（25列 → runner 规范 xlsx） |
| 5 | 统一报告 | **新建汇总脚本**（三源读取，缺哪跳哪） |

## 3. 总体架构

新建调度套件 `e:/AI/skills/testflow/`，定位：**流程导航 + 格式转换 + 报告汇总**。不实现任何测试能力。

```
testflow/
├── SKILL.md                      # 主调度：阶段判断、分支调度、恢复逻辑
├── scripts/
│   ├── convert_25col_to_ui_xlsx.py   # 25列 → runner xlsx（3B 入口）
│   └── aggregate_reports.py          # 三源 → 统一 Markdown 报告
└── references/
    └── workflow-map.md           # 全景流程图 + 各阶段入口技能 + 产物路径约定
```

**集成方式**：文档调度。testflow SKILL.md 用相对链接指向各阶段技能的 SKILL.md，执行到某阶段读取对应技能并完整移交控制权（不 fork、不改写）。各技能保持独立可用，testflow 只是「地图 + 转换器 + 汇总器」。

**触发方式**：`/testflow <需求文档路径>` 或自然语言「完整测试流程」「从需求到报告」。

## 4. 端到端流程（7 阶段）

```
阶段0        阶段1        阶段2              阶段3                 阶段4       阶段5
需求准备  →  需求评审  →  用例设计        →  执行（双支线）     →  统一报告  →  归档
(可选)       prd-review   spectest 8步        3A 接口 / 3B UI       汇总脚本     spectest-archive
```

| 阶段 | 入口技能 | 产物 | 说明 |
|------|---------|------|------|
| 0 预热（可选） | api-doc-generator | 接口文档 | 仅当只有源码没需求文档时；否则跳过 |
| 1 需求评审 | prd-review | 5 维评审报告（MD） | 作为 spectest-new proposal 输入附件 |
| 2 用例设计 | spectest 8 步（new→analysis→points→generate→review→fix） | 25 列 Excel + testcases.json | **分流点**：「用例类型」列 ∈ UI/功能类 → 3B；API 类 → 线索供 3A 参考 |
| 3A 接口支线 | api-doc-generator → api-scenario-generator → api-test-generator → api-test-runner | cases.json/xlsx + Allure | **默认不启动**：需用户显式要求或有源码且用户确认 |
| 3B UI 支线 | convert_25col_to_ui_xlsx.py → browser-use-case-runner | ui_cases.xlsx + MD 报告 + 截图 | 默认支线 |
| 4 统一报告 | aggregate_reports.py | unified-report.md | 三源缺哪个跳过哪个 |
| 5 归档 | spectest-archive | 归档目录 | 可选：operation-manual 生成手册 |

**调度规则**：
- **默认链路 1→2→3B→4**；3A 需用户显式触发
- **每阶段轻量确认**：产物落地后向用户复述（路径+统计+下一步选项），用户说继续才推进——不自动串联全部阶段（UI 执行需被测 URL、接口执行需环境信息，中途必问）
- **中断恢复**：基于产物存在性判断（无额外状态文件），再次 `/testflow` 时扫描目录报告「已完成阶段 X，可从 X+1 继续」

## 5. 脚本设计

### 5.1 convert_25col_to_ui_xlsx.py

- **输入**：25 列 `*_testcases.xlsx`；**输出**：runner 规范 8 列 xlsx（表头按 browser-use-case-runner 的 references/xlsx-columns.md）
- **列映射**：

| runner 8 列 | ← 25 列来源 | 规则 |
|---|---|---|
| 用例编号 | 测试项 | 若空则 `模块-功能-行号` 生成 |
| 用例名称 | 用例标题 | 直传 |
| 功能模块 | 模块 | 直传 |
| 优先级 | 用例优先级 | 直传（P0/P1 或 高/中/低 原样保留） |
| 前置条件 | 前置条件 | 直传 |
| 测试步骤 | 测试步骤 | 直传（保留换行） |
| 测试数据 | 测试数据 | 直传 |
| 预期结果 | 预期结果 | 直传 |

- **筛选规则**：只导出「用例类型」∈ {功能测试, UI测试, 功能, UI}（白名单可配置）；API 类、禁用行跳过
- **去重**：同编号只保留首行
- **自检输出**：总行数 / 导出数 / 跳过数（按原因分类：类型不符 / 禁用 / 重复编号）

### 5.2 aggregate_reports.py

- **输入**（三源，缺哪个跳过哪个，不报错）：

| 源 | 读取内容 | 缺失/空的处理 |
|---|---|---|
| 25 列 Excel | 「实际结果」「是否通过」「执行时间」列 | 全空（未人工执行）→ 该节标记「待执行」 |
| allure-results 目录 | testcase JSON（status: passed/failed/broken、duration） | 目录不存在或无 JSON → 跳过该节 |
| case-runner MD 报告 | `RESULT: PASS/FAIL/BLOCKED` 行 | 文件不存在 → 该节标「UI 报告未生成」 |

- **输出**：`spectest/changes/<name>/unified-report.md`，结构：
  1. **执行总览表**：三来源 × 用例数/通过/失败/阻塞/通过率。统计口径：通过率 = 通过/(通过+失败)，阻塞单列不进分母
  2. **需求覆盖对照**：从 25 列「关联需求ID」列统计（需求→用例数→通过率）；不做跨源用例关联
  3. **三节明细**：人工用例（25 列已执行行）/ 接口自动化（Allure 失败用例+根因建议）/ UI 执行（PASS/FAIL/BLOCKED+截图链接）
  4. **风险与建议**：失败集中模块、阻塞项、覆盖薄弱需求
- **CLI**：`--excel <path> --allure-dir <path> --ui-report <path> --output <path>`
  - 默认推导：`--excel` = 当前变更 `artifacts/` 下首个 `*_testcases.xlsx`；`--output` = 同目录 `unified-report.md`；`--allure-dir`/`--ui-report` 无默认，须显式传入或由 testflow 调度时按当轮执行记录填写

## 6. 状态与路径约定

复用 spectest 已有约定，**目标项目**的 `spectest/changes/<name>/` 是唯一状态根，testflow 不另起炉灶：

```
spectest/changes/<name>/
├── proposal.md                  # ← 阶段1 评审报告附于其后或被引用
├── project_info/                # spectest-analysis 产物
├── specs/                       # 测试点
├── artifacts/
│   ├── <name>_testcases.xlsx    # 25 列用例（双支线源头）
│   ├── ui_cases.xlsx            # ← 新：3B 入口产物
│   ├── api/                     # ← 新：3A 产物（cases.json、allure-results 路径记录）
│   └── unified-report.md        # ← 新：统一报告
└── db_info/                     # DB 断言信息（api-test-generator 用）
```

- API 支线的接口文档、scenario/cases 产物按各套件自身约定落在目标项目 `docs/` 下；testflow 只把 allure-results 路径记录进统一报告元信息
- 汇总时 `--allure-dir` 可显式指定（无隐式默认值，见 5.2 CLI 推导规则）

## 7. 部署同步

- testflow 与其他套件平级放 `e:/AI/skills/testflow/`
- sync_skills.ps1 扩展：新增 testflow 目录覆盖；同时修复脚本内 `$SourceDir` 旧路径问题（指向已迁移的旧地址 `E:\AI\spectest\spectest`）
- 流程：先在开发目录验证脚本，再同步部署到 `C:\Users\admin\.claude\skills\`

## 8. 非目标（明确不做）

- 不改造现有 22 个技能的内部逻辑
- 不做 spectest testcases.json ↔ ApiAutoTest cases.json 的互转（两链路独立，决策 3）
- 不做跨来源的用例级关联（仅报告级汇合）
- 不引入数据库/服务作为状态存储（纯文件产物存在性判断）
- 不自动串联全部阶段（每阶段轻量确认）

## 9. 测试策略

- 两个脚本各配单测（`scripts/tests/` 下 `test_convert_25col_to_ui_xlsx.py`、`test_aggregate_reports.py`）
- 转换器测试用例：标准 25 列输入、缺列输入、类型过滤、编号去重、空输入
- 汇总器测试用例：三源齐备、仅 Excel、仅 Allure、仅 MD、全空、统计口径验证（阻塞不进分母）
- 端到端验证：用一个真实需求文档（如 spectest/测试需求/ 下的样例）走一遍默认链路 1→2→3B→4

## 账本（含各任务裁定与 deferred minors）

# SDD ledger — plan: e:/AI/skills/docs/superpowers/plans/2026-08-24-testflow.md

## 环境适配（Ruling）

- Ruling: 工作区非 git 仓库 → 无 worktree / 无 commit / 无 BASE-HEAD diff。审查包改为「新建文件全文 + 修改前后对照」文件；任务完成判据 = 测试通过 + 计划步骤的 Expected 达成。代价：若需回滚只能手工删除文件；无 git 历史可考。

## 预审扫描（Pre-flight）

| 检查对 | 发现 | 裁定 |
|---|---|---|
| Task 1 ↔ Task 3（转换器 CLI 签名） | Task 1 Produces `-i/-o/--sheet/--types`；Task 3 SKILL.md Step 4 命令用 `-i/-o` —— 一致 | 通过 |
| Task 2 ↔ Task 3（汇总器 CLI 签名） | Task 2 Produces `--excel/--allure-dir/--ui-report/--output`；Task 3 Step 6 命令一致 | 通过 |
| Task 1 自身（测试 vs 实现） | 8 个测试的行为与实现代码逐条对应；`test_wrong_sheet_errors` 期望 `SystemExit` 且 match "测试用例"，实现 raise SystemExit(中文消息含 Sheet 名) —— 一致 | 通过 |
| Task 2 自身（测试 vs 实现） | 6 个测试与实现对应；`test_main_cli` 调 `main([...])`，实现签名 `main(argv=None)` —— 一致；`read_ui_results` 正则匹配测试样例 —— 一致 | 通过 |
| Task 4 自身（修改点 vs 现文件） | `$SourceDir = "E:\AI\spectest\spectest"` 存在于 sync_skills.ps1；追加块锚点（文件末尾 ls 提示行）存在 | 通过 |
| Task 1+2 共享 `tests/` 目录 | 无冲突（不同文件名） | 通过 |
| 计划 vs 审查准绳 | 无「断言为空的测试」或「逐字重复块」被强制要求 | 通过 |

预审结论：干净，无需裁定项。开始 Task 1。

## Task 1

- 状态: DONE_WITH_CONCERNS → 审查通过
- 产物: e:/AI/skills/testflow/scripts/convert_25col_to_ui_xlsx.py + tests/test_convert_25col_to_ui_xlsx.py（8/8 passed，冒烟 98行→导出6）
- Ruling: 实现者对计划逐字代码做了 4 处最小偏差修复（2 个实现 bug：回退编号未写入输出、needed 缺「功能」列；2 个测试断言缺陷：tuple==list 恒 False、空串读回 None）。控制器已用探针实验独立证实 openpyxl 两项行为，审查者逐行核对确认全部必要且正确。裁定：批准偏差，计划代码视为有笔误，实现为准。代价：若计划被重放，逐字代码会复现 bug——计划文档已不修改，账本此条即为记录。
- Task 1: complete (8/8 passed, review clean; minor 4 条已记录: types白名单未归一化/回退行号语义/SystemExit风格/src闭包, 均为计划继承，不阻塞)

## Task 2

- 状态: DONE → 审查 2 Important → fix round 1 → 完成
- 产物: e:/AI/skills/testflow/scripts/aggregate_reports.py + tests/test_aggregate_reports.py（6/6 + 全套 14/14）
- Ruling 1: 审查者指控「:178/:180 前缀为实现者未披露添加」——控制器 grep 独立核实简报 359/362/367/369 行原文即含前缀，仅 364 行缺失，指控的事实前提错误。实现者初版确为逐字一致。
- Ruling 2: 真实缺陷只有 :175 缺前缀（计划代码笔误），fix round 1 已补，5 行一致，报告偏差清单已更正为 1 处。
- Ruling 3: 用户批准跳过 fix round 1 的范围性重审——改动仅一行格式字符串且控制器已直接 grep 核实修复事实，重审增量价值小。
- Task 2: complete (14/14 passed, fix round 1: 2 addressed(1项经澄清成立), 0 open; minor 已记录: 50%断言不锁来源/执行时间列未读/阻塞列硬编码/capsys未用, 均计划继承不阻塞)

## Task 3

- 状态: DONE → 审查通过（Spec ✅ / Approved）
- 产物: e:/AI/skills/testflow/SKILL.md + references/workflow-map.md（逐字模板；Step 3 路径 11/11；Step 4 CLI 一致性通过）
- 审查者核实: 文档 CLI 与两脚本 argparse 逐行匹配；Task 2 行为注记与代码措辞一致；frontmatter/状态根/默认链/3A 门控/恢复机制全符合
- Task 3: complete (review clean; minor 3 条均为模板/计划层面，留最终审查: ①恢复表引用 artifacts/api/cases.json 但 3A 产物实际落 docs/（恢复标记可能永不存在）②"8步"标签 vs 实列 6 技能 ③<testflow-skill-dir> 占位符是新模式，部署时需解析)

## Task 4

- 状态: DONE → 审查通过（Spec ✅ / Approved）
- 产物: sync_skills.ps1 修复（$SourceDir + testflow 块）+ 真实部署完成（C:/Users/admin/.claude/skills/testflow/ 5 文件，控制器独立核验；部署目录 pytest 14/14）
- Ruling: 实现者计划外加 UTF-8 BOM（3 字节）——PS5.1 对无 BOM 含中文/emoji 脚本按 GBK 误解析，原脚本在本机早已解析失败（MissingEndCurlyBrace 落在未改动行即为证据）。裁定：必要最小修复，批准。代价：无（不加则 Step 3 必败）。
- Task 4: complete (部署验证通过, review clean; minor 3 条继承性: ①头注释仍指旧路径 ②SKILL.md 缺失时静默继续 ③非镜像式同步不清理废弃文件)

## Task 1 产物: convert_25col_to_ui_xlsx.py

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
    needed = set(SOURCE_COLS) | {"API URL", "用例类型", "功能"}  # 「功能」用于回退编号生成
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

        row_out = [src(c) for c in SOURCE_COLS]
        row_out[0] = case_id  # 回退生成的编号必须写入输出（源「测试项/测试点」为空）
        out_rows.append(row_out)
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

## Task 1 测试

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

## Task 2 产物: aggregate_reports.py

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

## Task 2 测试

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

## Task 3 产物: SKILL.md

---
name: testflow
description: >-
  测试全生命周期调度：需求评审(prd-review) → 用例设计(spectest) → 双支线执行
  (ApiAutoTest2.0 接口 / browser-use-case-runner UI) → 统一报告汇总。
  Use when the user asks for 完整测试流程、从需求到报告、testflow、端到端测试工作流,
  or wants to chain 需求评审/用例设计/用例执行/统一报告 in one run.
---

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
  | `artifacts/api/cases.json` | 阶段 3A 已有产物 |
  | `artifacts/unified-report.md` | 阶段 4 已完成 |
- **不存在** → 走 Step 2 从头开始
- 每完成一个阶段，向用户复述（产物路径 + 统计 + 下一步选项），**用户确认后才推进**

## Step 2：阶段1 需求评审

1. 调用 **prd-review** 技能（读取其 SKILL.md 并移交控制权），输入需求文档
2. 产出 5 维评审报告（MD）
3. 将报告路径记入 `spectest/changes/<name>/proposal.md`（附录或引用）

## Step 3：阶段2 用例设计

调用 **spectest** 8 步（每步都是独立技能，依次移交）：
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

## Task 3 产物: references/workflow-map.md

# testflow 全景流程图

## 端到端流程（7 阶段）

| 阶段 | 入口技能 | 产物 | 触发条件 |
|------|---------|------|---------|
| 0 预热（可选） | api-doc-generator | 接口文档（目标项目 docs/） | 只有源码、没需求文档时 |
| 1 需求评审 | prd-review | 5 维评审报告 MD → 附入 proposal.md | 默认链路起点 |
| 2 用例设计 | spectest-new / -analysis / -points / -generate / -review / -fix | artifacts/<name>_testcases.xlsx（25列）+ testcases.json | 阶段 1 完成后 |
| 3A 接口支线 | api-doc-generator → api-scenario-generator → api-test-generator → api-test-runner | docs/ 下 scenario/cases + Allure | **用户显式要求**或有源码且确认 |
| 3B UI 支线 | testflow 转换器 + browser-use-case-runner | artifacts/ui_cases.xlsx + MD 报告 + 截图 | 默认支线 |
| 4 统一报告 | testflow 汇总器 | artifacts/unified-report.md | 任一执行支线完成后 |
| 5 归档 | spectest-archive（可选 operation-manual） | 归档目录 / 操作手册 | 用户确认后 |

## 状态目录与产物

```
spectest/changes/<name>/
├── proposal.md                  # 阶段1 评审报告附于其后或被引用
├── project_info/                # spectest-analysis 产物
├── specs/                       # 测试点
├── artifacts/
│   ├── <name>_testcases.xlsx    # 25列用例（双支线源头）
│   ├── ui_cases.xlsx            # 3B 入口产物（testflow 转换器输出）
│   ├── api/                     # 3A 记录（allure-results 路径等）
│   └── unified-report.md        # 统一报告（testflow 汇总器输出）
└── db_info/                     # DB 断言信息（api-test-generator 用）
```

## 格式契约

- **25 列表头**：系统/项目, 模块, 功能, 测试项/测试点, 用例标题, 前置条件, 涉及相关数据库表, 测试数据准备, 测试步骤, 预期结果, 验证SQL, 实际结果, 是否通过, 预估工时, 执行时间, 测试进度, 用例类型, 用例优先级, 是否回归用例, 是否阻塞上线, 关联需求ID, API URL, BUG数, BUG未解决数, 用例版本
- **runner 8 列表头**：用例编号, 用例名称, 功能模块, 优先级, 前置条件, 测试步骤, 测试数据, 预期结果
- **列映射**（转换器 HEADER_MAP）：用例编号←测试项/测试点，用例名称←用例标题，功能模块←模块，优先级←用例优先级，前置条件←前置条件，测试步骤←测试步骤，测试数据←测试数据准备，预期结果←预期结果
- **API 用例判定**：25 列中「API URL」非空
- **统计口径**：通过率 = 通过/(通过+失败)，阻塞单列不进分母

## 双链路独立性

- **需求驱动链路**（prd-review → spectest）：源头是需求文档
- **代码驱动链路**（api-doc-generator → … → api-test-runner）：源头是后端源码
- 两链路互不转换、各自独立，**仅在阶段 4 统一报告处汇合**（不做用例级关联）

## Task 4 产物: sync_skills.ps1（修改后全文）

﻿# SpecTest 技能同步脚本
# 用途：将 E:\AI\spectest\spectest\spectest-*\ 同步到 C:\Users\admin\.claude\skills\spectest-*\

$SourceDir = "E:\AI\skills\spectest\spectest"
$TargetDir = "C:\Users\admin\.claude\skills"

Write-Host "=== 开始同步 SpecTest 技能 ===" -ForegroundColor Green
Write-Host "源目录: $SourceDir"
Write-Host "目标目录: $TargetDir"
Write-Host ""

# 统计变量
$totalSkills = 0
$syncedScripts = 0
$syncedSkillMd = 0

foreach ($skillDir in Get-ChildItem -Path "$SourceDir\spectest-*" -Directory) {
    $skillName = $skillDir.Name
    $targetPath = Join-Path $TargetDir $skillName

    Write-Host "📦 处理: $skillName" -ForegroundColor Cyan
    $totalSkills++

    # 创建目标目录（如果不存在）
    if (-not (Test-Path $targetPath)) {
        New-Item -ItemType Directory -Path $targetPath | Out-Null
        Write-Host "  ✓ 创建目录: $targetPath" -ForegroundColor Yellow
    }

    # 同步 scripts 目录
    $scriptsPath = Join-Path $skillDir.FullName "scripts"
    if (Test-Path $scriptsPath) {
        $targetScripts = Join-Path $targetPath "scripts"
        if (-not (Test-Path $targetScripts)) {
            New-Item -ItemType Directory -Path $targetScripts | Out-Null
        }
        Copy-Item -Path "$scriptsPath\*" -Destination $targetScripts -Recurse -Force
        Write-Host "  ✓ scripts/ 已同步" -ForegroundColor Green
        $syncedScripts++
        # 显示同步的 Python 文件
        $pyFiles = Get-ChildItem -Path $targetScripts -Filter "*.py" -File
        foreach ($py in $pyFiles) {
            Write-Host "      - $($py.Name)" -ForegroundColor Gray
        }
    }

    # 同步 SKILL.md
    $skillMd = Join-Path $skillDir.FullName "SKILL.md"
    if (Test-Path $skillMd) {
        Copy-Item $skillMd -Destination $targetPath -Force
        Write-Host "  ✓ SKILL.md 已同步" -ForegroundColor Green
        $syncedSkillMd++
    }

    # 同步 references 目录
    $refsPath = Join-Path $skillDir.FullName "references"
    if (Test-Path $refsPath) {
        $targetRefs = Join-Path $targetPath "references"
        if (-not (Test-Path $targetRefs)) {
            New-Item -ItemType Directory -Path $targetRefs | Out-Null
        }
        Copy-Item -Path "$refsPath\*" -Destination $targetRefs -Recurse -Force
        Write-Host "  ✓ references/ 已同步" -ForegroundColor Green
    }

    # 同步 assets 目录
    $assetsPath = Join-Path $skillDir.FullName "assets"
    if (Test-Path $assetsPath) {
        $targetAssets = Join-Path $targetPath "assets"
        if (-not (Test-Path $targetAssets)) {
            New-Item -ItemType Directory -Path $targetAssets | Out-Null
        }
        Copy-Item -Path "$assetsPath\*" -Destination $targetAssets -Recurse -Force
        Write-Host "  ✓ assets/ 已同步" -ForegroundColor Green
    }

    # 同步 pyproject.toml
    $pyproject = Join-Path $skillDir.FullName "pyproject.toml"
    if (Test-Path $pyproject) {
        Copy-Item $pyproject -Destination $targetPath -Force
        Write-Host "  ✓ pyproject.toml 已同步" -ForegroundColor Green
    }

    Write-Host "  ✅ $skillName 同步完成" -ForegroundColor Green
    Write-Host ""
}

Write-Host "=== ✅ 所有 SpecTest 技能已同步完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "📊 同步统计：" -ForegroundColor Cyan
Write-Host "  总技能数: $totalSkills"
Write-Host "  同步 scripts/: $syncedScripts"
Write-Host "  同步 SKILL.md: $syncedSkillMd"
Write-Host ""
Write-Host "⏰ 同步时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""
Write-Host "💡 提示：请验证关键脚本是否同步成功" -ForegroundColor Yellow
Write-Host "   ls $TargetDir\spectest-generate\scripts\"

# ══════════════════════════════════════════════════════════
# testflow 调度套件同步（scripts/references 整目录 + SKILL.md）
# ══════════════════════════════════════════════════════════
$TestflowSource = "E:\AI\skills\testflow"
$TestflowTarget = Join-Path $TargetDir "testflow"

if (Test-Path $TestflowSource) {
    Write-Host "📦 处理: testflow" -ForegroundColor Cyan
    if (-not (Test-Path $TestflowTarget)) {
        New-Item -ItemType Directory -Path $TestflowTarget | Out-Null
    }
    foreach ($sub in @("scripts", "references")) {
        $srcSub = Join-Path $TestflowSource $sub
        $dstSub = Join-Path $TestflowTarget $sub
        if (Test-Path $srcSub) {
            if (-not (Test-Path $dstSub)) { New-Item -ItemType Directory -Path $dstSub | Out-Null }
            Copy-Item -Path "$srcSub\*" -Destination $dstSub -Recurse -Force
            Write-Host "  ✓ $sub/ 已同步" -ForegroundColor Green
        }
    }
    Copy-Item (Join-Path $TestflowSource "SKILL.md") -Destination $TestflowTarget -Force
    Write-Host "  ✓ SKILL.md 已同步" -ForegroundColor Green
    Write-Host "  ✅ testflow 同步完成" -ForegroundColor Green
} else {
    Write-Host "⚠️ 未找到 $TestflowSource，跳过 testflow 同步" -ForegroundColor Yellow
}
