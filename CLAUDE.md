# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是 Claude Code Skills 开发工作区，用于创建、调整和维护 Agent Skills，聚焦测试领域（用例设计、API 自动化、Web UI 执行、需求评审）及配套文档生成。技能在此开发调试，同步到 `C:\Users\admin\.claude\skills\` 后由 Claude Code 实际调用。**不是 git 仓库**。

## 仓库结构

四大技能套件，每个顶层目录相互独立：

| 目录 | 内容 |
|------|------|
| `spectest/` | SpecTest 统一测试工作流（10 个技能，9 步流程）。**内含自己的 CLAUDE.md**，改 spectest 技能前先读它（含 25 列 Excel 格式定义、数据库配置等细节） |
| `ApiAutoTest2.0/` | API 自动化测试套件（6 个技能组成执行流水线） |
| `browser-use-case-runner/` | Web UI 用例执行器（xlsx/MD/手动用例 → 有头 browser-use 逐条执行 → Markdown 报告） |
| `browser-use/` | browser-use CLI 封装参考（`state`/`input`/`click`/`screenshot` 等命令契约；被 case-runner 依赖） |
| `operation-manual/` | 网站操作手册生成（playwright-cli 浏览器探索 + 截图，默认有头模式） |
| `prd-review/` | 测试视角需求评审（5 维度，支持 pdf/docx/md/txt） |
| `miniprogram/` | 微信小程序 UI 自动化三件套（script-author 写 Jest 脚本 / run 执行回归 / shared 共享约定；miniprogram-automator + 微信开发者工具模拟器） |
| `testflow/` | 测试全生命周期调度器（需求评审 → 用例设计 → 三支线执行 → 统一报告；自带 25列→runner 8列转换器与多源汇总器） |
| `web-script-author/` | 界面脚本生成（25 列 UI 用例 → Playwright spec，采真实 selector 不臆造，不执行不下结论；产物落测试资产库 `E:\AI\test-automation\web\`，主干/迭代目录见该库 README） |

浏览器自动化有两个独立工具链，勿混用：`browser-use` CLI（daemon 常驻、按索引操作）用于 UI 测试；`playwright-cli`（snapshot ref e0/e1）用于操作手册生成。

`spectest/archive/` 存放已废弃的 OpenTest / Testcase 原始技能，仅作历史参考，不再维护。

## 技能结构约定

每个技能是一个独立目录：

```
<skill-name>/
├── SKILL.md          # 必需。YAML frontmatter（name、description、可选 allowed-tools）+ 工作流正文
├── scripts/          # 可执行 Python 脚本（自包含，不依赖外部项目）
├── references/       # 详细参考文档（评审维度、格式说明、模板）
└── templates/        # 输出模板
```

技能间引用用 sibling 相对路径（如 `[../browser-use/SKILL.md](../browser-use/SKILL.md)`）；SKILL.md 中写死的 `.claude/skills/<skill-name>/scripts/...` 调用路径指向**部署后**的使用目录，开发目录中调试时需换成实际路径。

SKILL.md 编写规范：

- frontmatter `description` 包含中文触发词 + 英文 "Use when..." 双语触发描述
- 正文按「职责 → 执行步骤 → 产物 → 下一步」组织；流程型技能用 `Task Progress` 复选框追踪
- 引用技能内文件用相对路径链接（如 `[references/dimensions.md](references/dimensions.md)`）
- 中文为主体语言；脚本文件名、API、命令用英文

## 常用命令

### spectest 套件的 Python 脚本（必须用 uv，不能直接 python）

```bash
SKILL_DIR="e:/AI/skills/spectest/spectest/<skill-name>"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/<script>.py" [参数]
```

- `SKILL_DIR=` 赋值与 `uv run` 必须在**同一次** Bash 调用中，否则变量丢失
- 首次使用先 `uv sync --project "$SKILL_DIR"` 创建 .venv
- 依赖声明在各技能的 `pyproject.toml`（Python ≥3.10，常用 openpyxl、pymysql、pandas）

### ApiAutoTest2.0 脚本（直接 python）

```bash
# 执行 JSON 用例计划（pytest + Allure）
python ApiAutoTest2.0/api-test-runner/scripts/run_tests.py --cases-json <cases.json> [--base-url <url>] [--serve]
```

### browser-use-case-runner 脚本（在被测项目根目录执行，直接 python3）

```bash
# 表格/MD 用例 → JSONL（字段键：id, name, module, priority, preconditions, steps, data, expected, source）
python3 .claude/skills/browser-use-case-runner/scripts/test_cases_export.py xlsx test-data/用例.xlsx -o reports/cases.jsonl

# 生成当轮 run-config（整轮唯一真源，含 sessionStrategy / videoRecording）
python3 .claude/skills/browser-use-case-runner/scripts/generate_run_config.py \
  --jsonl reports/cases.jsonl --source "xlsx:<路径>" \
  --defaults .claude/skills/browser-use-case-runner/runner-config.json
