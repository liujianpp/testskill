---
name: spectest-plan
description: SpecTest 测试计划 - 在需求分析之后、测试点之前，生成或更新 test-plan.md（范围/策略/环境/人力与人天/进度/进出标准/风险/交付物）。当用户要写测试计划、或执行 spectest-plan / spectest plan 时使用。Use when the user asks for 测试计划、test plan、测试排期与人天估算, or wants to define scope/strategy/schedule before designing test points.
---

# spectest-plan：测试计划

## 职责

在当前 SpecTest 变更目录下生成或更新 `test-plan.md`，完成**策略 + 管理**向的测试计划：范围与策略、测试类型与优先级、环境与数据、人力与人天、进度、进出标准、风险、交付物。用于指导后续测试点深度与优先级，**不**写覆盖矩阵或用例提纲（那些由 spectest-generate 的 `design.md` 负责）。

本步骤为**可选步骤**，位于流程中：spectest-analysis → **spectest-plan** → spectest-points。没有 test-plan.md 时后续步骤照常执行（spectest-points 会提示但不阻断）。

## 当前变更目录

- 若用户指定了变更名，使用 `spectest/changes/<name>/`。
- 若未指定且项目下仅有一个非归档变更目录（即 `spectest/changes/` 下仅有一个非 `archive` 的子目录），则默认使用该目录。
- 若有多个未归档变更，询问用户要对哪一个执行。

## 与上下游文档的边界

- **proposal.md**：只引用背景与测试目标，不在计划中重写长背景。
- **requirements-analysis.md**：据此定范围、优先级与风险；不重写需求拆解表。
- **test-plan.md（本产物）**：组织这次测试怎么做（策略与管理）。
- **design.md**：用例设计方法、覆盖矩阵、提纲——本技能不产出、不替代。
- **prd-review 评审报告**（若经 testflow 链路附入）：需求视角的阻塞点/风险提示可作为本计划「风险与应对」的输入；本计划不重复评审内容。

## 执行步骤

1. **确定当前变更目录**（按上规则）。
2. **读取上下文**：
   - 若存在 `requirements-analysis.md`，优先读取（范围、可测项、待澄清、边界与异常）。
   - 若存在 `proposal.md`，读取被测对象与测试目标以保持一致。
   - 若存在 prd-review 评审报告（proposal 中附记的路径），读取其阻塞点与风险提示。
   - 若尚无 `requirements-analysis.md`，仍可基于 proposal 起草计划，并在「风险与应对」或相关节注明建议先完成需求分析。
3. **生成或更新 test-plan.md**：在变更目录下写入 `test-plan.md`，内容包含：
   - 目标与范围（在范围内 / 不在范围内；对齐 proposal / 需求分析）
   - 策略与优先级（测试类型、覆盖深度策略、模块或能力优先级）
   - 环境与数据
   - 人力与人天（角色分工、分阶段/模块人天估算与合计）
   - 进度与里程碑（与人天、可用人力对齐）
   - 进入标准 / 退出标准
   - 风险与应对
   - 交付物（对应该变更后续产物）
   - 模板与字段说明见：[references/test-plan-template.md](references/test-plan-template.md)。
4. **告知用户**：文件路径及下一步可执行「测试点」（spectest-points）。

## 产物

- `spectest/changes/<name>/test-plan.md`

## 下一步

完成测试计划后，可以执行：

- `/spectest-points 自动` - 生成测试点时会对照本计划的范围与优先级策略
- `/spectest-points 手动` - 手动编写测试点
