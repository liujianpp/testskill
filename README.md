# AI Skills 测试工作区

Claude Code Agent Skills 开发工作区，聚焦**测试领域全生命周期**：需求评审 → 用例设计 → 接口 / Web UI / 小程序三支线执行 → 资产沉淀与主干回归 → 统一报告。

技能在此开发调试，同步到 `C:\Users\admin\.claude\skills\` 后由 Claude Code 实际调用。本仓库同时承载测试资产库 `test-automation/` 与每日回归 CI。

## 目录总览

| 目录 | 定位 |
|------|------|
| [spectest/](spectest/) | **SpecTest 统一测试工作流**（10 技能、9 步流程：new → analysis → plan → points → generate → review → fix → report → archive），产出 25 列标准 Excel / XMind。内含自己的 CLAUDE.md（25 列格式定义、数据库配置） |
| [ApiAutoTest2.0/](ApiAutoTest2.0/) | **接口自动化流水线**（6 技能）：接口文档扫描 → 场景生成 → 用例生成（cases.json/xlsx）→ pytest 执行 + Allure 报告 → 报告服务 |
| [browser-use-case-runner/](browser-use-case-runner/) | **Web UI 用例执行器**：xlsx / MD / 手动用例 → 有头 browser-use 逐条执行 → Markdown 报告（PASS/FAIL/BLOCKED） |
| [miniprogram/](miniprogram/) | **微信小程序 UI 自动化三件套**：script-author 写 Jest 脚本 / run 执行回归 / shared 共享约定（miniprogram-automator + 开发者工具模拟器） |
| [testflow/](testflow/) | **全流程调度器**：需求评审 → 用例设计 → 三支线执行 → 统一报告汇总（五源：25 列 Excel / Allure / UI MD / miniprogram / Playwright JSON） |
| [web-script-author/](web-script-author/) | **界面脚本生成**：25 列 UI 用例 → Playwright spec（采真实 selector，不执行不下结论），产物落 `test-automation/web/` |
| [test-automation/](test-automation/) | **测试资产库**：用例库 cases/ + 接口 pytest + 界面 Playwright + 小程序约定；主干 `main/` × 迭代 `iterations/`，目录即身份；CI 见仓库根 `.github/workflows/regression.yml` |
| [prd-review/](prd-review/) | 测试视角需求评审（可测性 / 边界异常 / 场景状态 / 数据环境 / 阻塞点，支持 pdf/docx/md/txt） |
| [operation-manual/](operation-manual/) | 网站操作手册生成（playwright-cli 浏览器探索 + 截图，默认有头模式） |
| [browser-use/](browser-use/) | browser-use CLI 封装参考（`state`/`input`/`click`/`screenshot` 命令契约；被 case-runner 依赖） |
| [testerarmy-e2e/](testerarmy-e2e/) | 基于开源 [tester-army/e2e](https://github.com/tester-army/e2e) 的五技能 E2E 套件（init → explore-draft → run → fix → report） |
| [opentest1.0.5/](opentest1.0.5/)、[playwright-cli-testcase1.0.1/](playwright-cli-testcase1.0.1/)、[playwright-midscene-skills/](playwright-midscene-skills/) | 历史参考方案（各含「使用说明 + 原文」），OpenTest/Testcase 早期技能已归档至 `spectest/archive/`，不再维护 |
| [docs/](docs/) | 实践计划等文档 |

各主要技能目录均有 `使用说明.md` 可直接查阅。

## 核心架构

```
需求文档 ──► prd-review（测试视角评审）
              │
              ▼
           spectest（9 步用例设计，产出 25 列 Excel）
              │
              ├──► 3A ApiAutoTest2.0 ── 接口执行（pytest + Allure）
              ├──► 3B browser-use-case-runner ── Web UI 执行（有头 browser-use）
              ├──► 3C miniprogram ── 小程序执行（Jest + automator）
              │         （testflow 调度，convert_25col_to_ui_xlsx.py 供 3B/3C 共用）
              ▼
           test-automation（资产沉淀：分拣 promote_cases.py / 晋级 promote_iteration.py）
              │
              ▼
           aggregate_reports.py 统一报告（五源汇总）＋ 每日回归 CI
```

关键契约：

- **SpecTest**：所有用例走标准 25 列 Excel（列定义见 [spectest/CLAUDE.md](spectest/CLAUDE.md)）；覆盖率目标 正向 ≥40%、负向 ≥30%、边界 ≥20%、安全 ≥10%
- **ApiAutoTest2.0**：`request` 与 `steps` 互斥（至少其一）；引用协议 `ENV:KEY` / `DEP:dep.field` / `STEP:step.field`；runner **只执行不修改**，失败仅输出根因与修复建议；账号密码走环境变量
- **browser-use-case-runner**：每轮生成 `run-config-<UTC>.json` 作为唯一真源；遇阻即停（FAIL/BLOCKED/验证码需人工）；验证码三级兜底（截图 → 视觉识别报置信度 → 停止等人工），不得伪造通过
- **两条浏览器工具链勿混用**：`browser-use` CLI（daemon 常驻、按索引操作）用于 UI 测试；`playwright-cli`（snapshot ref）用于操作手册生成

## 常用命令

### spectest 套件脚本（必须用 uv）

```bash
SKILL_DIR="e:/AI/skills/spectest/spectest/<skill-name>"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/<script>.py" [参数]
# SKILL_DIR 赋值与 uv run 必须在同一次 Bash 调用中；首次先 uv sync --project "$SKILL_DIR"
```

### ApiAutoTest2.0（直接 python）

```bash
python ApiAutoTest2.0/api-test-runner/scripts/run_tests.py --cases-json <cases.json> [--base-url <url>] [--serve]
```

### browser-use-case-runner（在被测项目根目录执行）

```bash
python3 .claude/skills/browser-use-case-runner/scripts/test_cases_export.py xlsx test-data/用例.xlsx -o reports/cases.jsonl
python3 .claude/skills/browser-use-case-runner/scripts/generate_run_config.py \
  --jsonl reports/cases.jsonl --source "xlsx:<路径>" \
  --defaults .claude/skills/browser-use-case-runner/runner-config.json
```

### 资产分拣与晋级（test-automation）

```bash
cd test-automation
uv run --with openpyxl python scripts/promote_cases.py --input <25列.xlsx> --version 2026Q4-xxx [--dry-run]
uv run --with openpyxl python scripts/promote_iteration.py --version 2026Q4-xxx [--confirm]
```

## 技能部署（开发目录 → 使用目录）

修改任何技能后，必须重新同步到 `C:\Users\admin\.claude\skills\` 才会生效：

```powershell
powershell -ExecutionPolicy Bypass -File e:\AI\skills\spectest\spectest\sync_skills.ps1
```

> ⚠️ sync 脚本内的 `$SourceDir` 若仍指向旧路径 `E:\AI\spectest\spectest`，执行前需先确认/更新。

## 持续集成

[`.github/workflows/regression.yml`](.github/workflows/regression.yml)：每日 02:17 定时 + 手动触发，跑 `test-automation/` 下接口（pytest main）与界面（Playwright chromium）主干回归，支持 `scope=main|all`。

## 约定

- 每个技能一个独立目录：`SKILL.md`（YAML frontmatter + 工作流正文）+ `scripts/` + `references/` + `templates/`
- frontmatter `description` 包含中文触发词 + 英文 "Use when..." 双语描述
- 中文为主体语言；脚本文件名、API、命令用英文
- 技能间引用用 sibling 相对路径；SKILL.md 中写死的 `.claude/skills/...` 路径指向部署后的使用目录
