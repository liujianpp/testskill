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
