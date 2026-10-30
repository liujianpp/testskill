---
name: seed-test-data
description: 根据接口文档、HAR 抓包、curl 命令或表结构生成可执行测试数据。支持 Postman Collection JSON、SQL（新增+回滚，用户手工执行）、Excel 造数表、可执行 Python HTTP 造数脚本；生成前咨询用户产物格式。Use when the user asks for 造数、测试数据、造账号、造订单、准备用例数据、Postman 造数、seed SQL、回滚 SQL、Excel 造数表、Python 造数脚本、HAR、.har、抓包造数、curl、复制为 cURL, or provides API docs / HAR / curl / DDL / table schema for test data.
---

# 测试造数

根据用户提供的接口文档、HAR 抓包、curl 命令或表结构，确认范围与产物格式后，生成可直接使用的 Postman Collection、SQL 文件（含回滚，由用户手工执行）、Excel 造数表和/或可执行 Python HTTP 脚本。

解析与产物细节分别见：
- [references/parse-api.md](references/parse-api.md)
- [references/parse-har.md](references/parse-har.md)
- [references/parse-curl.md](references/parse-curl.md)
- [references/parse-schema.md](references/parse-schema.md)
- [references/postman-template.md](references/postman-template.md)
- [references/sql-template.md](references/sql-template.md)
- [references/excel-template.md](references/excel-template.md)
- [references/python-template.md](references/python-template.md)

## 硬规则

- 先解析输入，再让用户勾选范围与格式；禁止一上来开放追问「你想造什么」
- 禁止连生产库；本 Skill **只出文件，不执行 INSERT/DELETE、不调真实接口、不替用户跑造数脚本或 SQL**
- 表结构产物必须成对：`seed` + `rollback` SQL 文件；缺回滚不算完成；**禁止**再生成 `*-db-seed.py` 等连库 Python 脚本
- 回滚只删本次标识数据，禁止 `TRUNCATE`、禁止无 WHERE 的 `DELETE`；SQL 回滚 **优先本批精确业务键 `IN (...)`**，禁止用 `LIKE 'QA_YYYYMMDD_%'` 做 DELETE（易误删同日前缀其他数据）
- 接口文档若无删除/取消类接口，回滚文件夹可空 / Python `rollback` 须明确失败提示，并在说明里写明无法接口回滚
- **产物格式以用户勾选为准**；未选时才走推荐默认
- 选了 Postman / Python 但无接口文档、无 HAR、无 curl → 不出并说明；选了 SQL 但无表结构 → 不出并说明；仅接口文档 / 仅 HAR / 仅 curl 时**禁止**出 SQL；Excel 始终可出
- 对话里只给路径和清单，不要贴整份 JSON/SQL/Excel/Python/HAR/curl 内容

## 默认假设

信息不足时按下列默认执行，并在交付说明里用 1–2 句写明；不要连环确认。

| 项 | 默认 |
|---|---|
| 范围 | 能识别出主链路时选该**串联链路**；否则文档中的主资源（创建类接口 / 核心业务表） |
| 画像 | 正常 + 1 条异常 |
| 数量 | 每种画像 1 条 |
| 标识前缀 | `QA_YYYYMMDD_`（当天日期） |
| 输出目录 | 用户指定，否则当前工作目录 |
| 产物格式（未勾选时） | 仅接口 / 仅 HAR / 仅 curl → Postman + Excel + Python(HTTP)；仅表结构 → SQL + Excel；接口侧 + 表结构 → Postman + SQL + Excel + Python(HTTP) |

## 工作流程

### 1. 识别并解析输入

判断用户给的是 **接口文档**、**HAR**、**curl**、**表结构**，或其中组合。

