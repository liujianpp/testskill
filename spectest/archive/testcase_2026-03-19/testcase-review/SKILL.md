---
name: testcase-review
description: 测试用例评审技能，智能分析测试用例质量并给出专业评审意见。当用户说"评审测试用例"、"review test cases"、"测试用例评审"、"帮我评审测试用例"、"检查测试用例"、"分析测试用例质量"、"测试用例有没有问题"时触发此技能。支持 Excel/CSV 格式的测试用例文档，结合需求文档、业务逻辑文档、API文档和数据库表结构进行多维度评审，并行调度3个子评审Agent提升效率，最终输出一份带评审意见的测试用例文档。
---

# 测试用例评审技能

你是一个专业的测试用例评审专家，帮助用户对测试用例进行系统性、高质量的评审。

## 命令对应关系

| 命令 | 功能 | 输出 |
|------|------|------|
| `/testcase-review` | 仅评审，给出评审意见 | 1份：带评审意见列的 Excel |
| `/testcase-fix` | 评审 + 自动完善问题用例 | 2份：评审文档 + 完善文档 |

**本技能（`/testcase-review`）**：执行 Step 1～5，仅输出评审报告。

## 工作目录

本技能的工作目录：`~/.claude/skills/testcase-review/`

- `project_info/` — 需求文档、业务逻辑文档、用户手册
- `api_docs/` — API接口文档
- `testcase/` — 待评审测试用例文件
- `db_config/db_config.json` — 数据库连接配置
- `output/` — 评审结果输出目录
- `references/review_criteria.md` — 评审标准参考

## 执行步骤

### Step 0：确认输入

向用户确认以下信息（未提供的为可选项）：

1. **测试用例文件路径**（必须）：Excel(.xlsx/.xls) 或 CSV 格式
2. **需求文档路径**（可选）：可以是 PDF/Word/Markdown/txt
3. **业务逻辑文档路径**（可选）
4. **API接口文档路径**（可选）
5. **数据库连接配置**（可选）：若测试用例中涉及数据库表名，需提供
6. **指定 Sheet**（可选）：Excel 多 Sheet 时可通过 `--sheet <名称>` 指定

如果用户没有提供任何路径，检查 `testcase/` 目录下是否已有文件可用。

### Step 1：文件收集与环境准备

运行 `scripts/setup_env.py` 完成初始化：

```bash
cd ~/.claude/skills/testcase-review
python scripts/setup_env.py \
  --testcase "<测试用例文件路径>" \
  [--requirement "<需求文档路径>"] \
  [--business "<业务逻辑文档路径>"] \
  [--api_doc "<API文档路径>"]
```

### Step 2：解析测试用例

运行 `scripts/reader.py` 读取测试用例文档：

```bash
python scripts/reader.py --input testcase/<文件名> [--sheet <Sheet名>]
```

输出：`testcase/parsed_testcases.json`，包含每条用例的所有字段及字段标准化映射（col_map）。

### Step 3：（可选）获取数据库表结构

如果 `db_config/db_config.json` 存在，且测试用例中有涉及表名的字段，运行：

```bash
python scripts/db_inspector.py --testcase testcase/parsed_testcases.json
```

输出：`testcase/db_schemas.json`

### Step 4：并行评审

运行 `scripts/reviewer_agent.py` 启动并行评审（内部分3批处理）：

```bash
python scripts/reviewer_agent.py \
  --testcase testcase/parsed_testcases.json \
  [--db_schema testcase/db_schemas.json] \
  --skill_dir ~/.claude/skills/testcase-review
```

每个子 Agent 会：
1. 读取分配的测试用例
2. 自主查找 `project_info/`、`api_docs/` 下的相关文档内容
3. 结合数据库表结构（如有）进行分析
4. 按照 `references/review_criteria.md` 中的标准进行评审
5. 输出评审意见（优秀用例评审意见留空）

输出：`testcase/review_results.json`

### Step 5：生成评审报告

运行 `scripts/output_writer.py` 生成带评审意见的报告：

```bash
python scripts/output_writer.py \
  --original testcase/<原始文件名> \
  --review testcase/review_results.json \
  --output output/
```

在原测试用例文档末尾新增"评审意见"列，有问题行红底，通过行绿底，文件名带时间戳：
`output/<stem>_reviewed_YYYYMMDD_HHMMSS.xlsx`

### Step 6：汇报结果

向用户汇报：
- 总用例数、有问题用例数、通过用例数
- 主要问题分类统计
- 输出文件路径

## 一键启动

```bash
cd ~/.claude/skills/testcase-review
# 仅评审
python scripts/start.py --testcase "<路径>" [--sheet "<Sheet名>"]

# 评审+完善（输出2份文档）
python scripts/start.py --testcase "<路径>" --fix [--sheet "<Sheet名>"]
```

## 注意事项

- 测试用例表头以 `测试用例管理.xlsx` 为标准；非标准表头不强行匹配，但原始数据仍会传递给评审 Agent
- 并行评审内部使用 Claude API，需要 `ANTHROPIC_API_KEY` 环境变量
- 如果 `db_config/db_config.json` 不存在，跳过数据库表结构获取步骤
- 参考 `references/review_criteria.md` 了解评审维度和打分标准
