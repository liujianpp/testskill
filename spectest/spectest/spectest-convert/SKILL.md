---
name: spectest-convert
description: SpecTest 测试用例格式转换 - 将不同表头格式的测试用例 Excel 文件，智能映射并转换为统一标准的25列表头 Excel 文件。完全使用 testcase-convert 的能力。当用户要转换格式、统一表头、或执行 spectest-convert 时使用。
---

# spectest-convert：测试用例格式转换

## 职责

将任意表头的测试用例 Excel 文件，自动识别并映射到标准25列格式，输出一份新的规范 Excel 文件。

**完全使用 testcase-convert 的能力。**

## 标准表头（25列）

25列顺序：系统/项目、模块、功能、测试项、用例标题、前置条件、涉及到数据库表、测试数据、测试步骤、预期结果、验证SQL、实际结果、是否通过、预计工时(h)、执行时间(年月日)、测试进度(%)、用例类型、用例优先级、是否回归用例、是否阻塞上线、关联需求ID、API URL、BUG数、BUG未解决数、用例版本。

## 执行步骤

1. **确认输入**：用户提供 Excel 文件路径（.xlsx 或 .xls）。若未指定输出路径，在同目录生成 `原文件名_标准格式.xlsx`。
2. **调用 testcase-convert 技能**：
   ```bash
   SKILL_DIR="$HOME/.claude/skills/testcase-convert"
   uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/convert_testcase.py" \
     "<输入文件路径>" \
     -o "<输出文件路径>"
   ```
3. **向用户汇报结果**：
   - 输出文件路径
   - 成功转换的行数
   - 列映射情况
   - 未映射的源列
   - 空白的标准列

## 脚本功能

脚本自动完成：
1. 识别源文件表头（支持多引擎：calamine / openpyxl）
2. 将源列智能映射到标准列（精确匹配优先，再关键词包含匹配）
3. 未匹配的源列被忽略，未找到来源的标准列留空
4. 输出带蓝色表头、冻结首行、自动筛选的标准 Excel 文件

## 依赖

- **pandas**：数据处理
- **openpyxl**：Excel 读写
- **python-calamine**：高性能 Excel 读取（备选引擎）

## 使用场景

- 收到其他团队的测试用例，表头格式不一致
- 需要统一测试用例格式以便合并分析
- 不同时期的测试用例表头不同，需要统一

## 注意

- 此技能不依赖任何流程步骤
- 可随时独立使用
- 不修改原文件，只生成新文件

## 完成后

格式转换完成后，可以执行：
- `/spectest-new <变更名>` - 创建新的测试工作
- 将转换后的用例作为参考
