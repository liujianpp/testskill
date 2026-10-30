# Excel 造数表模板

生成 `{场景}-seed.xlsx`，给人查阅与手工录入参考。接口文档或表结构均可产出。

依赖：`pip install openpyxl`（若环境未安装）。

## Sheet 约定

### 1. 造数清单（固定第一张）

给人看的总览。表头：

| 列 | 说明 |
|---|---|
| 序号 | 从 1 起 |
| 用途 | 如「正常-主链路」「正常用户」「异常-冻结用户」；串联时写清链路用途 |
| 画像 | 正常 / 边界 / 异常 |
| 资源 | 接口 path 或表名；串联可写整链简述如 `公寓→房间→租客→入住` |
| 链路 | 可选；串联时填链路名或步骤序号，如 `主链路` / `1/4`；单资源可空 |
| 关键数据 | 账号、单号、金额等一眼能用的值 |
| 查找方式 | 如 `username IN ('QA_..._a1b2c3')` 或 Postman 变量 |
| 回滚方式 | SQL 文件名、精确 DELETE 条件，或「接口 DELETE /users/{id}」 |

冻结首行。选了串联时：用途写「正常-主链路」等；明细表各资源用同一前缀/序号对齐关联字段（如公寓名 `...公寓1` 对应房间描述 `...房间1`）。

### 2. 每个资源一张明细表

- Sheet 名 = 资源名（表名或简短模块名，如 `user`、`order`）；非法字符替换为 `_`，最长 31
- 第 1 列表头固定为 **画像**
- 其余列为字段名（与接口 body 或表列一致）
- 每行一条数据；`rows` 中每行第一个元素是画像，后面与 `headers` 一一对应
- 冻结首行

## 中间 JSON

Agent 先写 JSON，再调用导出脚本。结构：

```json
{
  "title": "场景名",
  "prefix": "QA_YYYYMMDD_",
  "summary": [
    {
      "purpose": "正常-主链路",
      "profile": "正常",
      "resource": "公寓→房间→租客→入住",
      "chain": "主链路",
      "key_data": "QA_20260904_阳光公寓1_a1b2c3 / R_A1B2C3 / QA_20260904_张三_a1b2c3",
      "lookup": "name IN ('QA_20260904_阳光公寓1_a1b2c3')",
      "rollback": "执行 02_rollback.sql（精确业务键 IN）"
    }
  ],
  "sheets": [
    {
      "name": "apartment",
      "headers": ["name", "address", "contact_phone"],
      "rows": [
        ["正常", "QA_20260904_阳光公寓1", "北京市朝阳区测试路 1 号", "13800000001"]
      ]
    }
  ]
}
```

| 字段 | 要求 |
|---|---|
| `title` | 场景名，用于交付说明 |
| `prefix` | 与造数前缀一致 |
| `summary` | 非空数组；对应「造数清单」每一行；串联时可含可选字段 `chain` |
| `sheets` | 至少一个资源明细；`headers` 不含「画像」；`rows[i][0]` 为画像，其后长度 = `len(headers)`；串联时各 sheet 用同一前缀/序号对齐 |

## 导出命令

```bash
python3 "$SKILL_DIR/scripts/export_excel.py" <data.json> <{场景}-seed.xlsx>
```

文件名默认：`{场景}-seed.xlsx`。
