# 接口文档解析

从用户提供的接口材料抽出造数所需信息。只抽取**会写入数据**的接口，以及配套的查询/删除接口。

## 支持的材料

- OpenAPI / Swagger（JSON 或 YAML）
- Markdown / Word / 表格形式的接口说明
- 接口截图、抓包截图
- 已有 Postman Collection（抽取 path、method、body，不要原样复述无关请求）
- **HAR 抓包**（`.har`）：按 [parse-har.md](parse-har.md) 过滤噪声、去重后纳入同一套抽取与勾选流程
- **curl 命令**（粘贴或 `.sh` / `.curl` / `.txt`）：按 [parse-curl.md](parse-curl.md) 解析后纳入同一套流程

多种格式混给时，以 OpenAPI 为准，其余补字段说明；有 HAR / curl 时用其补真实调用顺序、header 与 body 样例。

## 抽取字段

每个候选接口记录：

| 项 | 说明 |
|---|---|
| 模块 | 用户、订单等 |
| method + path | 如 `POST /api/v1/users` |
| 用途 | `create` / `get` / `delete` / `cancel` / 其他 |
| 鉴权 | header 名、是否要 token；写入 environment 变量 |
| Content-Type | 默认 `application/json` |
| 必填 body/query | 名称、类型、约束（长度、枚举、格式） |
| 可选字段 | 造正常数据时填有意义的值；造异常数据时可省略或给非法值 |
| 响应 id | 如 `data.id`、`data.userId`；用于写入 collection 变量 |

## 识别造数相关接口

优先纳入：

- `POST`/`PUT` 创建或录入类（造数主路径）
- 对应 `GET`（校验）
- 对应 `DELETE`、取消、下线、作废（回滚）

不要为列表查询、纯配置读取、登录以外的鉴权探测生成造数请求。若造数需要登录，单独放一条「准备-登录」在造数文件夹之前，token 写入 `{{token}}`。

## 依赖与串联链路

有创建依赖时按「先主后从」排序，例如：公寓 → 房间 → 租客 → 入住。

**识别串联链路的来源**（任一即可）：

- 文档中的推荐调用链 / 联调示例步骤
- 某接口响应 id（如 `data.id`）被后续请求 body/path 消费
- 必填字段为外键或 `xxxId`（如 `apartmentId`、`tenantId` + `roomId`）

把文档里**最长主路径**列为一条「串联」勾选项（标推荐）。链上可并行、互不依赖的步骤（如建房与建租客）仍写在同一条链里；生成时允许并行，最终在汇合点（如入住）绑定 ID。

在勾选清单里同时给出：单资源、串联链路、都要。用户只选了子资源时，自动补上缺失的父资源，并在交付假设里说明。

## 勾选清单示例

向用户展示时用短列表，不要贴完整 schema：

```
可造数范围（回复序号即可）：
1. 公寓：POST /apartment
2. 房间：POST /room/create（依赖公寓）
3. 租客：POST /tenant/create
4. 入住：POST /tenant/lease（依赖房间+租客）
5. 串联：公寓 → 房间 → 租客 → 入住（推荐）
6. 都要

画像默认：正常 + 异常，各 1 条。要改请一并说明。
```

选了串联（或「都要」覆盖整条链）时：同一条画像数据贯穿整条链，上一步产出的 id 传给下一步；不要为每个接口各造互不相关的独立记录。
## 缺字段时的取值

可搜字段带前缀 `QA_YYYYMMDD_`；**唯一字段用随机，避免重复造数冲突**。

- 姓名 / 昵称 / 备注 / 公寓名：`{prefix}{语义}{n}` 或 `{prefix}{语义}_{rand}`
- 手机：`1` + 10 位随机数字（如 `1` + `secrets.randbelow(10**10)` 补零）；禁止固定 `13800000001` 这类写死号
- 邮箱：`{prefix}{rand}@qa.local`
- 身份证（18 位）：地区码（如 `110101`）+ 随机数字补足 17 位 + 末位数字或 `X`；**每次 seed 重新随机**，禁止固定尾号序号
- 用户名 / 业务单号：`{prefix}{模块}_{rand}` 或 `{prefix}{模块}{n}_{rand}`
- 同公寓房间号：`{floor}{两位随机}` 或 `R{rand}`，保证同公寓内不重复
- 密码：`Qa@123456`（写入交付清单）
- 金额：正常用普通正数；异常用 `0`、负数或超上限（按文档约束）
- 枚举：正常取文档第一个合法值；异常取空串或不在枚举中的值
- 时间：正常用当前时间；过期类异常显式给过去时间

Python 示例：

```python
import secrets

def rand_digits(n: int) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(n))

phone = "1" + rand_digits(10)
id_card = "110101" + rand_digits(11) + rand_digits(1)  # 18 位
email = f"{PREFIX}{secrets.token_hex(4)}@qa.local"
```
