---
name: spectest-analysis
description: SpecTest 智能需求分析 - 生成或更新 requirements-analysis.md，提取功能点清单和 API 接口清单。当用户要做需求分析、梳理可测项、或执行 spectest-analysis 时使用。在当前变更目录下产出 requirements-analysis.md（需求拆解、功能清单、API清单）、project_info/feature_list.md、project_info/api_list.json，对应流程中的「智能需求分析」步骤。
---
# spectest-analysis：智能需求分析

## 职责

在当前 SpecTest 变更目录下生成或更新 `requirements-analysis.md`，完成智能需求分析与可测项梳理，同时提取功能点清单和 API 接口清单，对应流程中的「智能需求分析」步骤。

**核心能力：** 整合 testcase-design-api 和 testcase-design-functional 的解析能力。

## 当前变更目录

- 若用户指定了变更名，使用 `spectest/changes/<name>/`。
- 若未指定且项目下仅有一个非归档变更目录（即 `spectest/changes/` 下仅有一个非 `archive` 的子目录），则默认使用该目录。
- 若有多个未归档变更，询问用户要对哪一个执行。

## 执行步骤

1. **确定当前变更目录**（按上规则）。
2. **读取上下文**：
   - 读取 `proposal.md` 以保持与提案一致
   - 读取 `project_info/` 下的需求文档（PDF、Word、Markdown 等）
3. **智能提取**（调用 testcase 解析能力）：
   - **功能点清单**：提取功能点、用户故事、业务规则
   - **API 接口清单**：提取 API 端点、请求方法、路径
   - **数据库表**：识别涉及的数据库表（如有）
4. **生成或更新 requirements-analysis.md**：
   - 需求来源：需求文档/PRD/用户故事路径或摘要
   - 功能与可测项拆解：按功能或模块列出可测点
   - 边界与异常：关键边界、异常输入、依赖条件
   - 待澄清项：需与产品/开发确认的问题（如有）
   - 模板与字段说明见：`references/requirements-analysis-template.md`。
5. **生成 project_info/feature_list.md**：
   - Markdown 格式的功能点清单
   - 包含：功能点名称、描述、数据库表、技术栈、业务规则
6. **生成 project_info/api_list.json**（如有 API）：
   - JSON 格式的 API 接口清单
   - 包含：端点路径、请求方法、描述
7. **告知用户**：文件路径及下一步可执行「测试点」（spectest-points）。

## 产物

- `spectest/changes/<name>/requirements-analysis.md`
- `spectest/changes/<name>/project_info/feature_list.md`
- `spectest/changes/<name>/project_info/api_list.json`（如有 API）

## 内部调用说明

本技能内部调用以下 testcase 技能的能力：

- **testcase-design-functional** 的解析逻辑：从需求文档提取功能点
- **testcase-design-api** 的解析逻辑：从 API 文档提取接口清单

## 可用脚本

本技能包含以下可执行脚本（使用 `uv run` 执行）：

### 1. parse_feature_list.py - 解析功能清单

从 Markdown 格式的功能清单中提取结构化功能点列表。

**用法：**

```bash
SKILL_DIR="$HOME/.claude/skills/spectest-analysis"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/parse_feature_list.py" \
  --feature_list <功能清单.md> \
  --output feature_list.json
```

**输出：** `feature_list.json` - 结构化的功能点列表

### 2. query_db_schema.py - 查询数据库表结构

根据表名关键词查询 MySQL 数据库表结构。

**用法：**

```bash
SKILL_DIR="$HOME/.claude/skills/spectest-analysis"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/query_db_schema.py" \
  --db_config <db_config.json> \
  --table_keywords <关键词1,关键词2> \
  --output table_schema.json
```

**输出：** `table_schema.json` - 表结构信息

## 参考文档

本技能使用以下参考文档：

- **references/design-methods.md** - 测试用例设计方法指南（场景法、等价类、边界值等）
- **references/testcase-headers.md** - 标准测试用例表头定义（25列格式）

## 下一步

完成需求分析后，可以执行：

- `/spectest-points 自动` - 自动生成测试点（推荐）
- `/spectest-points 手动` - 手动编写测试点
