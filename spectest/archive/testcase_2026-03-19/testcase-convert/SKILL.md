---
name: testcase-convert
description: >
  测试用例格式转换技能：将不同表头格式的测试用例 Excel 文件，智能映射并转换为统一标准的25列表头 Excel 文件。
  不修改任何测试用例内容，只做列的映射和格式统一。
  当用户说"转换测试用例格式"、"统一测试用例表头"、"convert test case format"、"测试用例格式转换"、
  "testcase format convert"、"帮我把测试用例转换成标准格式"、"统一测试用例Excel格式"、
  "测试用例表头不一致想统一"时，立即触发此技能，不要尝试手动转换。
---

# 测试用例格式转换

将任意表头的测试用例 Excel 文件，自动识别并映射到标准25列格式，输出一份新的规范 Excel 文件。

## 关键路径

- 技能目录：`/home/che/.claude/skills/testcase-convert/`
- 转换脚本：`scripts/convert_testcase.py`
- uv 虚拟环境：`.venv/`（首次使用时由 `scripts/setup_env.sh` 自动创建）
- Python 解释器：`.venv/bin/python`

## 标准表头（25列）

25列顺序：系统/项目、模块、功能、测试项、用例标题、前置条件、涉及到数据库表、测试数据、测试步骤、预期结果、验证SQL、实际结果、是否通过、预计工时(h)、执行时间(年月日)、测试进度(%)、用例类型、用例优先级、是否回归用例、是否阻塞上线、关联需求ID、API URL、BUG数、BUG未解决数、用例版本。

详细定义见：`references/standard-headers.md`

## 执行流程

### 第1步：确认输入

用户提供 Excel 文件路径（.xlsx 或 .xls）。若未指定输出路径，在同目录生成 `原文件名_标准格式.xlsx`。

### 第2步：检查并初始化 uv 环境

每次执行前，先检查虚拟环境是否就绪：

```bash
SKILL_DIR="/home/che/.claude/skills/testcase-convert"
VENV="$SKILL_DIR/.venv"

# 检查环境是否已就绪
if [ -f "$VENV/bin/python" ] && "$VENV/bin/python" -c "import pandas, openpyxl, python_calamine" 2>/dev/null; then
    echo "uv 环境已就绪"
else
    # 首次使用：初始化环境（约需30秒）
    bash "$SKILL_DIR/scripts/setup_env.sh"
fi
```

首次使用时 `setup_env.sh` 会自动用 uv 创建虚拟环境并安装依赖（pandas、openpyxl、python-calamine）。后续使用直接复用已有环境，无需重复安装。

### 第3步：运行转换脚本

```bash
SKILL_DIR="/home/che/.claude/skills/testcase-convert"
VENV="$SKILL_DIR/.venv"

"$VENV/bin/python" "$SKILL_DIR/scripts/convert_testcase.py" \
  "<输入文件绝对路径>" \
  -o "<输出文件绝对路径>"
```

脚本自动完成：
1. 识别源文件表头（支持多引擎：calamine / openpyxl）
2. 将源列智能映射到标准列（精确匹配优先，再关键词包含匹配）
3. 未匹配的源列被忽略，未找到来源的标准列留空
4. 输出带蓝色表头、冻结首行、自动筛选的标准 Excel 文件

### 第4步：向用户汇报结果

转换完成后，告知用户：
- 输出文件路径
- 成功转换的行数
- **列映射情况**：哪些源列映射到了哪个标准列
- **未映射的源列**：被忽略的列，用户可能需要手动补充
- **空白的标准列**：源文件中没有对应数据的标准列

## 常见映射示例

| 源列名 | 映射到标准列 |
|--------|------------|
| 归属、project | 系统/项目 |
| 系统模块、module | 模块 |
| 测试用例名称、用例名 | 用例标题 |
| 步骤、操作步骤 | 测试步骤 |
| 预期、期望结果 | 预期结果 |
| 状态、测试结果 | 是否通过 |
| 优先级 | 用例优先级 |
| 测试时间 | 执行时间(年月日) |

## 注意事项

- **不修改内容**：只做列的重排和表头统一，不修改任何单元格内容
- **路径使用绝对路径**：避免相对路径导致找不到文件
- **映射不满意时**：可修改脚本 `MAPPING_RULES` 字典中的别名列表，然后重新运行
- **多轮迭代**：如果用户对映射结果不满意，根据反馈调整后重新转换