```

### 技能部署（开发目录 → 使用目录）

修改任何技能后，必须重新同步到 `C:\Users\admin\.claude\skills\` 才会生效：

```powershell
powershell -ExecutionPolicy Bypass -File e:\AI\skills\spectest\spectest\sync_skills.ps1
```

⚠️ sync 脚本（及 spectest/README.md）内的 `$SourceDir` 仍指向旧路径 `E:\AI\spectest\spectest`；仓库已迁移到 `e:\AI\skills`，执行前需先确认/更新脚本内路径。

## 架构：两大测试体系的职责边界

### SpecTest（spectest/）— 测试用例设计工作流

9 步顺序流程（plan 可选），状态存放在**目标项目**的 `spectest/changes/<name>/` 目录：

`new`（建目录 + proposal）→ `analysis`（requirements-analysis.md + feature_list.md + api_list.json）→ `plan`（test-plan.md 测试计划，可选）→ `points`（specs/*.md 测试点）→ `generate`（先出 design.md 设计方案，再导出 25 列标准 Excel / XMind）→ `review` → `fix` → `report` → `archive`

- generate 有三种输入源：`from-specs`（测试点转换，先生成 design.md 覆盖矩阵与提纲再展开）、`from-api`（OpenAPI 智能设计）、`from-feature`（功能清单智能设计）
- 核心契约：所有用例走标准 25 列 Excel（列定义见 spectest/CLAUDE.md）；覆盖率目标 正向≥40%、负向≥30%、边界≥20%、安全≥10%

### ApiAutoTest2.0 — 接口测试执行流水线

技能间管道式协作：

`api-doc-generator`（扫 Java/Go/Python/Node 源码出接口文档）→ `api-scenario-generator`（业务场景 JSON）→ `api-test-generator`（转 cases.json + cases.xlsx 双产出）→ `api-test-runner`（pytest 执行 + Allure 报告）→ `api-test-report`（报告服务）；`api-test-config` 辅助维护 config/.env

- 核心契约：cases.json 顶层 `dependencies` + `cases`；每条 case 的 `request` 与 `steps` 互斥（至少其一）；引用协议 `ENV:KEY`、`DEP:dep.field`、`STEP:step.field`（可嵌入字符串如 `Bearer DEP:auth.token`）
- **api-test-runner 只执行不修改**：失败时只输出失败用例 ID、预期 vs 实际、根因判断、修复建议（分高/中/低优先级），禁止自动改断言、请求体、路径参数、依赖引用
- 敏感信息（账号密码）通过环境变量注入，不写入计划文件

### browser-use-case-runner — Web UI 用例执行

首个**跨技能依赖**范例：case-runner 的 CLI 命令契约（`state`/`input`/`click`/`screenshot` 行为）以 sibling skill [browser-use/SKILL.md](browser-use/SKILL.md) 为准，不得臆造未文档化的子命令（如 `browser-use ocr`）。

核心机制：

- **每轮必须生成 `reports/run-config-<UTC>.json`** 作为当轮唯一真源（skill 目录的 `runner-config.json` 仅是 `--defaults` 模板）；整轮执行只读当轮文件
- **会话策略**：登录类套件（启发式推断）默认 `fresh-per-case`（每条前 `close --all` 再 `headed open`）；其他默认 `single-session`（同会话连续执行）
- **执行节奏**：默认遇阻即停（FAIL/BLOCKED/CLI 硬错误/需人工）；PASS 且无未决人工步骤则自动下一条；「逐条停顿」「失败也继续」仅用户显式声明时启用
- **验证码三级兜底**：截图落盘 → 视觉 Agent 识别（须报置信度）→ 停止等人工回复；不得伪造通过或绕过风控
- **留痕默认方式 1**：`videoRecording.enabled=false`，仅关键步骤 + 结论态 `screenshot` 到 `reports/screenshots/`；整屏 ffmpeg 录屏仅用户显式要求时走，且非 browser-use 内置能力
- 每条用例由 Agent 阅读自然语言步骤后驱动浏览器（LLM 驱动，非脚本映射）；`state` 返回的元素索引会跨页变化，禁止硬编码复用旧索引

### miniprogram（miniprogram/）— 微信小程序 UI 自动化

三件套协作：`miniprogram-script-author`（读用例 → 模拟器采 WXML inspect → 逐条生成 Jest describe → 维护 suite.json，**不执行不下结论**）→ `miniprogram-run`（`run-with-reports.sh suite` 逐条执行 + 台账 + Session 报告）+ `miniprogram-shared`（conventions/selectors/脚手架模板）。

- 核心契约：suite.json 是唯一编排源（一模块一文件、一条 TC 一个 describe，`--testNamePattern` 按 id 命中）；无 WXML inspect 依据禁止写选择器；截图必须 `miniProgram.screenshot`（Page 无此 API）
- 报告：`reports/miniprogram-executions.md` 台账 + `miniprogram-report-<sessionId>.md/.html` + 伪 Trace（automator 不支持 Playwright video/trace.zip）

### testflow（testflow/）— 全流程调度

「地图 + 转换器 + 汇总器」，不含测试能力：prd-review → spectest → 三支线执行（3A ApiAutoTest2.0 接口 / 3B browser-use-case-runner Web UI / 3C miniprogram 小程序）→ `aggregate_reports.py` 统一报告（五源：25列 Excel / Allure / UI MD / miniprogram 报告 / Playwright JSON）。3B 与 3C 共用转换器 `convert_25col_to_ui_xlsx.py`（输出 `ui_cases.xlsx` / `mp_cases.xlsx`，8 列格式对两条支线均兼容）。
