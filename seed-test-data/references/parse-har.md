# HAR 抓包解析

从用户提供的 HAR（HTTP Archive）抽出造数所需接口。HAR 视为**接口侧材料**：可产出 Postman / Excel / Python(HTTP)；无表结构时禁止出 SQL。

细则与勾选/串联规则同 [parse-api.md](parse-api.md)；本文只写 HAR 特有步骤。

## 支持的材料

- Chrome / Edge / Firefox DevTools 导出的 `.har`（HAR 1.2，`log.entries[]`）
- Charles / Proxyman 等导出的 HAR（结构兼容即可）

大文件时先跑 Skill 自带摘要工具，再勾选；不要把整份 HAR 贴进对话：

```bash
python3 "$SKILL_DIR/scripts/summarize_har.py" <file.har> [--host api.example.com]
```

## 解析步骤

1. 读 `log.entries[]`；每条取 `request` / `response`
2. **过滤噪声**（不进入可造数清单）：
   - 静态资源：扩展名或 MIME 含 `js` / `css` / `png` / `jpg` / `gif` / `svg` / `woff` / `ttf` / `map` / `ico`
   - method 为 `OPTIONS`
   - 纯健康检查（path 含 `/health`、`/ping`、`/actuator` 等且无写库 body）
   - 非业务 host：默认取出现次数最多的 API host；可用 `--host` 或用户指定收窄
3. **保留候选**：
   - `POST` / `PUT` / `PATCH`：造数主路径
   - 同资源 `GET`：校验
   - `DELETE` 或 path/body 明显为取消、作废、退房：回滚
   - 登录（如 `/login`、`/auth/token`）：若后续请求带 Authorization，列入「准备-登录」
4. **抽取字段**（与 parse-api 表一致）：
   - method + path（URL 去 query；path 参数保留为 `/users/{id}` 形态时，用实际值推断并在假设里说明）
   - Content-Type（header 或 `postData.mimeType`）
   - 鉴权 header 名（`Authorization`、`token`、`X-Token` 等）；**产物与清单不写真实 token**
   - `postData.text`：能解析 JSON 则记字段名与示例结构
   - 响应 body：找 `data.id`、`id`、`*Id` 等，供串联与 collection 变量
5. **去重**：同一 `METHOD + path` 保留 request body 字段最完整的一条（字段数多者优先；并列取时间较晚）
6. **串联**：后一条请求的 path / query / body 出现前序响应里的 id 值 → 标依赖；最长链列为「串联」勾选项（推荐）
7. **脱敏**：生成 Postman / Python / `.env` 时 token 用占位；交付假设写一句「鉴权从 HAR 识别，请本地填 SEED_TOKEN」

## 用途猜测（摘要与勾选）

| 信号 | 用途 |
|---|---|
| POST/PUT/PATCH + 有 JSON body | `create`（或更新类录入） |
| GET + 路径含 id | `get`（校验） |
| DELETE，或 path 含 cancel/void/checkout | `delete` / `cancel` |
| login / token / oauth | 准备-登录 |

不确定时标「待确认」，仍给合理示例值，不要连环追问。

## 与其它输入混用

| 组合 | 处理 |
|---|---|
| 仅 HAR | 按仅接口：默认 Postman + Excel + Python；禁止出 SQL |
| HAR + 接口文档 | 以 OpenAPI/文档字段约束为准，HAR 补真实 path、header、串联顺序 |
| HAR + 表结构 | 接口产物 + SQL；表结构管库表，HAR 管 HTTP 链路 |
| HAR + Postman | 去重后合并；冲突时文档/OpenAPI > Postman > HAR 示例值 |

## 勾选清单示例

```
可造数范围（来自 HAR，回复序号即可）：
1. 公寓：POST /apartment
2. 房间：POST /room/create（依赖公寓）
3. 租客：POST /tenant/create
4. 入住：POST /tenant/lease（依赖房间+租客）
5. 串联：公寓 → 房间 → 租客 → 入住（推荐）
6. 都要

画像默认：正常 + 异常，各 1 条。要改请一并说明。
```
