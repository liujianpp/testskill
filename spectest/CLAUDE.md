# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 项目概述

这是一套完整的测试用例管理和设计系统。仓库包含：

- **`spectest/`** - SpecTest 统一测试工作流（整合了 OpenTest + Testcase 的所有功能）
- **`archive/opentest_2026-03-19/`** - 已归档的 OpenTest 原始技能（保留供参考）
- **`archive/testcase_2026-03-19/`** - 已归档的 Testcase 原始技能（保留供参考）

**整合完成日期：** 2026-03-19
**整合版本：** SpecTest V1

### SpecTest 8步工作流

1. **spectest-new** - 创建新的测试变更目录
2. **spectest-analysis** - 智能需求分析（支持 API/功能清单）
3. **spectest-points** - 生成测试点文件（自动或手动）
4. **spectest-generate** - 生成测试用例（Excel/XMind）
5. **spectest-review** - 评审测试用例质量
6. **spectest-fix** - 自动修复测试用例问题
7. **spectest-report** - 生成测试执行报告
8. **spectest-archive** - 归档完成的变更

## 架构

### 技能结构

每个技能都是独立模块，包含以下结构：

```
<skill-name>/
├── SKILL.md              # 技能定义和工作流（通过 / 命令触发）
├── pyproject.toml        # Python 依赖（uv 管理）
├── requirements.txt      # 可选的 pip 依赖
├── scripts/              # 可执行的 Python 脚本
├── references/           # 文档（设计方法、模板）
└── assets/               # 模板和静态资源
```

### 技能触发方式

技能通过斜杠命令或自然语言模式触发。示例触发词：
- `/opentest-new` - 创建新的 OpenTest 变更目录
- `/opentest-analysis` - 生成需求分析
- `/opentest-points` - 生成测试点
- `/opentest-generate` - 生成测试用例（Excel 或 XMind）
- "生成API测试用例" 或 "design api test cases" - 触发 `testcase-design-api`
- "生成功能测试用例" 或 "design functional test cases" - 触发 `testcase-design-functional`
- "转换测试用例格式" 或 "convert test case format" - 触发 `testcase-convert`

## 开发工作流

### 环境设置

所有 Python 脚本必须使用 `uv run` 执行（不能直接使用 `python`）：

```bash
# Linux/macOS/WSL
SKILL_DIR="$HOME/.claude/skills/<skill-name>"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/<script>.py" [参数]

# Windows PowerShell
$SkillDir = "$env:USERPROFILE\.claude\skills\<skill-name>"
uv run --project $SkillDir python "$SkillDir\scripts\<script>.py" [参数]
```

**重要提示：** `SKILL_DIR=` 变量赋值和 `uv run` 命令必须在同一个 Bash 工具调用中执行，否则变量会丢失。

### 安装依赖

首次使用每个技能时（创建 `.venv` 并安装依赖）：

```bash
# 确保 uv 已安装
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 同步依赖（如需要会创建 .venv）
uv sync --project "$SKILL_DIR"
```

后续运行会复用已有环境，几乎瞬间完成。

### Python 环境

技能使用 `uv` 进行依赖管理，配置在 `pyproject.toml` 中：
- **Python 版本**：要求 Python 3.10+
- **常用依赖**：openpyxl（Excel）、pymysql（MySQL）、pandas（数据处理）、anthropic（AI）

## 测试用例格式

### 标准 25 列 Excel 格式

所有测试用例使用标准化的 25 列格式。列顺序如下：

1. 系统/项目 (project/system)
2. 模块 (module)
3. 功能 (feature)
4. 测试项/测试点 (test_item)
5. 用例标题 (title)
6. 前置条件 (preconditions)
7. 涉及相关数据库表 (db_tables)
8. 测试数据准备 (test_data)
9. 测试步骤 (steps) - **必填**
10. 预期结果 (expected_result) - **必填**
11. 验证SQL (validation_sql)
12. 实际结果 (actual_result)
13. 是否通过 (is_passed)
14. 预估工时 (estimated_hours)
15. 执行时间 (execute_date)
16. 测试进度 (test_progress)
17. 用例类型 (case_type) - "API测试" 或 "功能测试"
18. 用例优先级 (priority) - P0/P1/P2 - **必填**
19. 是否回归用例 (is_regression) - "是"/"否"
20. 是否阻塞上线 (is_blocker) - "是"/"否"
21. 关联需求ID (requirement_id)
22. API URL (api_url)
23. BUG数 (bug_count)
24. BUG未解决数 (bug_unresolved)
25. 用例版本 (case_version)

### 内部字段（不导出到 Excel）

- `test_type` - 用于行颜色标记："正向"/"负向"/"边界"/"安全"

## SpecTest 工作流

SpecTest 在 `spectest/changes/<name>/` 中遵循顺序工作流：

1. **spectest-new** - 创建变更目录并编写 `proposal.md`
2. **spectest-analysis** - 生成 `requirements-analysis.md`（智能需求拆解、可测项梳理）
3. **spectest-points** - 生成 `specs/*.md` 测试点文件（支持自动生成）
4. **spectest-generate** - 根据测试点生成测试用例（Excel/XMind，支持 3 种模式）
5. **spectest-review** - 评审测试用例质量、覆盖率、SQL 正确性
6. **spectest-fix** - 自动修复测试用例中发现的问题
7. **spectest-report** - 生成 `report.md` 执行摘要
8. **spectest-archive** - 将完成的变更移至 `archive/`

### 技能触发方式

