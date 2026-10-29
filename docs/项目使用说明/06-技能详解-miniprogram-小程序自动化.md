# 06 · 技能详解：miniprogram（微信小程序 UI 自动化三件套）

> **一句话**：把小程序用例变成 **Jest 自动化脚本**并在微信开发者工具模拟器里逐条执行，出执行报告。技术栈：miniprogram-automator + 微信开发者工具模拟器 + Jest。

[← 返回总导读](README.md) | 套件自带文档：[miniprogram/使用说明.md](../../miniprogram/使用说明.md)

---

## 1. 三个技能的职责

| 技能 | 职责 | 产出 | 不做 |
|------|------|------|------|
| `miniprogram-script-author` | 读用例（Excel/MD/XMind/文本）→ 模拟器采 WXML 快照 → 逐条生成 Jest 脚本 → 维护 suite.json | `miniprogram/tests/<模块>/<模块>.spec.js`、`miniprogram/suite.json`、`miniprogram/inspect/run-<RunId>/*.wxml` | **不执行**、不下 PASS/FAIL 结论 |
| `miniprogram-run` | 逐条执行既有 spec，写台账与 Session 报告 | `reports/miniprogram-executions.md`（台账）、`reports/miniprogram-report-<sessionId>.md/.html`、artifacts | 不从零写用例 spec |
| `miniprogram-shared` | 纯共享层：仓库约定、选择器规则、脚手架、模板、本机配置 | 脚手架与规范文档 | — |

> ⚠️ 两个执行型技能设了「禁止自动触发」，**必须显式调用**：`@miniprogram-script-author` / `@miniprogram-run`。

## 2. 两步工作流

```
@miniprogram-script-author（探索 + 写 spec + 维护 suite）
        │  交付时注明「待 @miniprogram-run 校验」
        ▼
@miniprogram-run（suite 逐条执行 + 台账 + 伪 Trace + Session 报告）
        │  失败时：读 artifacts 日志定位，修订 spec 交回 script-author（至多重试 2 次）
        ▼
   循环直至全绿
```

## 3. 首次使用：安装与初始化（6 步，一次性）

1. **放置技能**：三个技能目录放到 `<项目>/.cursor/skills/`（或 `.claude/skills/`），三者须同级；
2. **脚手架**：在小程序**自动化仓库根**执行：
   ```bash
   bash <skills-root>/miniprogram-shared/scaffold.sh .
   ```
   （生成 scripts/、miniprogram/tests/、空 suite.json 等）
3. **配置**：复制 `miniprogram.local.config.example` → `miniprogram.local.config`，填写：
   - `projectPath`：小程序工程路径（必填）
   - `cliPath`：微信开发者工具 CLI 路径（必填，或改用 `wsEndpoint`）
   - ⚠️ **Windows 注意**：cliPath 必须是**本机真实安装路径**（文档示例的 macOS 路径不可用），且需在开发者工具中**开启服务端口**
   - 此文件不入 Git、禁止臆造路径
4. **依赖**（仓库根）：`npm install --save-dev jest@^29.7.0 miniprogram-automator@^0.12.1 xlsx@^0.18.5`
5. **凭据**：设 `MP_ACCOUNT` / `MP_PASSWORD`（可选 `MP_ID_CARD`）环境变量
6. **开发者工具**：开启服务端口并 `cli auto`（或配置 `wsEndpoint` 连接已打开的工具）

## 4. 你的仓库会变成什么样

```
<自动化仓库根>/
├── scripts/                        # 脚手架拷贝（launch / capture-wxml / parse-testcases）
├── miniprogram/
│   ├── suite.json                  # ★ 唯一编排源（cases[] 按 order 排序）
│   ├── tests/<模块>/<模块>.spec.js  # 一模块一文件；一条用例一个顶层 describe（名字以用例 ID 开头）
│   ├── tests/helpers/              # auth.js（登录）、trace.js、screenshot.js
│   ├── inspect/run-<RunId>/        # WXML 快照（写 spec 的唯一依据）
│   └── probes/run-<RunId>/         # 导航探针
└── reports/
    ├── miniprogram-executions.md   # 跨 Session 累积台账
    ├── miniprogram-report-<sessionId>.md / .html
    └── artifacts/<sessionId>/<caseKey>/{jest-results.json, console.log, screenshot.png?, trace/}
```

