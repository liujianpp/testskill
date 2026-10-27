---
name: spectest-points
description: SpecTest 测试点 - 按用例设计方法（等价类/边界值/场景法/错误推测）推导「要测什么」。支持两种模式：自动生成（调用 testcase 智能设计）或手动编写。当用户要写测试点、或执行 spectest-points 时使用。产出 specs/*.md 测试点文件，供 spectest-generate 展开为完整测试用例。
---

# spectest-points：测试点

## 职责

在当前 SpecTest 变更目录的 `specs/` 下生成测试点文件，列出「要测什么」的要点清单，对应流程中的「测试点」步骤。

**设计方法推导**：针对各模块/功能点选用等价类、边界值、场景法、错误推测等设计方法（可组合）推导测试点，并为每条测试点标注所用方法；若有 `test-plan.md`，按其中的范围与优先级策略取舍覆盖深度。

**两种模式：**
1. **自动生成**：调用 testcase 智能设计能力，从功能清单和 API 文档自动生成测试点
2. **手动编写**：用户手动编写测试点文件

## 当前变更目录

- 若用户指定了变更名，使用 `spectest/changes/<name>/`。
- 若未指定且项目下仅有一个非归档变更目录（即 `spectest/changes/` 下仅有一个非 `archive` 的子目录），则默认使用该目录。
- 若有多个未归档变更，询问用户要对哪一个执行。

## 模式选择

根据用户输入判断模式：
- 用户输入"自动" → 自动生成模式
- 用户输入"手动" → 手动编写模式
- 未指定 → 询问用户选择哪种模式

## 自动生成模式

### 执行步骤

1. **确定当前变更目录**。
2. **读取上下文**：
   - `requirements-analysis.md`（需求分析）
   - `project_info/feature_list.md`（功能点清单）
   - `project_info/api_list.json`（API 接口清单）
   - `test-plan.md`（若存在：对照其范围、优先级与覆盖深度策略；若不存在，可提示用户先做「测试计划」spectest-plan，不强制阻断）
3. **调用 testcase 智能设计能力**（按设计方法推导，可组合）：
   - **功能测试点**：调用 testcase-design-functional，按等价类、边界值、场景法、错误推测推导
   - **API 测试点**：调用 testcase-design-api，按参数边界、异常组合、场景链路推导
4. **查询数据库表结构**（如需要）：
   - 读取 `db_info/db_config.json`
   - 使用 query_db_schema.py 查询表结构
5. **生成测试点文件**：
   - 每个功能点生成 `feature_<name>.md`
   - 每个 API 生成 `api_<name>.md`
   - 包含：测试点编号、标题、设计方法、用户故事、验收条件、测试数据、验证SQL、优先级、测试类型
6. **告知用户**：产出路径及下一步可执行「生成用例」（spectest-generate）。

### 产物

- `spectest/changes/<name>/specs/feature_*.md` - 功能测试点
- `spectest/changes/<name>/specs/api_*.md` - API 测试点

## 手动编写模式

### 执行步骤

1. **确定当前变更目录**。
2. **读取上下文**：
   - `proposal.md`
   - `requirements-analysis.md`（如存在）
   - `test-plan.md`（如存在：对照其范围与优先级策略；若无，可提示先做 spectest-plan，不阻断）
3. **打开编辑器**：
   - 在 `specs/` 目录下创建测试点文件
   - 提供测试点模板和示例
4. **用户手动编写**：
   - 按照模板编写测试点
   - 完成后告知用户
5. **告知用户**：下一步可执行「生成用例」（spectest-generate）。

### 测试点模板

```markdown
# <功能/API 名称>

## 测试点 <编号>：<标题>

**设计方法：** 等价类/边界值/场景法/错误推测（可组合，标注本条所用方法）

**用户故事：** <描述>

**验收条件：**
- <条件1>
- <条件2>

**测试数据：** <具体数据>

**数据库验证：**
```sql
<SELECT 语句>
```

**优先级：** P0/P1/P2

**测试类型：** 正向/负向/边界/安全
```

### 产物

- `spectest/changes/<name>/specs/testpoints.md` 或用户命名的其他文件

## 内部调用说明

**自动生成模式**内部调用以下 testcase 技能的能力：
- **testcase-design-functional** 的设计逻辑：识别测试维度、设计功能测试点
- **testcase-design-api** 的设计逻辑：识别 API 测试场景、设计 API 测试点
- **query_db_schema.py**：查询数据库表结构，生成验证 SQL

## 下一步

完成测试点后，可以执行：
- `/spectest-generate from-specs` - 从测试点生成用例（会先出用例设计方案 design.md，再展开导出）
- `/spectest-generate from-api` - 从 API 文档智能生成用例
- `/spectest-generate from-feature` - 从功能清单智能生成用例
