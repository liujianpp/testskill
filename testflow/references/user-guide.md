# testflow 使用说明书

> 读者：使用 `/testflow` 命令的**人**。如果你是想了解执行细节的 Agent，请读 [../SKILL.md](../SKILL.md)。
>
> testflow 是「地图 + 转换器 + 汇总器」——它调度 7 大测试技能套件，本身不实现任何测试能力。

---

## 1. testflow 是什么

一句话：**从一份需求文档出发，走完「需求评审 → 用例设计 → 用例执行 → 统一报告」的端到端测试工作流调度器。**

```
阶段0        阶段1        阶段2              阶段3                 阶段4       阶段5
需求预热  →  需求评审  →  用例设计        →  执行（三支线）     →  统一报告  →  归档
(可选)       prd-review   spectest 9步        3A 接口(可选)         汇总脚本     spectest-archive
                                             3B Web UI(默认)
                                             3C 小程序(可选)
```

**默认链路是 1 → 2 → 3B → 4**：评审 → 设计 → UI 执行 → 报告。接口支线（3A）与小程序支线（3C）不自动启动，需要你显式要求。每个阶段结束后会**停下来向你复述结果**，你说继续才走下一阶段——不会一口气跑完全程。

## 2. 前置条件

| 项目 | 要求 | 说明 |
|------|------|------|
| 被测项目 | 一个目录 | 全程产物都写在该项目的 `spectest/changes/<变更名>/` 下 |
| 需求文档 | `.md` / `.txt` / `.pdf` / `.docx` | 阶段 1 的输入；PDF/Word 会自动抽取正文 |
| UI 执行（阶段 3B） | 被测系统 URL + browser-use CLI | 执行前会向你确认 URL 与会话策略；需 `browser-use doctor` 通过 |
| 接口支线（阶段 3A，可选） | 后端源码或接口文档 + pytest + Allure | 仅你显式要求时启动 |
| 小程序支线（阶段 3C，可选） | 微信开发者工具（开启服务端口）+ miniprogram-automator + 自动化仓库脚手架 | 仅你显式声明被测端含微信小程序时启动；账号走 `MP_ACCOUNT`/`MP_PASSWORD` 环境变量 |
| Python 环境 | Python 3.10+，openpyxl | 转换与汇总脚本依赖；缺失时按提示 `pip install` 即可 |

## 3. 快速开始

### 触发方式（三选一）

1. 斜杠命令：`/testflow <需求文档路径>`（如 `/testflow docs/需求-登录改造.md`）
2. 自然语言：「完整测试流程」「从需求到报告」
3. 半路续跑：直接再说一次 `/testflow`——它会扫描产物目录，告诉你已完成到哪、可从哪继续

### 一次最小示例

```
你：   /testflow docs/多彩支支串飞兑换券活动改造.md
Agent: 定位状态目录 → 新建 spectest/changes/duocai-coupon/
       ── 阶段1 需求评审 ──
       （调用 prd-review，产出 5 维评审报告）
       ✅ 评审完成：test-review-report.md，发现 3 个可测性风险
       下一步：进入用例设计？[继续 / 调整 / 停]
你：   继续
Agent: ── 阶段2 用例设计 ──
       （依次调用 spectest-new → analysis → plan(可选) → points → generate → review → fix；
        test-plan.md 与 design.md 自动生成不停等，供事后审阅）
       ✅ 用例就绪：artifacts/duocai-coupon_testcases.xlsx（25列，共 42 条）
       下一步：转 UI 用例并执行？需要被测 URL
你：   https://test.example.com，继续
Agent: ── 阶段3B UI 支线 ──
       转换：42 行 → 导出 38 条（跳过 API 用例 4 条）
       （调用 browser-use-case-runner 逐条有头执行……遇验证码会停下问你）
       ✅ 执行完成：reports/case-run-xxx.md（PASS 30 / FAIL 6 / BLOCKED 2）
       下一步：生成统一报告？
你：   继续
Agent: ── 阶段4 统一报告 ──
       ✅ artifacts/unified-report.md（总览 + 需求覆盖 + 明细 + 风险）
```

## 4. 七阶段：你要提供什么 / 会发生什么 / 产出在哪

### 阶段 0 · 需求预热（可选，多数情况跳过）

- **何时用**：手里只有后端源码、没有需求文档时，先扫出接口文档垫底
- **你提供**：源码路径 / 模块范围
- **产出**：接口文档（目标项目 `docs/` 下）

### 阶段 1 · 需求评审

