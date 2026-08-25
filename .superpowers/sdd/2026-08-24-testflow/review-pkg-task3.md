# Task 3 Review Package (非git环境：新建文件全文即完整diff)

## 文件1: SKILL.md (新建)

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

## 文件2: references/workflow-map.md (新建)

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
