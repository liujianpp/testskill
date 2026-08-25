---
name: testcase-fix
description: 测试用例评审并自动完善技能。当用户说"评审并完善测试用例"、"帮我完善测试用例"、"fix test cases"、"修复测试用例"、"测试用例评审和修复"、"评审并改进测试用例"时触发此技能。在评审的基础上，自动根据评审意见补全缺失内容、完善测试步骤和预期结果，最终输出2份文档：一份带评审意见的文档（供审查）、一份已完善的干净用例文档（可直接使用）。
---

# 测试用例评审+完善技能

你是一个专业的测试用例改进专家，先评审测试用例发现问题，再根据评审意见自动完善用例内容，输出两份文档。

## 工作目录

本技能复用 `~/.claude/skills/testcase-review/` 的所有脚本和目录结构。

## 与 `/testcase-review` 的区别

| 功能 | `/testcase-review` | `/testcase-fix`（本技能）|
|------|---------------------|--------------------------|
| 评审，给出意见 | ✅ | ✅ |
| 根据意见自动完善 | ❌ | ✅ |
| 输出文档数量 | 1份（带评审意见列） | 2份（评审文档 + 完善文档）|

## 执行步骤

### Step 0：确认输入

向用户确认以下信息：

1. **测试用例文件路径**（必须）：Excel(.xlsx/.xls) 或 CSV
2. **需求文档路径**（可选）
3. **业务逻辑文档路径**（可选）
4. **API接口文档路径**（可选）
5. **数据库连接配置**（可选）
6. **指定 Sheet**（可选，多 Sheet Excel 时使用）

### Step 1～5：评审流程（同 `/testcase-review`）

按照 `~/.claude/skills/testcase-review/SKILL.md` 的 Step 1～5 完整执行评审流程，得到评审报告文件：
`output/<stem>_reviewed_YYYYMMDD_HHMMSS.xlsx`

### Step 4b：并行完善有问题的用例

```bash
cd ~/.claude/skills/testcase-review
python scripts/fixer_agent.py \
  --review testcase/review_results.json \
  --parsed testcase/parsed_testcases.json \
  --skill_dir ~/.claude/skills/testcase-review \
  --workers 3
```

每个 Worker 会：
1. 读取有评审意见的测试用例
2. 理解评审意见指出的具体问题
3. 调用 Claude 根据问题完善对应字段（步骤、预期结果、前置条件、用例标题等）
4. 只修改有问题的字段，不改动其他内容

输出：`testcase/fixed_testcases.json`

### Step 5b：生成完善后的测试用例文档

```bash
python scripts/fixed_writer.py \
  --original testcase/<原始文件名> \
  --fixed testcase/fixed_testcases.json \
  --output output/
```

基于原始 Excel 结构，将改进内容写回对应单元格，改动的单元格用**浅黄色**高亮标注，方便对比查看：
`output/<stem>_fixed_YYYYMMDD_HHMMSS.xlsx`

### Step 6：汇报结果

向用户汇报：
- 评审结果：总用例数、有问题数、通过数
- 完善结果：实际完善了几条用例、改动了几个单元格
- 输出2份文档路径

## 一键命令

```bash
cd ~/.claude/skills/testcase-review
python scripts/start.py --testcase "<路径>" --fix [--sheet "<Sheet名>"]
```

## 两份输出文档说明

| 文档 | 文件名格式 | 用途 |
|------|-----------|------|
| 评审文档 | `*_reviewed_*.xlsx` | 保留评审意见列，红/绿高亮，供测试负责人审核 |
| 完善文档 | `*_fixed_*.xlsx` | 无评审意见列，黄色标注改动处，可直接作为正式测试用例 |

## 注意事项

- 完善仅针对**有评审意见的用例**；评审为空（优秀用例）直接原样保留
- 可完善的字段：用例标题、前置条件、测试步骤、预期结果、用例类型、用例优先级
- 非标准表头（不符合 `测试用例管理.xlsx` 规范）的列无法精确回填，但 AI 仍会尽力完善
- 需要 `ANTHROPIC_API_KEY` 环境变量
