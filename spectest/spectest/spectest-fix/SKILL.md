---
name: spectest-fix
description: SpecTest 测试用例修复 - 根据评审意见自动完善测试用例。完全使用 testcase-fix 的能力。当用户要根据评审意见修复用例、补充缺失场景、或执行 spectest-fix 时使用。
---

# spectest-fix：测试用例修复

## 职责

根据评审意见自动完善测试用例，补充缺失内容、修正测试步骤和预期结果。

**完全使用 testcase-fix 的能力。**

## 当前变更目录

- 若用户指定了变更名，使用 `spectest/changes/<name>/`。
- 若未指定且项目下仅有一个非归档变更目录（即 `spectest/changes/` 下仅有一个非 `archive` 的子目录），则默认使用该目录。
- 若有多个未归档变更，询问用户要对哪一个执行。

## 执行步骤

1. **确定当前变更目录**。
2. **读取评审报告**：
   - `review/review_report.md`
   - 或用户指定的评审报告
3. **调用 testcase-fix 技能**：
   ```bash
   SKILL_DIR="$HOME/.claude/skills/testcase-fix"
   uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/start.py" \
     --testcase "<用例文件>" \
     --review "<评审报告>" \
     --fix
   ```
4. **保存完善后的用例**：
   - 将完善后的用例保存到 `artifacts/` 目录
5. **告知用户**：
   - 修复了哪些问题
   - 新增了哪些测试场景
   - 输出文件路径

## 修复能力

testcase-fix 会自动修复以下问题：

1. **补充缺失的测试场景**：
   - 覆盖率不足时，自动补充测试用例
   - 增加边界值测试
   - 增加安全测试

2. **修正测试步骤**：
   - 步骤不清晰时，重新编写
   - 缺少前置条件时，补充前置条件
   - 步骤顺序不合理时，调整顺序

3. **修正预期结果**：
   - 预期结果不明确时，重新编写
   - 缺少验证点时，补充验证点
   - 验证SQL错误时，修正SQL

4. **修正测试数据**：
   - 测试数据不真实时，使用真实数据
   - 缺少测试数据时，补充测试数据
   - 测试数据来源不明确时，标注来源

## 输出

- 评审文档（带评审意见列）
- 完善文档（已修复的干净用例）

## 下一步

修复完成后，可以执行：
- `/spectest-generate from-specs` - 重新生成用例 Excel
- `/spectest-report` - 生成执行报告（执行测试后）
- `/spectest-archive` - 归档变更
