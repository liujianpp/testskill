# curl 命令解析

从用户粘贴或文件中的 `curl` 命令抽出造数所需接口。curl 视为**接口侧材料**：可产出 Postman / Excel / Python(HTTP)；无表结构时禁止出 SQL。**不**把「产出 curl 脚本」列为产物格式。

细则与勾选/串联规则同 [parse-api.md](parse-api.md)；本文只写 curl 特有步骤。

## 支持的材料

- 对话中粘贴的一条或多条 `curl ...`（含 Chrome「复制为 cURL」）
- 文件：`.sh` / `.curl` / `.txt`（可含多条；按出现顺序）

大段文件先跑摘要再勾选；不要把整份命令贴进交付对话：

```bash
python3 "$SKILL_DIR/scripts/summarize_curl.py" <file.sh|.curl|.txt>
# 或：
cat cmds.txt | python3 "$SKILL_DIR/scripts/summarize_curl.py" -
```

## 解析步骤

1. 拆分命令：支持行续接 `\`；忽略纯注释与非 `curl` 行；每条独立解析
2. **抽取**：
   - URL：第一个 `http(s)://...` 参数；path 去掉 query
   - method：`-X` / `--request`；若无显式 method 但有 `-d` / `--data*` / `--json`，视为 `POST`；否则默认 `GET`
   - header：每个 `-H` / `--header`（`Name: value`）
   - body：`-d` / `--data` / `--data-raw` / `--data-binary` / `--json`；能解析 JSON 则记字段名
   - Content-Type：来自 header，或 `--json` 时记为 `application/json`
3. **鉴权**：识别 `Authorization` / `token` / `X-Token` 等；**产物与清单不写真实 token**
4. **用途猜测**：同 [parse-har.md](parse-har.md)（create / get / delete / login）
5. **多条 curl**：按文件或粘贴顺序排列；若后一条 path/body 含前一条里出现过的数字 id / UUID，可标弱串联（curl 通常无响应体，串联弱于 HAR，交付假设写一句）
6. **去重**：同一 `METHOD + path` 保留 body 字段更完整的一条
7. **脱敏**：生成 Postman / Python / `.env` 时 token 用占位；交付假设写「鉴权从 curl 识别，请本地填 SEED_TOKEN」

## 与其它输入混用

| 组合 | 处理 |
|---|---|
| 仅 curl | 按仅接口：默认 Postman + Excel + Python；禁止出 SQL |
| curl + 接口文档 | 以 OpenAPI/文档字段约束为准，curl 补真实 path、header、body 样例 |
| curl + HAR | 去重合并；HAR 可补响应 id 串联，curl 补手工精选请求 |
| curl + 表结构 | 接口产物 + SQL |

## 勾选清单示例

```
可造数范围（来自 curl，回复序号即可）：
1. 公寓：POST /apartment
2. 房间：POST /room/create（依赖公寓，弱串联）
3. 串联：公寓 → 房间（推荐）
4. 都要

画像默认：正常 + 异常，各 1 条。要改请一并说明。
```
