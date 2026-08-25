# 功能测试用例表头模板（25列标准格式）

> 以 D:\testcase\测试用例管理.xlsx 表头为准

## 列定义速查

| 列 | 列名 | Key | 设计阶段规则 |
|----|------|-----|------------|
| A | 系统/项目 | project | 填项目名或留空 |
| B | 模块 | module | 必填，来自功能清单一级标题 |
| C | 功能 | feature | 必填，来自功能清单二级标题 |
| D | 测试项 | test_item | 必填：从功能细化出的具体检查项，描述性文字，如"关键字模糊搜索准确性"、"空关键字处理"、"登录状态权限校验" |
| E | 用例标题 | title | 必填，动词短语 |
| F | 前置条件 | preconditions | 必填 |
| G | 涉及到数据库表 | db_tables | 从功能清单db_tables提取，可空 |
| H | 测试数据 | test_data | 必填 |
| I | 测试步骤 | steps | 必填，按序编号 |
| J | 预期结果 | expected_result | 必填，含UI+数据层断言 |
| K | 验证SQL | validation_sql | 数据操作必填；纯UI填N/A |
| L | 实际结果 | actual_result | 留空（执行后填） |
| M | 是否通过 | is_passed | 留空（执行后填） |
| N | 预计工时(h) | estimated_hours | 可空 |
| O | 执行时间(年月日) | execute_date | 留空（执行后填） |
| P | 测试进度(%) | test_progress | 留空（执行后填） |
| Q | 用例类型 | case_type | 固定填：功能测试 |
| R | 用例优先级 | priority | 必填：P0/P1/P2/P3 |
| S | 是否回归用例 | is_regression | 是/否，P0/P1填"是" |
| T | 是否阻塞上线 | is_blocker | 是/否，P0填"是" |
| U | 关联需求ID | requirement_id | 禅道需求ID，如 RQ-001，可空 |
| V | API URL | api_url | 从功能清单related_api提取，可空 |
| W | BUG数 | bug_count | 填0（执行后更新） |
| X | BUG未解决数 | bug_unresolved | 填0（执行后更新） |
| Y | 用例版本 | case_version | 必填整数。全新功能填 1；已有用例基础上新增/修改填（旧最大版本号 + 1） |

---

## 测试项（test_item）说明

**测试项是针对功能细化出来的具体测试检查项，是描述性文字，不是类型标签。**

- ✅ 正确示例：`关键字模糊搜索准确性`、`空关键字处理`、`搜索结果分页展示`、`未登录访问重定向`
- ❌ 错误示例：`正向`、`负向`、`边界`（这些是覆盖类型标签，不是测试项）

| 功能 | 测试项示例 |
|------|-----------|
| 地址搜索 | 关键字模糊搜索准确性 |
| 地址搜索 | 空关键字处理 |
| 地址搜索 | 搜索结果数据一致性验证 |
| 地址新增 | 必填字段校验 |
| 地址新增 | 地址名称唯一性约束 |
| 地址新增 | 成功新增后列表刷新 |

---

## 覆盖类型（test_type，内部字段，不导出为列）

SubAgent 输出 JSON 中需包含 `test_type` 字段，用于 Excel 行背景着色，**不会出现在 Excel 列中**。

| test_type 值 | 含义 | Excel 行颜色 | 覆盖目标 |
|-------------|------|------------|---------|
| 正向 | 正常流程、主成功场景 | 白色 | ≥ 40% |
| 负向 | 异常输入、错误提示、空数据 | 淡黄 #FFF2CC | ≥ 30% |
| 边界 | 边界值、最大最小、临界场景 | 淡蓝 #DDEEFF | ≥ 20% |
| 安全 | SQL注入、XSS等安全场景 | 淡橙 #FFE4CC | ≥ 10%（安全+权限合计） |
| 权限 | 角色权限、越权访问、未登录 | 淡橙 #FFE4CC | ≥ 10%（安全+权限合计） |

---

## 完整用例示例（地址搜索功能）

### 用例1（正向 P0）

| 字段 | 内容 |
|------|------|
| 系统/项目 | LSP物流平台 |
| 模块 | 地址管理 |
| 功能 | 地址搜索 |
| 测试项 | 关键字模糊搜索准确性 |
| 用例标题 | 有效中文关键字模糊搜索返回匹配地址列表 |
| 前置条件 | 1. 已使用管理员账号登录系统\n2. 数据库中存在包含"上海"的地址记录\n3. 已进入地址列表页面 |
| 涉及到数据库表 | lsp_dev.lsp_address_suburb |
| 测试数据 | 搜索关键字：上海 |
| 测试步骤 | 1. 进入「地址管理」→「地址列表」页面\n2. 在顶部搜索框中输入"上海"\n3. 点击「搜索」按钮（或按 Enter）\n4. 等待列表区域加载完成\n5. 核查列表数据行数与顶部显示总数 |
| 预期结果 | UI层：\n- 页面无报错（无红色弹框）\n- 列表显示含"上海"的地址记录，每行包含地址名称、所属区域等字段\n- 顶部显示结果总数：共 X 条记录\n- 搜索框保留输入的"上海"\n\n数据层：\nSELECT COUNT(*) = 页面显示的总数 |
| 验证SQL | SELECT COUNT(*) FROM lsp_dev.lsp_address_suburb WHERE suburb_name LIKE '%上海%' OR district LIKE '%上海%'; |
| 实际结果 | （执行后填写） |
| 是否通过 | （执行后填写） |
| 预计工时(h) | 0.5 |
| 执行时间(年月日) | （执行后填写） |
| 测试进度(%) | （执行后填写） |
| 用例类型 | 功能测试 |
| 用例优先级 | P0 |
| 是否回归用例 | 是 |
| 是否阻塞上线 | 是 |
| 关联需求ID | RQ-001 |
| API URL | /api/address/search |
| BUG数 | 0 |
| BUG未解决数 | 0 |
| 用例版本 | 1 |