- **你提供**：需求文档路径（或直接粘贴正文）
- **会发生**：prd-review 从测试视角按 5 维度（可测性、边界异常、场景状态、数据环境、阻塞点）评审；报告路径会被登记到 proposal
- **产出**：Markdown 评审报告
- **确认点**：评审完成后复述发现的风险，你决定是否带着意见进入设计

### 阶段 2 · 用例设计

- **你提供**：变更名（或采用默认）；后续基本只需按阶段确认
- **会发生**：spectest 六步依次执行（新建变更目录 → 需求分析 → 测试点 → 生成 25 列 Excel → 评审 → 修复）；report/archive 两步由本流程的阶段 4/5 承接
- **产出**：`artifacts/<变更名>_testcases.xlsx`（标准 25 列，Sheet「测试用例」）
- **关键机制**：25 列中「API URL」列非空的行会被识别为 API 用例——它们留给接口支线，不进入 UI 执行

### 阶段 3B · UI 执行（默认支线）

- **你提供**：被测 URL；会话策略（登录类套件默认每条重启浏览器，其他默认同一会话连续执行——Agent 会问你）
- **会发生**：先转换（25 列 → runner 8 列 `ui_cases.xlsx`），再由 browser-use-case-runner 有头浏览器逐条执行；**遇 FAIL/BLOCKED/验证码/需人工即停**，不会伪造通过
- **产出**：`artifacts/ui_cases.xlsx` + `reports/case-run-*.md` + `reports/screenshots/`
- **验证码约定**：截图落盘 → 视觉识别（附置信度）→ 停下等你回复验证码字符串

### 阶段 3A · 接口执行（可选支线）

- **何时用**：你显式说「要做接口自动化」，或项目有后端源码且你同意
- **你提供**：源码/接口文档范围；环境信息（账号密码走环境变量，不写进文件）
- **会发生**：api-doc-generator → api-scenario-generator → api-test-generator → api-test-runner 依次执行；**runner 只执行不修改**——失败只给修复建议，不会自动改断言或请求体
- **产出**：目标项目 `docs/` 下的 scenario/cases 文件 + Allure 报告；allure-results 路径登记到 `artifacts/api/`

### 阶段 3C · 小程序执行（可选支线）

- **何时用**：被测端含微信小程序——你显式声明，或需求/用例明确指向小程序端且你同意 Agent 的提议
- **你提供**：首次使用时的一次性环境——在目标项目根跑脚手架（`scaffold.sh`）、编辑 `miniprogram.local.config`（小程序工程路径 + 本机微信开发者工具 CLI 路径或 wsEndpoint；Windows 的 CLI 路径以本机安装为准）、装 npm 依赖、设 `MP_ACCOUNT`/`MP_PASSWORD`
- **会发生**：先转换（25 列 → `mp_cases.xlsx`，与 UI 支线同一转换器），再由 miniprogram 三件套接管——script-author 在模拟器采 WXML 快照后逐条生成 Jest 脚本并维护 suite.json，run 逐条执行回归；**写脚本的技能不下 PASS/FAIL 结论，结果只认执行报告**
- **产出**：`artifacts/mp_cases.xlsx` + `miniprogram/tests/<模块>/*.spec.js` + `suite.json` + `reports/miniprogram-report-<sessionId>.md/.html`（含伪 Trace 证据链）；报告路径登记到 `artifacts/mp/`

### 阶段 4 · 统一报告

- **你提供**：无需额外输入（若走了 3A/3C，确认 allure / 小程序报告路径）
- **会发生**：汇总五源——25 列 Excel 执行结果列、Allure 结果、UI 执行报告、小程序执行报告、Playwright JSON 结果 → 一份 `unified-report.md`，含四节：执行总览（通过率 = 通过/(通过+失败)，阻塞/未执行单列不进分母）/ 需求覆盖对照 / 四支线明细 / 风险与建议
- **产出**：`artifacts/unified-report.md`

### 阶段 5 · 归档（收尾）

- **你提供**：确认归档；（可选）要不要顺手生成系统操作手册
- **产出**：归档目录；手册（可选，走 operation-manual）

## 5. 中断与恢复

任何时候都可以停（直接关对话也行）。再次 `/testflow` 时按**产物存在性**判断进度：

| 已存在的产物 | 说明 |
|---|---|
| `artifacts/*_testcases.xlsx` | 阶段 2 已完成 |
| `artifacts/ui_cases.xlsx` | 阶段 3B 转换已完成 |
| `reports/case-run-*.md` | 阶段 3B 已执行 |
| `artifacts/api/` 下有说明文件（如 allure_path.txt） | 阶段 3A 已执行 |
| `artifacts/mp_cases.xlsx` | 阶段 3C 转换已完成 |
| `miniprogram/suite.json` 有 cases 且 `artifacts/mp/` 有说明文件 | 阶段 3C 已执行 |
| `artifacts/unified-report.md` | 阶段 4 已完成 |