## 5. 两个技能的要点

### 5.1 miniprogram-script-author（写脚本）

- **交错快照**（Act → Snapshot → Write）：界面每次有意义变化就采 WXML 落盘，再照着快照写脚本；**禁止没对照快照就写选择器和断言**；
- **一条一闭环**：每条用例独立走「解析 → 补采缺口 → 写 describe → 更新 suite.json」再下一条；
- 用例输入：Excel 用 `node scripts/parse-testcases.js --input cases.xlsx --out cases.json`；每条须含 `id/title/order/steps/expected`；
- 反模式禁令：禁止一条用例一文件、禁止并行 automator、业务用例不许每条重新登录、禁止仅凭 Excel 写选择器；
- 探索完还缺材料 → **不落盘可执行脚本**，输出阻塞原因和缺失清单，不虚构路径。

### 5.2 miniprogram-run（执行）

```bash
<skills-root>/miniprogram-run/run-with-reports.sh <子命令> [参数]
```

| 子命令 | 用途 |
|--------|------|
| `suite` | 按 suite.json 逐条跑（`--testNamePattern` 按用例 ID 命中 describe）；默认失败后继续 |
| `suite --from TC-MP-003` | 从该条续跑（新开 Session） |
| `single <spec.js>` | 跑整个模块文件（调试用） |

可调配置（`miniprogram-run.config`）：`RECORD_TRACE=true`（伪 Trace，默认开）、`RECORD_SCREENSHOT=false`、`OPEN_HTML=true`、`STOP_ON_FAIL=false`。

失败排查：读 `artifacts/<session>/<caseKey>/` 的 console.log、jest-results.json、trace/viewer.html。

## 6. 选择器铁律（为什么它总要「先看再写」）

1. 每个关键页必须有 **WXML 快照依据**（禁止仅凭 Excel/口头步骤写选择器）；
2. 优先级：`id` / `data-*` > 快照核对过的 class > `$$()` 文本过滤兜底 > 禁止纯坐标；
3. **自定义组件内的元素必须先 `page.$('组件')` 再 `.inner`**（`page.$()` 不能跨组件）；
4. 动态列表用 `$$()` 遍历 + 文本过滤。

## 7. 已知限制（提前知道不踩坑）

- miniprogram-automator **不支持** Playwright 级 video/trace.zip → 用**伪 Trace**（步骤 meta + WXML + 尽力截图 + viewer.html）当证据链；
- 截图只能 `miniProgram.screenshot`（Page 没有此 API，仅模拟器可用）；
- 无日志依据不得宣称 PASS。

## 8. 使用话术

**场景 1：从用例表生成脚本**
> 「@miniprogram-script-author 按 artifacts/mp_cases.xlsx 生成小程序测试脚本」

**场景 2：执行**
> 「@miniprogram-run 执行 suite 全部用例并出报告」

**场景 3：失败了修复**
> 「读 artifacts 里的失败日志，定位后修订 spec」（修订必须交回 script-author，至多重试 2 次）

**场景 4：在 testflow 里**（3C 支线，说一句即可自动接管）
> 「跑一次完整 testflow，需求文档 docs/PRD.pdf，包含微信小程序端」

## 9. 和其他技能的关系

- 上游：testflow 转换器把 25 列转成 `mp_cases.xlsx`（8 列与 `parse-testcases.js` 表头兼容，无需再转）；
- 用例 ID 沿用 25 列「测试项/测试点」，报告可对齐追溯；
- 报告（台账或 Session 报告）被 testflow 阶段 4 汇总。

---

*本册基于 miniprogram 三件套 2026-10-29 现状整理。*
