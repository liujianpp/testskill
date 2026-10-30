# Postman 产物模板

生成 **Collection v2.1** 与配套 Environment，须可直接导入 Postman 后执行。

## 文件

| 文件 | 说明 |
|---|---|
| `{场景}-seed.postman_collection.json` | 造数 / 校验 / 回滚请求 |
| `{场景}-seed.postman_environment.json` | `baseUrl`、`token` 及业务变量 |

`info.schema` 固定：

`https://schema.getpostman.com/json/collection/v2.1.0/collection.json`

## Environment

至少包含：

```json
{
  "name": "{场景}-seed",
  "values": [
    { "key": "baseUrl", "value": "https://api.example.test", "enabled": true },
    { "key": "token", "value": "", "enabled": true }
  ]
}
```

用户文档里有网关地址则写入 `baseUrl`；没有则用占位 `https://api.example.test`，并在交付说明里提醒替换。  
造数过程中产生的 id 用 collection 变量（`{{userId}}`）即可，不必预先写进 environment。

## Collection 结构

根下三个文件夹，顺序固定：

1. `造数` — 创建类请求，按依赖 / 串联链路排序；需要登录时第一条为登录并把 token 写入 `{{token}}`
2. `校验` — 对造数得到的 id 发 GET；没有 GET 则省略该文件夹
3. `回滚` — DELETE / 取消 / 作废，按链路**反序**；没有此类接口则文件夹保留且 `item` 为空，并在 collection `description` 写明无法接口回滚

请求命名：`{画像}-{资源}`，如 `正常-公寓`、`正常-房间`、`异常-余额不足用户`。

### 串联链路

选了串联范围时，造数文件夹按链路顺序排请求；上一步响应 `data.id` 写入 collection 变量（如 `apartmentId` / `roomId` / `tenantId` / `leaseId`），下一步 body/path 用 `{{apartmentId}}` 等引用。同一画像下的多步共用同一套 id，不要为各资源各造互不相关的独立记录。校验与回滚按反序使用同一批变量。

## 单条请求约定

- `url` 使用 `{{baseUrl}}/实际路径`
- 需要鉴权时 header：`Authorization: Bearer {{token}}`（文档若规定其他 header 则跟文档）
- body 用 raw JSON，值为可提交的测试数据，不要留 `TODO`
- 造数请求的 `event` 里用 test 脚本取出 id：

```javascript
pm.test("2xx", function () {
  pm.expect(pm.response.code).to.be.within(200, 299);
});
const json = pm.response.json();
const id = json.data && (json.data.id || json.data.userId);
if (id) {
  pm.collectionVariables.set("userId", String(id));
}
```

变量名按资源：`apartmentId`、`roomId`、`tenantId`、`leaseId`、`userId`、`orderId`。后续校验/回滚请求的 path 使用对应变量。

异常画像请求：允许预期 4xx 的，把断言改成文档约定的错误码，不要强行 2xx。

## Collection 最小骨架

```json
{
  "info": {
    "name": "{场景}-seed",
    "description": "前缀 QA_YYYYMMDD_。回滚：{有删除接口 / 无删除接口}。",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    { "name": "造数", "item": [] },
    { "name": "校验", "item": [] },
    { "name": "回滚", "item": [] }
  ],
  "variable": [
    { "key": "userId", "value": "" }
  ]
}
```

导入方式（写在交付说明，不必自动操作 Postman）：Import → 选 collection JSON，再 Import environment，选中该环境后从「造数」文件夹自上而下 Run。