无需记状态文件——Agent 会扫描目录并复述「已完成阶段 X，可从 X+1 继续」。

## 6. 产物清单

```
<被测项目>/spectest/changes/<变更名>/
├── proposal.md                  # 变更提案（阶段1 评审报告路径附于此）
├── project_info/                # 需求分析产物（功能清单、API 清单）
├── specs/                       # 测试点文件
├── artifacts/
│   ├── <变更名>_testcases.xlsx  # ★ 25 列标准用例（三支线源头）
│   ├── ui_cases.xlsx            # UI 执行入口（转换器输出）
│   ├── mp_cases.xlsx            # 小程序执行入口（同一转换器输出）
│   ├── api/                     # 接口支线记录（allure 路径等）
│   ├── mp/                      # 小程序支线记录（报告路径等）
│   └── unified-report.md        # ★ 统一报告
└── db_info/                     # DB 断言配置（接口支线用）
```

另有两类运行期产物在被测项目根目录：`reports/`（UI 执行报告与截图；小程序支线的 Session 报告与伪 Trace 也在此）与 `docs/`（接口支线的 scenario/cases 文件）。

## 7. FAQ

**Q1：接口支线（3A）什么时候会跑？**
默认永远不自动跑。两种启动方式：对话中明确说「这个项目要做接口自动化」；或 Agent 发现有后端源码、征得你同意后启动。

**Q1b：小程序支线（3C）什么时候会跑？**
与 3A 同样的门控：对话中明确说「被测端是/含微信小程序」；或需求与用例明显指向小程序端、Agent 提议并经你同意。首次使用需要一次性环境准备（脚手架、开发者工具 CLI 路径、账号环境变量），Agent 会逐步引导。

**Q1c：Web UI（3B）和小程序（3C）能都跑吗？**
能。两者从同一份 25 列用例各自转换（`ui_cases.xlsx` / `mp_cases.xlsx`）分别执行——同一批功能用例在两个端各验证一遍，结果在统一报告分列展示，互不干扰。

**Q2：执行中遇到验证码怎么办？**
Agent 会截图 → 尝试视觉识别（会告诉你置信度）→ 停下来等你在对话里回复验证码。你也可以说「跳过本条」或「刷新再截」。**不会**绕过风控或伪造通过。

**Q3：转换后导出 0 行？**
说明 25 列用例全是 API 用例（「API URL」列全非空）或全被过滤。Agent 会停下来与你核对，而不是硬跑空批次。

**Q4：统一报告显示「UI 报告未生成」但我明明跑了 UI？**
汇总器找不到你给的 `--ui-report` 路径时会静默跳过该节。把 `reports/case-run-*.md` 的正确路径告诉 Agent 重新汇总即可。

**Q5：UI 执行到一半失败了，前面跑过的还算数吗？**
算。每条用例的结论在执行时就写入了 `case-run-*.md`，中断前的结果都在；统一报告会如实反映，失败/阻塞不会被隐藏。

**Q6：我能只用其中某个阶段吗？**
能。各套件本身独立可用：单独 `/spectest-generate`、单独跑 `api-test-runner`、单独 `/prd-review` 都没问题。testflow 只是帮你把它们按正确顺序串起来。

## 8. 附录：testflow 与 7 大套件的分工

| 套件 | 在流程中的角色 | 脱离 testflow 单用 |
|------|--------------|-------------------|
| prd-review | 阶段 1 需求评审 | ✅ `/prd-review` |
| spectest（8 技能） | 阶段 2 用例设计主轴 | ✅ 各技能独立可触发 |
| ApiAutoTest2.0（6 技能） | 阶段 3A 接口执行管道 | ✅ 管道独立可用 |
| browser-use-case-runner | 阶段 3B UI 执行 | ✅ 直接给它 xlsx/MD 用例 |
| browser-use | 3B 的底层浏览器 CLI | ✅（一般不直接用） |
| miniprogram（三件套） | 阶段 3C 小程序执行（script-author 写脚本 + run 执行） | ✅ 按其 SKILL.md 独立使用 |
| operation-manual | 阶段 5 可选手册 | ✅ `/operation-manual` |

testflow 自身新增的只有三样：**调度文档**（SKILL.md + workflow-map.md）、**转换器**（25列→runner 8列，3B/3C 共用）、**汇总器**（五源→统一报告：25列/Allure/UI/小程序/Playwright）。两条链路（需求驱动的 spectest、代码驱动的 ApiAutoTest）始终保持独立，仅在统一报告处汇合——不做用例级互转。
