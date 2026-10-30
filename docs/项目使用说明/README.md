# AI Skills 测试工作区 · 项目使用说明（总导读）

> **本文读者**：完全没接触过本项目的测试新人 / 第一次使用 AI 技能的小白。
> **这套文档的目的**：让你搞懂这个项目是什么、里面**每一个技能**是干什么的、什么场景用哪个、怎么组合使用，并且每一册都给你**可以直接照抄的对 Claude 说的话术**。
> **最后更新**：2026-10-29

---

## 0. 这套文档怎么读

| 你是谁 / 你想要什么 | 建议读法 |
|---|---|
| 纯小白，第一次接触 | 顺序读：本页 → [01-快速上手](01-快速上手-第一次使用.md) → [12-组合使用与实战场景](12-组合使用与实战场景.md) |
| 想了解某个具体技能 | 直接跳对应分册（见下面目录） |
| 不知道自己该用哪个技能 | 看本页 [§5 场景速查表](#5-场景速查表我该用什么) |
| 遇到问题 | 先查本页 [§6 FAQ](#6-常见问题-faq速查版详见各分册)，再查对应分册 |
| 想看术语解释 | 本页 [§7 小白术语表](#7-小白术语表) |

## 1. 文档目录（18 册）

| 分册 | 内容 | 适合什么时候看 |
|---|---|---|
| **本页（README）** | 项目总览、技能全家福、速查表、FAQ、术语表 | 随时 |
| [01-快速上手-第一次使用](01-快速上手-第一次使用.md) | 装什么软件、两个目录的概念、技能部署同步、怎么触发技能、第一次跑通 | 第一次使用前**必读** |
| [02-技能详解-prd-review-需求评审](02-技能详解-prd-review-需求评审.md) | 需求评审技能（5 维度评审 PRD） | 拿到需求文档时 |
| [03-技能详解-spectest-用例设计](03-技能详解-spectest-用例设计.md) | 用例设计工作流 **10 个技能**（9 步流程 + 格式转换） | 要写测试用例时 |
| [04-技能详解-ApiAutoTest2.0-接口自动化](04-技能详解-ApiAutoTest2.0-接口自动化.md) | 接口自动化 **6 个技能**（源码→文档→场景→用例→执行→报告） | 做接口测试时 |
| [05-技能详解-browser-use与case-runner-WebUI执行](05-技能详解-browser-use与case-runner-WebUI执行.md) | Web UI 执行 **2 个技能**（浏览器命令手册 + 用例执行器） | 在网页上执行用例时 |
| [06-技能详解-miniprogram-小程序自动化](06-技能详解-miniprogram-小程序自动化.md) | 微信小程序自动化 **3 个技能**（写脚本/执行/共享约定） | 测微信小程序时 |
| [07-技能详解-web-script-author-界面脚本生成](07-技能详解-web-script-author-界面脚本生成.md) | 25 列用例 → Playwright 永久回归脚本 | 想把用例沉淀为自动化时 |
| [08-技能详解-operation-manual-操作手册生成](08-技能详解-operation-manual-操作手册生成.md) | 网站 → 带截图的操作手册 | 要写用户手册时 |
| [09-技能详解-testerarmy-e2e-探索式E2E](09-技能详解-testerarmy-e2e-探索式E2E.md) | 开源 E2E 框架 **5 个技能**（init/探索/执行/修复/报告） | 想试 AI 自主探索测试时 |
| [10-技能详解-test-automation-资产库与CI](10-技能详解-test-automation-资产库与CI.md) | 测试资产库（不是技能，是沉淀仓库）+ 每日回归 CI | 管理用例/脚本资产时 |
| [11-技能详解-testflow-全流程调度](11-技能详解-testflow-全流程调度.md) | 全流程总指挥（把所有技能串成一条链） | 想一条龙跑完时 |
| [12-组合使用与实战场景](12-组合使用与实战场景.md) | 组合方式、6 个完整实操 walkthrough、产出消费关系 | **重点推荐**，教你怎么串着用 |
| [13-历史参考方案](13-历史参考方案.md) | 归档存档说明 + 全家演化图（各套件详解已拆至 14~16 册） | 了解历史时 |
| [14-技能详解-playwright-cli-testcase-探索式用例生成](14-技能详解-playwright-cli-testcase-探索式用例生成.md) | 探索式用例生成（1 技能）：给网址就探索界面出用例（10 列 Excel/XMind） | 没有需求文档、想对照真实界面出用例 |
| [15-技能详解-playwright-midscene-混合UI自动化](15-技能详解-playwright-midscene-混合UI自动化.md) | Playwright+Midscene 代码化 UI 自动化 **4 个技能**（难定位元素有视觉兜底，可进 CI） | 界面含 Canvas/Shadow DOM/验证码、要进 CI |
| [16-技能详解-opentest-用例设计工作流](16-技能详解-opentest-用例设计工作流.md) | OpenTest 1.0.5（spectest 前身，**7 个技能**，遗留项目维护用） | 维护旧 opentest 项目、了解演化 |
| [17-技能详解-seed-test-data-测试造数](17-技能详解-seed-test-data-测试造数.md) | 测试造数：接口文档/HAR/curl/表结构 → Postman/SQL(含回滚)/Excel/Python 造数文件 | 执行前准备测试数据时 |

---

## 2. 这个项目是什么（先搞懂 3 个概念）

### 2.1 一句话介绍

这是一个 **「AI 测试技能仓库」**：把测试人员的完整工作流（需求评审 → 设计用例 → 造数 → 执行测试 → 出报告 → 沉淀资产）做成了 **30 个主线 AI 技能**（分属 10 个套件）+ **1 个造数技能（seed-test-data）**，外加 **12 个可选/历史套件技能**（playwright-cli-testcase、playwright-midscene 四件套、opentest 七件套，见 14～16 册），交给 Claude Code 这个 AI 助手自动完成。

### 2.2 三个基础概念

**概念一：Claude Code 是什么？**

一个 AI 助手工具（命令行版 / VSCode 插件版 / 桌面版）。它会读文件、写文件、跑脚本、操控浏览器——相当于一个能动手干活的 AI 同事。你在对话框里用**自然语言**（中文大白话）告诉它要做什么，它就去干。

**概念二：「技能（Skill）」是什么？**

技能 = 一份写给 AI 看的**标准作业流程说明书**。每个技能是一个文件夹，核心是 `SKILL.md` 文件（内含触发词 + 工作步骤 + 产物格式）。Claude 读到说明书后，就「学会」按固定流程、固定格式干活。

> 打个比方：Claude 像一个聪明但没受过训的新员工，技能就像你递给他的《岗位 SOP 手册》。他照手册做，产出就规范、稳定。

**概念三：这个仓库的角色**

- 这里是技能的**开发调试车间**（改技能、调试都在这）；
- 技能要**复制（部署）到 `C:\Users\admin\.claude\skills\`** 后，Claude Code 才会真正加载（详见 [01-快速上手](01-快速上手-第一次使用.md)）；
- 仓库里还住着：**测试资产库** `test-automation/`（用例和自动化脚本长期存放地）和**每日自动回归 CI**。

### 2.3 整体架构一张图

```
需求文档 ──► prd-review（测试视角评审）
              │
              ▼
           spectest（9 步用例设计，产出 25 列标准 Excel）
              │
              ├──► 3A ApiAutoTest2.0 ── 接口执行（pytest + Allure）
              ├──► 3B browser-use-case-runner ── Web UI 执行（有头浏览器）
              ├──► 3C miniprogram ── 小程序执行（Jest + 微信开发者工具）
              │         （testflow 负责调度以上全流程）
              ▼
           test-automation（资产沉淀：主干 main/ 迭代 iterations/）
              │
              ▼
           统一报告汇总（五源合一）＋ 每日回归 CI
```

大白话：**你给一份需求文档，AI 帮你评审需求、设计出标准格式的测试用例表，然后自动在真实系统上执行（网页点一点 / 调接口 / 跑小程序），最后汇总成一份测试报告，并把有价值的用例沉淀下来供以后每天自动回归。**

---

## 3. 技能全家福（所有技能一张表）

> 共 **30 个主线在用技能**（10 套件）+ **1 个独立造数技能**（[17 册](17-技能详解-seed-test-data-测试造数.md)）+ **12 个可选/历史套件技能**（14～16 册详解）。详细用法点对应分册。

### 3.1 核心流程套件（12 个技能）

| # | 技能 | 所属套件 | 一句话职责 | 分册 |
|---|------|---------|-----------|------|
| 1 | `prd-review` | prd-review | 从测试视角按 5 维度评审需求文档，出评审报告 | [02](02-技能详解-prd-review-需求评审.md) |
| 2 | `spectest-new` | spectest | 第 1 步：创建测试变更目录 + 立项提案 | [03](03-技能详解-spectest-用例设计.md) |
| 3 | `spectest-analysis` | spectest | 第 2 步：智能需求分析（需求拆解/功能清单/API 清单） | [03](03-技能详解-spectest-用例设计.md) |
| 4 | `spectest-plan` | spectest | 第 3 步（可选）：测试计划（范围/策略/人天/进度） | [03](03-技能详解-spectest-用例设计.md) |
| 5 | `spectest-points` | spectest | 第 4 步：按等价类/边界值/场景法/错误推测推导测试点 | [03](03-技能详解-spectest-用例设计.md) |
| 6 | `spectest-generate` | spectest | 第 5 步：测试点 → 用例设计方案 → 25 列 Excel / XMind | [03](03-技能详解-spectest-用例设计.md) |
| 7 | `spectest-review` | spectest | 第 6 步：评审用例质量与覆盖率 | [03](03-技能详解-spectest-用例设计.md) |
| 8 | `spectest-fix` | spectest | 第 7 步：按评审意见自动修复用例 | [03](03-技能详解-spectest-用例设计.md) |
| 9 | `spectest-report` | spectest | 第 8 步：生成测试执行报告 | [03](03-技能详解-spectest-用例设计.md) |
| 10 | `spectest-archive` | spectest | 第 9 步：归档整个测试变更 | [03](03-技能详解-spectest-用例设计.md) |
| 11 | `spectest-convert` | spectest | 附：测试用例格式转换（Excel/XMind/Markdown 互转） | [03](03-技能详解-spectest-用例设计.md) |
| 12 | `testflow` | testflow | 全流程调度器：把所有环节串成一条链 | [11](11-技能详解-testflow-全流程调度.md) |

### 3.2 三支线执行套件（11 个技能）

| # | 技能 | 所属套件 | 一句话职责 | 分册 |
|---|------|---------|-----------|------|
| 13 | `api-doc-generator` | ApiAutoTest2.0 | 扫 Java/Go/Python/Node 源码 → 接口文档（JSON/MD） | [04](04-技能详解-ApiAutoTest2.0-接口自动化.md) |
| 14 | `api-scenario-generator` | ApiAutoTest2.0 | 接口文档 → 业务场景设计（JSON + Excel 评审表） | [04](04-技能详解-ApiAutoTest2.0-接口自动化.md) |
| 15 | `api-test-generator` | ApiAutoTest2.0 | 场景 → 可执行用例（cases.json + cases.xlsx） | [04](04-技能详解-ApiAutoTest2.0-接口自动化.md) |
| 16 | `api-test-runner` | ApiAutoTest2.0 | 执行 cases.json（pytest + Allure）；**只执行不修改** | [04](04-技能详解-ApiAutoTest2.0-接口自动化.md) |
| 17 | `api-test-report` | ApiAutoTest2.0 | 从 allure-results 生成/打开 Allure 报告 | [04](04-技能详解-ApiAutoTest2.0-接口自动化.md) |
| 18 | `api-test-config` | ApiAutoTest2.0 | 维护 config/.env（前置依赖变量 + DB 断言模板） | [04](04-技能详解-ApiAutoTest2.0-接口自动化.md) |
| 19 | `browser-use-case-runner` | 独立 | xlsx/MD/手动用例 → 有头浏览器逐条执行 → MD 报告+截图 | [05](05-技能详解-browser-use与case-runner-WebUI执行.md) |
| 20 | `browser-use` | 独立 | 浏览器自动化 CLI 命令手册（case-runner 的底层依赖） | [05](05-技能详解-browser-use与case-runner-WebUI执行.md) |
| 21 | `miniprogram-script-author` | miniprogram | 读用例 → 模拟器采 WXML → 逐条生成 Jest 脚本（不执行） | [06](06-技能详解-miniprogram-小程序自动化.md) |
| 22 | `miniprogram-run` | miniprogram | 逐条执行 spec + 台账 + Session 报告（结论只认它） | [06](06-技能详解-miniprogram-小程序自动化.md) |
| 23 | `miniprogram-shared` | miniprogram | 共享约定层（选择器铁律/脚手架/模板，幕后支撑） | [06](06-技能详解-miniprogram-小程序自动化.md) |

### 3.3 资产生成与独立工具（8 个技能）

| # | 技能 | 所属套件 | 一句话职责 | 分册 |
|---|------|---------|-----------|------|
| 24 | `web-script-author` | 独立 | 25 列 UI 用例 → Playwright 脚本（采真实 selector，不执行） | [07](07-技能详解-web-script-author-界面脚本生成.md) |
| 25 | `operation-manual` | 独立 | 网站 URL → 带截图的 Markdown 操作手册 | [08](08-技能详解-operation-manual-操作手册生成.md) |
| 26 | `e2e-init` | testerarmy-e2e | 初始化 E2E 脚手架（选引擎/厂商，写配置，停下等你填 Key） | [09](09-技能详解-testerarmy-e2e-探索式E2E.md) |
| 27 | `e2e-explore-draft` | testerarmy-e2e | 需求/用例/URL → charter → AI 探索 → 落草稿脚本 | [09](09-技能详解-testerarmy-e2e-探索式E2E.md) |
| 28 | `e2e-run` | testerarmy-e2e | 执行指定测试文件，出 MD+HTML 报告 | [09](09-技能详解-testerarmy-e2e-探索式E2E.md) |
| 29 | `e2e-fix` | testerarmy-e2e | 按失败报告修复脚本与定位器（同一失败点最多 2 轮） | [09](09-技能详解-testerarmy-e2e-探索式E2E.md) |
| 30 | `e2e-report` | testerarmy-e2e | 从 report.json 生成 MD + 单文件 HTML 报告 | [09](09-技能详解-testerarmy-e2e-探索式E2E.md) |
| 31 | `seed-test-data` | 独立 | 测试造数：接口文档/HAR/curl/表结构 → Postman / SQL(含回滚) / Excel / Python 造数文件；只出文件不执行 | [17](17-技能详解-seed-test-data-测试造数.md) |

### 3.4 非技能成员（但很重要）

| 成员 | 角色 | 分册 |
|------|------|------|
| `test-automation/` | 测试资产库（用例库+脚本库+每日回归 CI），**不是技能是仓库** | [10](10-技能详解-test-automation-资产库与CI.md) |
| `graphify-out/` | graphify 技能（`/graphify`，全局安装）的知识图谱产物，与测试流程无关 | 本页 §6 Q7 |

### 3.5 可选独立套件（5 个技能，部署可用、不在 testflow 主链）

| # | 技能 | 所属套件 | 一句话职责 | 分册 |
|---|------|---------|-----------|------|
| 31 | `playwright-cli-testcase` | 独立 | 给 URL 探索真实界面 → 测试点计划（须确认）→ 10 列用例 Excel/XMind | [14](14-技能详解-playwright-cli-testcase-探索式用例生成.md) |
| 32 | `00-playwright-explore-plan` | playwright-midscene-skills | 有头探索界面 → 探索报告（用例矩阵+每步 driver） | [15](15-技能详解-playwright-midscene-混合UI自动化.md) |
| 33 | `01-playwright-gen-code` | playwright-midscene-skills | 按探索报告生成测试代码（Playwright 为主 + Midscene 混入） | [15](15-技能详解-playwright-midscene-混合UI自动化.md) |
| 34 | `02-playwright-run-report` | playwright-midscene-skills | 无头执行 + HTML 报告 + 合规校验 | [15](15-技能详解-playwright-midscene-混合UI自动化.md) |
| 35 | `03-playwright-heal` | playwright-midscene-skills | 修复失败用例（Playwright 步修 locator / Midscene 步改 prompt），最多 2 轮 | [15](15-技能详解-playwright-midscene-混合UI自动化.md) |

### 3.6 历史前身套件（7 个技能，已整合进 spectest，独立分册详解）

| # | 技能 | 所属套件 | 一句话职责 | 分册 |
|---|------|---------|-----------|------|
| 36 | `opentest-new` | opentest1.0.5 | 新建变更目录 + 测试提案 | [16](16-技能详解-opentest-用例设计工作流.md) |
| 37 | `opentest-analysis` | opentest1.0.5 | 需求分析（pdf/docx/md/txt） | [16](16-技能详解-opentest-用例设计工作流.md) |
| 38 | `opentest-plan` | opentest1.0.5 | 测试计划（范围/策略/人天/进度） | [16](16-技能详解-opentest-用例设计工作流.md) |
| 39 | `opentest-points` | opentest1.0.5 | 测试点推导（specs/testpoints.md） | [16](16-技能详解-opentest-用例设计工作流.md) |
| 40 | `opentest-generate` | opentest1.0.5 | 生成用例（design.md → Excel/XMind） | [16](16-技能详解-opentest-用例设计工作流.md) |
| 41 | `opentest-report` | opentest1.0.5 | 从 Excel「执行结果」列汇总报告 | [16](16-技能详解-opentest-用例设计工作流.md) |
| 42 | `opentest-archive` | opentest1.0.5 | 归档变更 | [16](16-技能详解-opentest-用例设计工作流.md) |

更早的原始存档（`spectest/archive/` 下 OpenTest/Testcase 技能）见 [13-历史参考方案](13-历史参考方案.md)。

---

## 4. 仓库目录地图

```
E:\AI\skills\
├── README.md / CLAUDE.md          # 项目自述与开发规范（开发者向）
├── docs\                          # 文档（本套说明 + AI 自动化实践计划）
│   └── 项目使用说明\               # ★ 你正在读的这套文档（14 册）
│
├── prd-review\                    # 需求评审技能
├── spectest\                      # 用例设计套件（10 技能；内含自己的 CLAUDE.md 与 archive/）
├── testflow\                      # 全流程调度器
├── ApiAutoTest2.0\                # 接口自动化套件（6 技能）
├── browser-use-case-runner\       # Web UI 用例执行器
├── browser-use\                   # browser-use CLI 命令参考
├── miniprogram\                   # 小程序三件套
├── web-script-author\             # 界面脚本生成
├── operation-manual\              # 操作手册生成
├── seed-test-data\                # 测试造数（17 册）
├── testerarmy-e2e\                # 探索式 E2E 五件套
├── test-automation\               # 测试资产库（CI 在仓库根 .github/workflows/）
│
├── opentest1.0.5\                          # spectest 前身（16 册，遗留项目用）
├── playwright-cli-testcase1.0.1\ 、playwright-midscene-skills\   # 可选独立套件（14/15 册）
└── graphify-out\                  # 知识图谱产物（可忽略）
```

**每个主要技能目录里都有自带的《使用说明.md》**（面向该套件的进阶细节）。本套文档与它们互补：本套面向小白讲「怎么用、怎么组合」，套件文档讲「该套件内部的技术契约」。

---

## 5. 场景速查表：我该用什么

| 你现在的处境 | 想要的结果 | 用什么 | 对 Claude 说（示例） | 详见 |
|--------------|-----------|--------|---------------------|------|
| 拿到 PRD | 挑出需求的坑 | prd-review | 「测试视角评审 docs/PRD.pdf」 | 02 |
| 拿到 PRD | 规范测试用例 | spectest | 「/spectest-new 创建变更 xxx」后按 9 步走 | 03 |
| 拿到 PRD | 评审+用例+执行+报告全要 | **testflow** | 「跑完整 testflow，需求在…，地址…」 | 11、12 |
| 只有后端源码 | 接口文档 | api-doc-generator | 「扫描 backend/ 出接口文档」 | 04 |
| 只有后端源码 | 接口自动化全套 | ApiAutoTest2.0 | 按 04 册分步说 | 04 |
| 有一张用例表（xlsx/MD） | 在网页上执行 | browser-use-case-runner | 「执行 xx.xlsx，地址 https://…」 | 05 |
| 被测端含微信小程序 | 小程序 UI 自动化 | miniprogram 三件套 | 「@miniprogram-script-author …」 | 06 |
| 有 25 列 UI 用例 | 永久回归脚本（进 CI） | web-script-author | 「转 Playwright 脚本，落位…」 | 07 |
| 想要用户手册 | 带截图的操作手册 | operation-manual | 「给 https://… 生成操作手册」 | 08 |
| 没有需求文档，只有网址 | 从真实界面探索出用例 | playwright-cli-testcase | 「探索 https://… 出测试点计划，确认后导 Excel」 | 14 |
| 界面有 Canvas/验证码，又要进 CI | 代码化 UI 自动化 | playwright-midscene 四件套 | 「@00-playwright-explore-plan …」 | 15 |
| 维护遗留 opentest 项目 | 按原流程继续 | opentest 7 技能 | 「新建 OpenTest 测试工作，被测对象…」 | 16 |
| 执行前要准备测试数据 | 造数文件（Postman/SQL/Excel/Python） | seed-test-data | 「根据 docs/api-docs.md 造一套数据，正常+异常，要 Postman 和 Excel」 | 17 |
| 想试 AI 自主探索 E2E | 探索式测试 | testerarmy-e2e | 「初始化 e2e，引擎 Web，厂商 DeepSeek」 | 09 |
| 本次迭代做完 | 用例/脚本入库 | test-automation 脚本 | 「分拣入库，版本 2026Q4-xx」 | 10 |
| 迭代上线 | 资产晋级主干 | promote_iteration.py | 「把 2026Q4-xx 晋级」 | 10 |
| 用例格式要互转 | Excel/XMind/MD 转换 | spectest-convert | 「把 xx.xlsx 转成 XMind」 | 03 |

---

## 6. 常见问题 FAQ（速查版，详见各分册）

**Q1：我说了触发词，Claude 没用对应技能？**
检查技能是否已同步到使用目录（[01-快速上手 §3](01-快速上手-第一次使用.md)）；或直接用斜杠命令 `/技能名` 精确调用。

**Q2：spectest 的产物去哪了？**
在**被测项目**的 `spectest/changes/<变更名>/` 下，不在本仓库。

**Q3：跑 UI 用例时弹出验证码怎么办？**
正常。技能会截图 → 尝试识别（报告置信度）→ 停下等你回复验证码。**不会绕过风控或伪造通过**。

**Q4：接口用例失败它会自己改吗？**
不会。「runner 只执行不修改」是硬规矩——只给失败 ID、预期 vs 实际、根因、修复建议。

**Q5：账号密码会泄露到用例文件吗？**
不会。一律环境变量注入（`ENV:XXX`、`MP_ACCOUNT` 等），文件里只有变量名。

**Q6：中途中断了怎么办？**
直接重新说一次（如再发 `/testflow`），它会扫描已生成的产物判断进度、从断点继续。

**Q7：`graphify-out/` 是什么？**
graphify 技能（`/graphify`，把任意输入转知识图谱）的产物目录，与测试流程无关，可忽略。

**Q8：opentest1.0.5 / playwright-cli-testcase / playwright-midscene 这三套是什么？**
opentest 是 spectest 的前身（遗留项目维护用，见 [16 册](16-技能详解-opentest-用例设计工作流.md)）；后两套是**可选独立套件**（[14 册](14-技能详解-playwright-cli-testcase-探索式用例生成.md)、[15 册](15-技能详解-playwright-midscene-混合UI自动化.md)），部署后可用。新项目一律走 spectest + testflow 主线。

---

## 7. 小白术语表

| 术语 | 大白话解释 |
|------|-----------|
| 技能（Skill） | 写给 AI 的标准作业流程说明书（SKILL.md），AI 读了就照着干 |
| 触发词 | 说到的关键词，AI 据此判断启用哪个技能 |
| 斜杠命令 | 对话框输入 `/` 弹出的技能列表，如 `/spectest-generate`，精确点名技能 |
| 25 列 Excel | 全工作流通用的标准用例表格式（25 个固定列），spectest 产出，是所有环节的「通用货币」 |
| 8 列 xlsx | 执行器（UI/小程序）要的精简用例格式，由转换器从 25 列自动转出 |
| run-config | UI 执行当轮的唯一配置真源（会话策略、录屏开关），每轮自动生成 |
| 有头 / 无头 | 有头=能看见浏览器窗口；无头=后台静默跑。UI 测试默认有头便于观察 |
| PASS / FAIL / BLOCKED | 通过 / 失败 / 被阻塞（无法自动判定或需人工，≠ 通过） |
| pytest | Python 最常用的测试框架（接口执行用它） |
| Playwright | 微软出品的浏览器自动化框架（界面回归脚本用它） |
| Allure | 测试报告美化工具，出漂亮的网页版报告 |
| browser-use | 一个浏览器自动化 CLI 工具（daemon 常驻、按元素索引操作），UI 执行的底层工具 |
| Jest | JavaScript 测试框架（小程序脚本用它） |
| WXML | 小程序的页面结构文件（类似网页的 HTML），写小程序选择器前必须实际看到它 |
| 主干 main / 迭代 iterations | 资产库的两级目录：主干=每日回归的核心集；迭代=本版本新增，上线后晋级 |
| 分拣 / 晋级 | 把 25 列用例按规则归入库 / 把迭代资产并入主干 |
| CI | 持续集成，这里指每晚 02:17 自动跑回归的 GitHub Actions |
| `DEP:` / `STEP:` / `ENV:` | 接口用例里的引用语法：引用依赖的值 / 上一步的值 / 环境变量的值 |
| suite.json | 小程序/界面脚本的「用例清单+编排」文件（哪条用例对应哪个脚本） |
| Page Object | 界面自动化组织方式：一个页面一个文件，集中放该页的元素定位 |
| cases.json | 接口自动化的核心数据文件（顶层 dependencies + cases） |
| daemon | 常驻后台的进程（browser-use 用它保持浏览器跨命令存活） |

---

## 8. 安全红线（所有技能共同遵守）

1. **不伪造测试结果**：验证码识别不了、断言无法自动判定 → 如实标 BLOCKED 等人工，绝不假装通过；
2. **不绕过风控**：验证码/扫码/短信等人工环节按各技能的停等规则走，禁止技术绕过；
3. **敏感信息不入文件**：账号、密码一律环境变量注入，不写进用例/脚本/仓库；
4. **执行器不改用例**：api-test-runner 失败只给建议；修复由人（或专门 fix 技能）决策；
5. **不臆造**：扫描件抽不出字、选择器没见过真实页面、API 未文档化 → 明确报错/拒绝，不编造。

---

## 9. 深入阅读索引（各套件自带文档）

| 套件 | 自带文档（相对本目录） |
|------|------------------------|
| prd-review | [../../prd-review/使用说明.md](../../prd-review/使用说明.md) |
| spectest | [../../spectest/CLAUDE.md](../../spectest/CLAUDE.md)（25 列定义） |
| ApiAutoTest2.0 | [../../ApiAutoTest2.0/使用说明.md](../../ApiAutoTest2.0/使用说明.md) |
| browser-use-case-runner | [../../browser-use-case-runner/使用说明.md](../../browser-use-case-runner/使用说明.md) |
| browser-use | [../../browser-use/使用说明.md](../../browser-use/使用说明.md) |
| miniprogram | [../../miniprogram/使用说明.md](../../miniprogram/使用说明.md) |
| web-script-author | [../../web-script-author/SKILL.md](../../web-script-author/SKILL.md) |
| operation-manual | [../../operation-manual/使用说明.md](../../operation-manual/使用说明.md) |
| testerarmy-e2e | [../../testerarmy-e2e/使用说明.md](../../testerarmy-e2e/使用说明.md) |
| test-automation | [../../test-automation/README.md](../../test-automation/README.md)、[使用说明](../../test-automation/使用说明.md) |
| testflow | [../../testflow/使用说明.md](../../testflow/使用说明.md)、[用户指南](../../testflow/references/user-guide.md) |
| 工作区总览 | [../../README.md](../../README.md) |

---

*本文档基于 2026-10-29 的仓库现状整理。技能在持续迭代，若本套文档与各套件《使用说明.md》有出入，以套件文档为准。*
