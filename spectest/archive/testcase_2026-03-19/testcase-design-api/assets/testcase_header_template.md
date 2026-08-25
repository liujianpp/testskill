# 测试用例标准表头参考

本文件是 API 测试用例 Excel 输出的标准表头参考，共 25 列，与功能测试用例表头完全一致。

## 标准列顺序（共 25 列）

```
A  系统/项目          → （可留空）
B  模块               → 地址管理
C  功能               → 地址搜索
D  测试项             → 有效关键字模糊搜索
E  用例标题           → 有效关键字标准搜索返回匹配结果
F  前置条件           → 服务正常运行；数据库中存在包含'上海'的地址记录
G  涉及到数据库表     → lsp_dev.lsp_address_suburb
H  测试数据           → {"pages":{"keyword":"上海","limit":20,"page":1}}
I  测试步骤           → 1. 发送 POST 请求\n2. Body: {...}\n3. 查看响应
J  预期结果           → HTTP 200；success=true；data列表不为空；tp>=0
K  验证SQL            → SELECT COUNT(*) FROM lsp_address_suburb WHERE suburb_name LIKE '%上海%';
L  实际结果           → （执行阶段填写）
M  是否通过           → （执行阶段填写）
N  预计工时(h)        → 0.5
O  执行时间(年月日)   → （执行阶段填写）
P  测试进度(%)        → （执行阶段填写）
Q  用例类型           → API测试
R  用例优先级         → P0 / P1 / P2 / P3
S  是否回归用例       → 是 / 否
T  是否阻塞上线       → 是 / 否
U  关联需求ID         → REQ-001（可选）
V  API URL            → POST /address/search
W  BUG数              → 0
X  BUG未解决数        → 0
Y  用例版本           → 1
```

## 颜色编码（基于 test_type 内部字段）

| test_type | 行背景色 |
|-----------|---------|
| 表头 | #2E75B6（蓝）白字 |
| 正向 | #FFFFFF（白） |
| 负向 | #FFF2CC（浅黄） |
| 边界 | #DDEEFF（浅蓝） |
| 安全 | #FFE4CC（浅橙） |

## 示例用例

| 字段 | 值 |
|------|----|
| 系统/项目 | （空） |
| 模块 | 地址管理 |
| 功能 | 地址搜索 |
| 测试项 | 有效关键字模糊搜索 |
| 用例标题 | 有效关键字标准搜索返回匹配结果 |
| 前置条件 | 1. 服务正常运行且可访问<br>2. 数据库中存在含"上海"的地址数据 |
| 涉及到数据库表 | lsp_dev.lsp_address_suburb |
| 测试数据 | `{"pages":{"keyword":"上海","limit":20,"page":1}}` |
| 测试步骤 | 1. 构造请求 Body: `{"pages":{"keyword":"上海","limit":20,"page":1}}`<br>2. 发送 POST 请求至 /address/search<br>3. 检查 HTTP 状态码<br>4. 检查响应体中 success、data、tp 字段<br>5. 执行验证 SQL |
| 预期结果 | 1. HTTP 状态码 = 200<br>2. success = true<br>3. data 为非空列表<br>4. tp（总数）>= data条数<br>5. 每条记录中包含"上海"相关信息 |
| 验证SQL | `SELECT COUNT(*) FROM lsp_address_suburb WHERE suburb_name LIKE '%上海%';` |
| 实际结果 | （执行后填写） |
| 是否通过 | （执行后填写） |
| 预计工时(h) | 0.5 |
| 执行时间(年月日) | （执行后填写） |
| 测试进度(%) | （执行后填写） |
| 用例类型 | API测试 |
| 用例优先级 | P0 |
| 是否回归用例 | 是 |
| 是否阻塞上线 | 是 |
| 关联需求ID | REQ-ADDR-001 |
| API URL | POST /address/search |
| BUG数 | 0 |
| BUG未解决数 | 0 |
| 用例版本 | 1 |