| 输入 | 解析目标 |
|---|---|
| Swagger / OpenAPI、Markdown 接口说明、抓包/文档截图、已有 Postman | 模块、方法、路径、必填字段、鉴权、是否有删除/取消接口 |
| `.har` 抓包 | 同上；先过滤静态资源与 OPTIONS，再按 METHOD+path 去重；细则见 [parse-har.md](references/parse-har.md) |
| curl 粘贴或 `.sh` / `.curl` / `.txt` | 同上；拆命令抽 method/path/header/body；细则见 [parse-curl.md](references/parse-curl.md) |
| DDL、`SHOW CREATE`、字段说明表 | 表、主键、唯一、非空、默认值、外键/关联 |

解析后得到「可造数清单」（模块 / 接口 / 表）及可识别的**串联链路**。字段不明就标「待确认」并给合理示例值，不要停下来反复问。

大 HAR / 大段 curl 先跑摘要再勾选（勿贴全文）：

```bash
python3 "$SKILL_DIR/scripts/summarize_har.py" <file.har>
python3 "$SKILL_DIR/scripts/summarize_curl.py" <file.sh|.curl|.txt>
```

接口解析细则见 [references/parse-api.md](references/parse-api.md)；HAR 见 [references/parse-har.md](references/parse-har.md)；curl 见 [references/parse-curl.md](references/parse-curl.md)；表结构见 [references/parse-schema.md](references/parse-schema.md)。

### 2. 勾选范围与格式（只问这一次）

把清单整理成选项，一次抛出，等用户回复后再生成：

1. **范围**（可多选；三类选项一次抛出）：
   - **单资源**：各模块 / 接口 / 表，仍可单独勾选
   - **串联链路**（有依赖时**必须**列出）：把文档主调用链或外键链合成一项，例如 `公寓 → 房间 → 租客 → 入住`；标「推荐」
   - **都要**：全部单资源（含未进链路的独立接口/表）
2. **画像**：只要正常，或正常+异常，或正常+边界+异常
3. **数量**：每种画像几条（默认 1）
4. **产物格式（可多选）**：
   - Postman Collection（需接口文档 / HAR / curl）
   - SQL 新增 + 回滚（需表结构；用户在测试库手工执行，不出连库脚本）
   - Excel 造数表（接口 / HAR / curl / 表结构都可以）
   - Python HTTP 脚本（需接口文档 / HAR / curl；`script/{场景}-api-seed.py`）

用户已在首条消息里写清范围与格式时，跳过本步直接生成。未选格式时用上方推荐默认，并在交付里写明假设。

**串联与补全规则**：

- 选了串联链路：同一条画像数据贯穿整条链（一条「正常」= 一公寓 + 一房间 + 一租客 + 一入住，ID 互指）；不要拆成互不相关的独立记录
- 用户只选子资源时，自动补上链路前置（如只选入住 → 补公寓、房间、租客），交付假设里写一句
- 链路识别与勾选示例见 [references/parse-api.md](references/parse-api.md)、[references/parse-schema.md](references/parse-schema.md)

### 3. 生成产物

标识前缀统一用 `QA_YYYYMMDD_`，**可搜字段**（姓名、备注、公寓名、描述等）带此前缀；SQL 回滚用本批完整业务键精确删除，不用前缀 `LIKE`。

**唯一约束字段必须防重复**（身份证、手机、邮箱、唯一业务单号、同公寓房间号等）：

- **优先随机**：生成时或脚本运行时加入随机段（如 6～8 位十六进制 / 数字），不要写死成固定序号（禁止再现 `110101199001010011` 这类每次相同的值）
- **Python HTTP**：在 `do_seed()` **每次执行时**用 `secrets` 生成唯一值并打印到清单；同一次串联链路内各步共用同一批随机值
- **Postman / SQL / Excel**：写文件时即带随机后缀；交付清单列出本次关键唯一值
- 随机后仍须满足文档格式约束（手机 11 位、身份证 18 位等）

按勾选（或推荐默认）分别生成：

**Postman**（需接口文档 / HAR / curl）

读取 [references/postman-template.md](references/postman-template.md)，写出：