SpecTest 技能通过斜杠命令或自然语言模式触发。示例触发词：
- `/test-new` - 创建新的测试变更目录
- `/test-analysis` - 智能需求分析
- `/test-points` - 生成测试点
- `/test-generate Excel` - 生成 Excel 测试用例
- `/test-generate XMind` - 生成 XMind 思维导图
- `/test-review` - 评审测试用例
- `/test-fix` - 修复测试用例问题
- `/test-convert` - 转换测试用例格式（独立命令）

### 三种生成模式

`spectest-generate` 支持三种生成模式：

1. **from-specs** - 从测试点文件简单转换（`specs/*.md`）
2. **from-api** - 从 OpenAPI 文档智能生成（`project_info/api_list.json`）
3. **from-feature** - 从功能清单智能生成（`project_info/feature_list.md`）

## 数据库集成

### 默认配置

大多数技能使用存储在 `<skill>/db_config.json` 中的默认 MySQL 配置：

```json
{
  "测试mysql": {
    "host": "192.168.1.31",
    "port": 13306,
    "user": "ethan",
    "password": "ethan263*2",
    "database": null,
    "charset": "utf8mb4"
  }
}
```

### 查询数据库表结构

使用 `query_db_schema.py` 获取表结构用于测试用例设计：

```bash
SKILL_DIR="$HOME/.claude/skills/<skill-name>"
uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/query_db_schema.py" \
  --db_config "<db_config.json>" \
  --table_keywords "<表1>,<表2>"
```

## SpecTest 核心技能

### spectest-new
创建新的测试变更目录，编写关联需求文档的 proposal.md。

**使用方式**：`/test-new` 或提供功能名称和需求文档。

**输出结构**：
```
changes/<name>/
├── proposal.md              # 变更提案
├── requirements-analysis.md # 需求分析（test-analysis 生成）
├── specs/                   # 测试点文件（test-points 生成）
├── project_info/           # 项目信息（API列表、功能清单）
├── db_info/                # 数据库配置
├── artifacts/              # 生成的测试用例（JSON、Excel、XMind）
└── review/                 # 评审报告（test-review 生成）
```

### spectest-analysis
智能需求分析和可测项梳理。

**使用方式**：在变更目录中执行 `/test-analysis`

**功能特性**：
- 自动提取功能模块列表
- 自动识别 API 接口
- 智能拆解需求为可测项
- 生成 `project_info/feature_list.md` 和 `project_info/api_list.json`

**内部调用**：testcase-design-api 和 testcase-design-functional 的能力

### spectest-points
生成测试点文件。

**使用方式**：`/test-points`（自动）或 `/test-points manual`（手动）

**两种模式**：
1. **自动模式**（默认）：调用智能设计能力生成测试点
2. **手动模式**：提供结构化模板，用户手动编写

**输出**：`specs/feature_*.md` 测试点文件

### spectest-generate
根据测试点生成测试用例（Excel 或 XMind）。

**使用方式**：
- `/test-generate Excel` - 生成 Excel 文件
- `/test-generate XMind` - 生成 XMind 文件

**三种生成模式**：
1. `from-specs` - 从测试点文件简单转换
2. `from-api` - 从 OpenAPI 文档智能生成（调用 testcase-design-api）
3. `from-feature` - 从功能清单智能生成（调用 testcase-design-functional）

**脚本**：
- `scripts/generate_excel.py` - 导出 JSON 为标准 25 列 Excel
- `scripts/generate_xmind.py` - 导出 JSON 为 XMind 思维导图

**字段映射**：支持新旧字段名自动映射（get_field() 函数）

### spectest-review
评审测试用例质量、覆盖率、SQL 正确性。

**使用方式**：`/test-review`

**检查项**：
- 覆盖率是否达标（正向 ≥40%、负向 ≥30%、边界 ≥20%、安全 ≥10%）
- 测试用例可操作性
- SQL 语句正确性
- 优先级分布合理性

**完全使用**：testcase-review 的能力

### spectest-fix
自动修复测试用例中发现的问题。

**使用方式**：`/test-fix`

**功能**：
- 自动修复 SQL 错误
- 补充缺失字段
- 调整测试用例格式

**完全使用**：testcase-fix 的能力

### spectest-report
根据测试执行结果生成报告。

**使用方式**：`/test-report`

**脚本**：`scripts/read_execution_results.py`

**输出**：`report.md` 执行摘要

### spectest-archive
归档完成的测试变更。

**使用方式**：`/test-archive`

**功能**：将变更移至 `archive/` 目录，添加日期前缀

### spectest-convert
独立的测试用例格式转换工具（非工作流步骤）。

**使用方式**：`/test-convert`

**功能**：将不同表头格式的 Excel 转换为标准 25 列格式

**完全使用**：testcase-convert 的能力

## 测试

仓库中当前没有自动化测试。测试脚本通过技能工作流手动执行。

## Windows 特定说明

- 使用 PowerShell 执行技能
- 路径分隔符：`\`（反斜杠）
- 变量语法：`$SkillDir = "..."` 而非 `SKILL_DIR="..."`
- 如果使用 Git Bash/WSL，使用 Unix 风格命令和 `/` 路径分隔符

## 常见问题

### uv 命令未找到
先安装 uv：
```bash
# PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 变量未找到错误
确保 `SKILL_DIR=` 和 `uv run` 在同一个 Bash 工具调用中。

### 数据库连接失败
1. 检查 `db_config.json` 凭证
2. 验证到 MySQL 服务器的网络连接
3. 确认数据库存在且用户有权限

### Windows 权限错误
如需要，以管理员身份运行 PowerShell。

## 本地化

此代码库在以下方面使用简体中文：
- 测试用例内容和描述
- 数据库字段名和注释
- SKILL.md 文件中的文档

英文用于：
- 代码和脚本文件名
- 技术文档
- API 规范
