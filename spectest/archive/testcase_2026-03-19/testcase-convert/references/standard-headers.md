# 标准25列表头定义

详细定义参见：`/home/che/.claude/skills/testcase-design-functional/references/testcase-headers.md`

## 列顺序与Key映射

| 列 | 列名 | Key |
|----|------|-----|
| A | 系统/项目 | project |
| B | 模块 | module |
| C | 功能 | feature |
| D | 测试项 | test_item |
| E | 用例标题 | title |
| F | 前置条件 | preconditions |
| G | 涉及到数据库表 | db_tables |
| H | 测试数据 | test_data |
| I | 测试步骤 | steps |
| J | 预期结果 | expected_result |
| K | 验证SQL | validation_sql |
| L | 实际结果 | actual_result |
| M | 是否通过 | is_passed |
| N | 预计工时(h) | estimated_hours |
| O | 执行时间(年月日) | execute_date |
| P | 测试进度(%) | test_progress |
| Q | 用例类型 | case_type |
| R | 用例优先级 | priority |
| S | 是否回归用例 | is_regression |
| T | 是否阻塞上线 | is_blocker |
| U | 关联需求ID | requirement_id |
| V | API URL | api_url |
| W | BUG数 | bug_count |
| X | BUG未解决数 | bug_unresolved |
| Y | 用例版本 | case_version |

## 映射规则说明

脚本 `scripts/convert_testcase.py` 中的 `MAPPING_RULES` 字典定义了每个标准Key支持的别名列表。

映射策略（按优先级）：
1. **精确匹配**：源列名标准化后（去空格+小写）与别名完全相同
2. **包含匹配**：源列名包含别名，或别名包含源列名

如需添加新的别名，修改 `MAPPING_RULES` 字典中对应 key 的别名列表即可。
