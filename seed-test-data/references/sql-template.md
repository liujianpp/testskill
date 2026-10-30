# SQL 产物模板

生成成对脚本，编码 UTF-8，可直接在测试库客户端执行。默认 MySQL 语法。

## 文件

| 文件 | 内容 |
|---|---|
| `{场景}-01_seed.sql` | 按依赖正向 `INSERT` |
| `{场景}-02_rollback.sql` | 按依赖反向 `DELETE` |

禁止只出其中一份。禁止在 seed 里 `UPDATE` 已有业务行。禁止 rollback 使用 `TRUNCATE` 或无 WHERE 的 `DELETE`。

## 文件头

两份文件开头都写：

```sql
-- 场景：{场景}
-- 前缀：QA_YYYYMMDD_
-- 画像：正常 / 异常
-- 表顺序（插入）：user -> order -> order_item
-- 表顺序（回滚）：order_item -> order -> user
-- 环境：仅测试库。执行前请确认当前库。
```

## seed

- 每张表一组 INSERT，组前用注释标明画像，如 `-- 正常用户`、`-- 异常-冻结用户`
- 自增主键不要手写 id（除非用户明确要求固定 id）
- 字符串用单引号；前缀出现在用户名、备注、业务单号等可搜列
- 同一批多行可用一条 `INSERT ... VALUES (...), (...);`
- **串联链路**：子表 INSERT 用 `SELECT` 按本次前缀业务键关联父表（同一序号互指），例如：

```sql
INSERT INTO apartment_room (apartment_id, room_no, floor, layout, area, status, description)
SELECT id, 'QA_101', 1, '一室一厅', 50.00, 2, 'QA_YYYYMMDD_正常房间1'
FROM apartment WHERE name = 'QA_YYYYMMDD_阳光公寓1';

INSERT INTO tenant_lease (tenant_id, room_id, check_in_time, lease_months, deposit, monthly_rent, status)
SELECT t.id, r.id, '2026-09-04 10:00:00', 12, 2000.00, 2500.00, 0
FROM tenant t
INNER JOIN apartment a ON a.name = 'QA_YYYYMMDD_阳光公寓1'
INNER JOIN apartment_room r ON r.apartment_id = a.id AND r.room_no = 'QA_101'
WHERE t.name = 'QA_YYYYMMDD_张三';
```

- 需要后续 rollback / 查找时，在 INSERT 后加注释或 `SELECT` 提示（优先写本批精确业务键，不用 `LIKE`）：

```sql
-- 查找本次数据：
-- SELECT id, username FROM user WHERE username IN ('QA_YYYYMMDD_user_ok_a1b2c3', 'QA_YYYYMMDD_user_frozen_d4e5f6');
```

不要把 `SELECT` 当作必须执行才能回滚；rollback 应仅靠本批已写入的精确业务键（或主键列表）即可删除。

## rollback

- 删除顺序与插入相反
- **优先精确业务键**：`WHERE 列 IN (...本批 seed 写死的唯一值...)`；唯一键优先（`id_card`、业务单号等），其次完整业务名 / 房间号等；**禁止**用 `LIKE 'QA_YYYYMMDD_%'` 做 DELETE（易误删同日前缀其他数据）
- 子表可通过 `IN (SELECT id FROM 父表 WHERE 精确键 IN (...))` 关联；需要多条件时（如房间）同时限定父表精确键 + 本批 `room_no`
- 示例：

```sql
DELETE FROM order_item WHERE order_id IN (SELECT id FROM `order` WHERE order_no IN ('QA_YYYYMMDD_ord_a1b2c3', 'QA_YYYYMMDD_ord_d4e5f6'));

DELETE FROM `order` WHERE order_no IN ('QA_YYYYMMDD_ord_a1b2c3', 'QA_YYYYMMDD_ord_d4e5f6');

DELETE FROM user WHERE username IN ('QA_YYYYMMDD_user_ok_a1b2c3', 'QA_YYYYMMDD_user_frozen_d4e5f6');
```

MySQL 若不允许删除子查询同表，改为把本批 id / 业务键写死到 `IN (...)`，或拆成用户可分步执行的临时表写法。

- 每条 `DELETE` 必须带 WHERE，且 WHERE 为本批精确键或明确 id 列表（同一行写完，便于校验）
- 文件末尾加查找残留（条件与 DELETE 一致，不用 `LIKE`）：

```sql
-- 可选检查（应为空）：
-- SELECT * FROM user WHERE username IN ('QA_YYYYMMDD_user_ok_a1b2c3', 'QA_YYYYMMDD_user_frozen_d4e5f6');
```

## 示例片段

seed：

```sql
INSERT INTO user (username, phone, status, remark)
VALUES
  ('QA_20260904_user_ok_a1b2c3', '13800000001', 1, '正常'),
  ('QA_20260904_user_frozen_d4e5f6', '13800000002', 0, '异常-冻结');
```

rollback：

```sql
DELETE FROM user WHERE username IN ('QA_20260904_user_ok_a1b2c3', 'QA_20260904_user_frozen_d4e5f6');
```