---

### 用例2（负向 P1）

| 字段 | 内容 |
|------|------|
| 测试项 | 空数据结果提示 |
| 用例标题 | 搜索数据库中不存在的关键字显示空状态提示 |
| 测试数据 | 搜索关键字：火星社区XYZ999 |
| 预期结果 | 列表区域显示"暂无数据"空状态提示，不报错，不崩溃 |
| 验证SQL | SELECT COUNT(*) FROM lsp_dev.lsp_address_suburb WHERE suburb_name LIKE '%火星社区XYZ999%'; -- 期望：0 |
| 用例优先级 | P1 |
| 是否回归用例 | 是 |
| 是否阻塞上线 | 否 |

---

### 用例3（负向 P2）

| 字段 | 内容 |
|------|------|
| 测试项 | SQL注入安全防护 |
| 用例标题 | 搜索框输入SQL注入字符不触发数据库异常 |
| 测试数据 | 搜索关键字：' OR '1'='1 |
| 预期结果 | 页面无SQL报错/500异常，返回空结果或正常结果，不暴露数据库信息 |
| 验证SQL | N/A（只读/交互功能） |
| 用例优先级 | P2 |
| 是否阻塞上线 | 否 |

---

### 用例4（边界 P2）

| 字段 | 内容 |
|------|------|
| 测试项 | 空关键字处理 |
| 用例标题 | 清空搜索框点击搜索显示全量地址数据 |
| 测试数据 | 搜索关键字：空（清空搜索框） |
| 预期结果 | 展示所有地址记录，分页正常，总数与数据库一致 |
| 验证SQL | SELECT COUNT(*) FROM lsp_dev.lsp_address_suburb WHERE is_deleted = 0; |
| 用例优先级 | P2 |

---

### 用例5（权限 P1）

| 字段 | 内容 |
|------|------|
| 测试项 | 未登录状态访问权限校验 |
| 用例标题 | 未登录状态访问地址列表页自动跳转登录页 |
| 前置条件 | 用户未登录，直接访问地址列表URL |
| 测试数据 | 无 |
| 预期结果 | 自动跳转到登录页面，不展示任何地址数据 |
| 验证SQL | N/A（只读/交互功能） |
| 用例优先级 | P1 |
| 是否回归用例 | 是 |
| 是否阻塞上线 | 是 |

---

## SubAgent 输出 JSON 示例

> `test_type` 为内部字段，用于行着色，**不导出为 Excel 列**。
> `test_item` 为描述性检查项文字，**导出为 Excel 第 D 列**。

```json
[
  {
    "project": "LSP物流平台",
    "module": "地址管理",
    "feature": "地址搜索",
    "test_item": "关键字模糊搜索准确性",
    "test_type": "正向",
    "title": "有效中文关键字模糊搜索返回匹配地址列表",
    "preconditions": "1. 已登录系统\n2. 数据库中存在含'上海'的地址\n3. 进入地址列表页",
    "db_tables": "lsp_dev.lsp_address_suburb",
    "test_data": "搜索关键字：上海",
    "steps": "1. 进入地址列表页\n2. 搜索框输入'上海'\n3. 点击搜索\n4. 等待加载",
    "expected_result": "UI层：列表显示含'上海'记录，总数正确\n数据层：COUNT(*)=页面总数",
    "validation_sql": "SELECT COUNT(*) FROM lsp_dev.lsp_address_suburb WHERE suburb_name LIKE '%上海%';",
    "actual_result": "",
    "is_passed": "",
    "estimated_hours": "0.5",
    "execute_date": "",
    "test_progress": "",
    "case_type": "功能测试",
    "priority": "P0",
    "is_regression": "是",
    "is_blocker": "是",
    "requirement_id": "RQ-001",
    "api_url": "/api/address/search",
    "bug_count": "0",
    "bug_unresolved": "0",
    "case_version": "1"
  },
  {
    "project": "LSP物流平台",
    "module": "地址管理",
    "feature": "地址搜索",
    "test_item": "空数据结果提示",
    "test_type": "负向",
    "title": "搜索不存在的关键字显示空状态提示",
    "preconditions": "1. 已登录系统\n2. 进入地址列表页",
    "db_tables": "lsp_dev.lsp_address_suburb",
    "test_data": "搜索关键字：火星社区XYZ999",
    "steps": "1. 进入地址列表页\n2. 搜索框输入'火星社区XYZ999'\n3. 点击搜索",
    "expected_result": "列表显示\"暂无数据\"空状态提示，不报错",
    "validation_sql": "SELECT COUNT(*) FROM lsp_dev.lsp_address_suburb WHERE suburb_name LIKE '%火星社区XYZ999%'; -- 期望：0",
    "actual_result": "",
    "is_passed": "",
    "estimated_hours": "0.5",
    "execute_date": "",
    "test_progress": "",
    "case_type": "功能测试",
    "priority": "P1",
    "is_regression": "是",
    "is_blocker": "否",
    "requirement_id": "",
    "api_url": "/api/address/search",
    "bug_count": "0",
    "bug_unresolved": "0",
    "case_version": "1"
  }
]
```
