---
name: spectest-review
description: SpecTest 测试用例评审 - 评审测试用例质量、覆盖率、最佳实践。完全使用 testcase-review 的能力。当用户要评审用例、检查覆盖率、或执行 spectest-review 时使用。
---

# spectest-review：测试用例评审

## 职责

评审测试用例的质量、覆盖率和最佳实践，输出评审报告和问题清单。

**完全使用 testcase-review 的能力。**

## 当前变更目录

- 若用户指定了变更名，使用 `spectest/changes/<name>/`。
- 若未指定且项目下仅有一个非归档变更目录（即 `spectest/changes/` 下仅有一个非 `archive` 的子目录），则默认使用该目录。
- 若有多个未归档变更，询问用户要对哪一个执行。

## 执行步骤

1. **确定当前变更目录**。
2. **调用 testcase-review 技能**：
   ```bash
   SKILL_DIR="$HOME/.claude/skills/testcase-review"
   uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/start.py" \
     --testcase "<用例文件>" \
     [--requirement "<需求文档>"] \
     [--api_doc "<API文档>"]
   ```
3. **读取评审报告**：
   - 总体评分
   - 优点清单
   - 问题清单
   - 改进建议
4. **保存评审报告**：
   - 将评审报告保存到 `review/review_report.md`
5. **询问用户**：是否需要根据评审意见修复用例？

## 评审维度

 testcase-review 会检查以下维度：

1. **覆盖率检查**：
   - 正向测试 ≥ 40%
   - 负向测试 ≥ 30%
   - 边界测试 ≥ 20%
   - 安全测试 ≥ 10%

2. **测试步骤可操作性**：
   - 步骤是否明确
   - 是否指明"点击哪里"、"输入什么"
   - 是否可以独立执行

3. **验证 SQL 正确性**：
   - 表名是否正确
   - 字段名是否匹配
   - SQL 语法是否正确

4. **优先级合理性**：
   - P0：核心流程、关键功能
   - P1：重要功能
   - P2：边缘场景

5. **测试数据来源**：
   - 是否标注测试数据来源
   - 是否使用真实数据

6. **测试用例完整性**：
   - 必填字段是否完整
   - 描述是否清晰

## 产物

- `spectest/changes/<name>/review/review_report.md` - 评审报告
- `spectest/changes/<name>/review/<name>_reviewed_YYYYMMDD_HHMMSS.xlsx` - 带评审意见的 Excel

## 下一步

评审完成后，可以执行：
- `/spectest-fix <问题>` - 根据评审意见修复用例
- `/spectest-report` - 生成执行报告（执行测试后）
- `/spectest-archive` - 归档变更