- `{场景}-seed.postman_collection.json`
- `{场景}-seed.postman_environment.json`

Collection 必须含文件夹：`造数`、`校验`（有 GET 才写）、`回滚`（有删除/取消接口才写请求）。请求按依赖 / 串联链路排序（先主数据，后从属数据）；选了串联时上一步 id 写入变量供下一步引用。

**SQL**（需表结构；用户手工执行）

读取 [references/sql-template.md](references/sql-template.md)，写出：

- `{场景}-01_seed.sql`（按外键正向 INSERT）
- `{场景}-02_rollback.sql`（按外键反向 DELETE；WHERE 用本批精确业务键或主键 `IN (...)`，不用 `LIKE`）

仅写出文件，不替用户连库执行；**不要**另写 `*-db-seed.py`。

**Excel**

读取 [references/excel-template.md](references/excel-template.md)，先写 JSON，再导出：

```bash
python3 "$SKILL_DIR/scripts/export_excel.py" <data.json> <{场景}-seed.xlsx>
```

**Python**（仅 HTTP；需接口文档 / HAR / curl）

读取 [references/python-template.md](references/python-template.md)，**直接写出完整可运行 .py**（不经中间 JSON），统一放到输出目录下的 `script/` 子目录（与 Skill 自带的 `scripts/` 工具目录区分）：

- `script/{场景}-api-seed.py`（`requests`，HTTP seed / rollback）
- 无接口文档、无 HAR、无 curl → 不出任何 `.py`
- **禁止**生成 `script/{场景}-db-seed.py`

连接信息只用环境变量或输出目录下的 `.env`（禁止把真实密码写进脚本 / 提交 `.env`）。出 Python 时一并写出：

- `{输出目录}/.env.example`（占位，可提交）
- `{输出目录}/.env`（本地填写；若仓库有 git，确保 `.env` 在 `.gitignore`）

`.env` 仅含 `SEED_BASE_URL` / `SEED_TOKEN`。脚本内嵌简易 `.env` 加载（无需 python-dotenv）：优先已有环境变量，再读输出根目录 `.env`。

生成后用本 Skill 的校验脚本检查（有对应产物才跑）：

```bash
python3 "$SKILL_DIR/scripts/validate_artifacts.py" <输出目录或文件...>
```

`SKILL_DIR` 为本文件所在目录。校验失败则先改产物，再交付。

### 4. 交付

告知文件路径，并用下面模板给清单（按实际删减）。不要把文件全文贴进对话。

```markdown
## 造数产物
- 场景：{场景}
- 前缀：QA_YYYYMMDD_
- 画像：正常 / 异常（各 N 条）
- 格式：Postman / SQL / Excel / Python(HTTP)
- 假设：{若有}

| 用途 | 关键数据 | 对应请求或表 | 查找方式 |
| --- | --- | --- | --- |
| 正常用户 | QA_..._a1b2c3 | POST /users 或 user | username IN ('QA_..._a1b2c3') |

## 文件
- Postman：{path}/...collection.json ；环境：{path}/...environment.json
- 新增 SQL：{path}/...-01_seed.sql
- 回滚 SQL：{path}/...-02_rollback.sql
- Excel：{path}/...-seed.xlsx
- Python HTTP：{path}/script/...-api-seed.py
- 环境配置：{path}/.env （模板：{path}/.env.example）

## 运行（Python）
```bash
# 编辑 .env 填入 SEED_TOKEN 后：
python3 script/{场景}-api-seed.py seed
python3 script/{场景}-api-seed.py rollback
# 也可不用 .env：export SEED_BASE_URL=... SEED_TOKEN=... 后再执行
```

## 回滚说明
- 接口：{有删除接口 / 无删除接口，无法接口回滚}
- SQL：用户在测试库自行执行 02_rollback.sql（按本批精确业务键删除；务必先于手改数据）；Skill 不连库执行
```
