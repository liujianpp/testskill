---
name: spectest-generate
description: SpecTest 生成测试用例 - 支持多种输入源生成完整测试用例并导出 Excel 或 XMind。三种模式：from-specs（从测试点）、from-api（从API文档智能生成）、from-feature（从功能清单智能生成）。当用户要生成用例、执行 spectest-generate 时使用。对应流程中的「生成测试用例」步骤。
---

# spectest-generate：用例生成

## 职责

根据用户指定的输入源，生成完整测试用例并导出为 Excel 或 XMind 格式，输出到当前变更的 `artifacts/` 目录。

**三种输入源模式：**
1. **from-specs**：从测试点（specs/*.md）生成用例（简单格式转换）
2. **from-api**：从 API 文档智能生成用例（调用 testcase-design-api）
3. **from-feature**：从功能清单智能生成用例（调用 testcase-design-functional）

## 当前变更目录

- 若用户指定了变更名，使用 `spectest/changes/<name>/`。
- 若未指定且项目下仅有一个非归档变更目录（即 `spectest/changes/` 下仅有一个非 `archive` 的子目录），则默认使用该目录。
- 若有多个未归档变更，询问用户要对哪一个执行。

## 输出格式

- **Excel**：生成 .xlsx 文件，25 列标准格式（系统/项目、模块、功能、测试项、用例标题、前置条件、涉及相关数据库表、测试数据准备、测试步骤、预期结果、验证SQL、实际结果、是否通过、预估工时、执行时间、测试进度、用例类型、用例优先级、是否回归用例、是否阻塞上线、关联需求ID、API URL、BUG数、BUG未解决数、用例版本）
- **XMind**：生成 .xmind 思维导图（XMind 8 格式），按功能模块组织

可同时生成两种格式，如 `--format Excel,XMind`。

## 模式 1：from-specs（从测试点生成）

### 适用场景
已有测试点文件（specs/*.md），需要快速转换为标准测试用例格式。

### 执行步骤

1. **确定当前变更目录**。
2. **读取上下文**：
   - `specs/*.md`（必须）
   - `requirements-analysis.md`（可选）
   - `proposal.md`（可选）
3. **解析测试点**：提取每个测试点的：
   - 场景描述
   - 验收条件
   - 测试数据
   - 验证 SQL
   - 优先级
   - 测试类型
4. **转换为结构化 JSON**：生成 `artifacts/testcases.json`
5. **调用生成脚本**：
   - Excel：`generate_excel.py`
   - XMind：`generate_xmind.py`
6. **告知用户**：列出生成的文件路径。

### 产物

- `spectest/changes/<name>/artifacts/<name>_testcases.xlsx`
- `spectest/changes/<name>/artifacts/<name>_testcases.xmind`
- `spectest/changes/<name>/artifacts/testcases.json`

## 模式 2：from-api（从 API 文档智能生成）

### 适用场景
只有 API 文档（OpenAPI JSON），需要智能设计 API 测试用例。

### 执行步骤

1. **确定当前变更目录**。
2. **读取 API 文档**：
   - 从 `--doc` 参数读取 OpenAPI JSON 文件
   - 或从 `project_info/api_list.json` 读取
3. **调用 testcase-design-api 智能设计**：
   - 解析 OpenAPI JSON，提取 API 端点
   - 对比已有用例，找出未覆盖的 API
   - 并行调度 3 个子 Agent 设计测试用例
   - 查询数据库表结构，生成验证 SQL
   - 获取真实测试数据（从 DB 随机采样）
   - 应用测试设计方法（等价类划分、边界值分析等）
   - 确保覆盖率目标（正向≥40%、负向≥30%、边界≥20%、安全≥10%）
4. **生成 testcases.json**：保存设计的测试用例
5. **调用生成脚本**：
   - Excel：`generate_excel.py`
   - XMind：`generate_xmind.py`
6. **告知用户**：列出生成的文件路径及覆盖率统计。

### 产物

- `spectest/changes/<name>/artifacts/<name>_API_testcases.xlsx`
- `spectest/changes/<name>/artifacts/testcases.json`

### 内部调用

- **testcase-design-api** 的完整流程：
  - `find_uncovered_apis.py`（找缺口）
  - `query_db_schema.py`（查询表结构）
  - 并行调度 3 个子 Agent 设计用例
  - `export_excel.py`（导出 Excel）

## 模式 3：from-feature（从功能清单智能生成）

### 适用场景
只有功能清单（Markdown），需要智能设计功能测试用例。

### 执行步骤

1. **确定当前变更目录**。
2. **读取功能清单**：
   - 从 `--doc` 参数读取 Markdown 功能清单
   - 或从 `project_info/feature_list.md` 读取
3. **调用 testcase-design-functional 智能设计**：
   - 解析功能清单，提取功能点
   - 并行调度 3 个子 Agent 设计测试用例
   - 查询数据库表结构，生成验证 SQL
   - 获取真实测试数据（从 DB 随机采样）
   - 应用测试设计方法（场景法、判定表等）
   - 确保覆盖率目标（正向≥40%、负向≥30%、边界≥20%、安全≥10%）
4. **生成 testcases.json**：保存设计的测试用例
5. **调用生成脚本**：
   - Excel：`generate_excel.py`
   - XMind：`generate_xmind.py`
6. **告知用户**：列出生成的文件路径及覆盖率统计。

### 产物

- `spectest/changes/<name>/artifacts/<name>_functional_testcases.xlsx`
- `spectest/changes/<name>/artifacts/testcases.json`

### 内部调用

- **testcase-design-functional** 的完整流程：
  - `parse_feature_list.py`（解析功能清单）
  - `find_uncovered_features.py`（找缺口）
  - `query_db_schema.py`（查询表结构）
  - 并行调度 3 个子 Agent 设计用例
  - `export_excel.py`（导出 Excel）

## 依赖

### Excel 生成
- **openpyxl**：`pip install openpyxl`
- **pandas**：`pip install pandas`

### XMind 生成
- 无额外依赖，使用 XMind 8 格式生成

### 数据库查询（智能生成模式）
- **pymysql**：`pip install pymysql`
- 数据库配置文件：`db_info/db_config.json`

## 可用脚本

本技能包含以下可执行脚本（使用 `uv run` 执行）：

### 1. find_uncovered_apis.py - 找出未覆盖的 API

解析 OpenAPI JSON，对比已有测试用例，找出还没有覆盖的 API。

**用法：**
```bash
SKILL_DIR="$HOME/.claude/skills/spectest-generate"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/find_uncovered_apis.py" \
  --api_doc <api_docs.json> \
  [--testcase <已有用例.xlsx>] \
  --output api_list_to_design.json
```

**输出：** `api_list_to_design.json` - 待设计用例的 API 列表

### 2. find_uncovered_features.py - 找出未覆盖的功能点

对比功能点列表与已有测试用例，找出没有任何测试用例覆盖的功能点。

**用法：**
```bash
SKILL_DIR="$HOME/.claude/skills/spectest-generate"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/find_uncovered_features.py" \
  --feature_list <feature_list.json> \
  [--testcase <已有用例.xlsx>] \
  --output features_to_design.json
```

**输出：** `features_to_design.json` - 待设计用例的功能点列表

### 3. query_db_schema.py - 查询数据库表结构

根据表名关键词查询 MySQL 数据库表结构。

**用法：**
```bash
SKILL_DIR="$HOME/.claude/skills/spectest-generate"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/query_db_schema.py" \
  --db_config <db_config.json> \
  --table_keywords <关键词1,关键词2> \
  --output table_schema.json
```

**输出：** `table_schema.json` - 表结构信息

### 4. generate_excel.py - 生成 Excel 测试用例

从 testcases.json 生成标准 25 列 Excel 文件（包含 3 个 Sheet）。

**用法：**
```bash
SKILL_DIR="$HOME/.claude/skills/spectest-generate"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/generate_excel.py" \
  --input testcases.json \
  --output artifacts/cases.xlsx
```

**输出：** Excel 文件（3 个 Sheet：测试用例、功能点覆盖矩阵、覆盖率汇总）

### 5. generate_xmind.py - 生成 XMind 测试用例

从 testcases.json 生成 XMind 思维导图。

**用法：**
```bash
SKILL_DIR="$HOME/.claude/skills/spectest-generate"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/generate_xmind.py" \
  --input testcases.json \
  --output artifacts/cases.xmind
```

**输出：** XMind 文件（按功能模块组织）

## 快速用例生成（跳过工作流）

支持不创建变更目录的快速生成模式：

```bash
# 只从 API 文档生成用例
/spectest-generate from-api \
  --doc ~/Downloads/api.json \
  --output ~/my_testcases.xlsx

# 只从功能清单生成用例
/spectest-generate from-feature \
  --doc ~/Downloads/feature_list.md \
  --output ~/my_testcases.xlsx
```

## 参考文档

本技能使用以下参考文档：
- **references/design-methods.md** - 测试用例设计方法指南（场景法、等价类、边界值等）
- **references/testcase-headers.md** - 标准测试用例表头定义（25列格式）

## 下一步

生成用例后，可以执行：
- `/spectest-review <文件>` - 评审用例质量和覆盖率
- `/spectest-report` - 生成执行报告（执行测试后）
- `/spectest-archive` - 归档变更
