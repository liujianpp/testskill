# 04 · 技能详解：ApiAutoTest2.0（接口自动化，6 个技能）

> **一句话**：从后端**源代码**出发，自动提取接口文档 → 设计业务场景 → 生成可执行用例 → 真实调接口执行 → 出漂亮的 Allure 报告。全程围绕一个核心数据文件 **`cases.json`** 衔接。

[← 返回总导读](README.md) | 套件自带文档：[ApiAutoTest2.0/使用说明.md](../../ApiAutoTest2.0/使用说明.md)

---

## 1. 六个技能与流水线

```
api-doc-generator ──► api-scenario-generator ──► api-test-generator ──► api-test-runner ──► api-test-report
  (源码→接口文档)        (文档→场景JSON/Excel)      (场景→cases.json/xlsx)   (执行+结果)       (Allure 查看)
                                                                     ▲
                                                     api-test-config（.env 配置助手，随时可用）
```

| # | 技能 | 职责 | 核心产物 |
|---|------|------|----------|
| 1 | `api-doc-generator` | 扫源码提取 HTTP 接口定义 | `docs/api/api-docs[-<模块>].md` 或 `.json` |
| 2 | `api-scenario-generator` | 设计业务场景（单接口+串联） | `docs/<name>_scenario.json` + `_scenario.xlsx`（评审表） |
| 3 | `api-test-generator` | 场景 → 可执行用例（JSON+Excel 双产出） | `docs/<name>_cases.json` + `_cases.xlsx`（2-sheet） |
| 4 | `api-test-runner` | 执行 cases.json（pytest 参数化） | `allure-results/` + 执行汇总与修复建议 |
| 5 | `api-test-report` | 从已有 allure-results 出报告 | Allure HTML 报告 |
| 6 | `api-test-config` | 维护 config/.env | `config/.env` |

## 2. 核心契约：cases.json（看懂这个就看懂了半个套件）

```json
{
  "dependencies": [
    { "name": "dep_login_admin",
      "request": { "method": "POST", "path": "/auth/login",
                   "body": { "username": "admin", "password": "ENV:ADMIN_PASS" } },
      "assert": { "status": 200, "checks": ["$.code==200 && $.data.token"] },
      "extract": { "token": "$.data.token" } }
  ],
  "cases": [
    { "id": "1", "name": "查询用户信息", "enabled": true,
      "steps": [
        { "name": "step_01_get",
          "request": { "method": "GET", "path": "/api/v1/user",
                       "headers": { "Authorization": "Bearer DEP:dep_login_admin.token" } },
          "assert": { "status": 200, "checks": ["$.code==200"] } }
      ] }
  ]
}
```

**必懂规则**：

| 规则 | 说明 |
|------|------|
| `dependencies` | 前置依赖（如登录拿 token），整个会话先跑，拓扑排序 |
| `request` 与 `steps` 互斥 | 每条 case 至少其一，不能都有 |
| 引用协议 | `ENV:KEY`（环境变量）、`DEP:依赖名.字段`、`STEP:步骤名.字段`；可嵌在字符串里如 `Bearer DEP:auth.token` |
| `id` 规则 | 纯数字字符串序号（`"1","2",...`），不用 `CASE-001` 这类编码 |
| `checks` 表达式 | `== != > >= < <=`，多条件用 `&&` |
| 禁止占位体 | `{"example":1}`、`__RANDOM__` 等假数据不许出现 |
| `db_assert` | 可选数据库断言（查库验证写入结果），默认关闭 |

## 3. 六个技能逐个详解

### 3.1 api-doc-generator（源码 → 接口文档）

- **支持语言**：Java（Spring 注解）/ Go（Gin、net/http）/ Python（Flask/FastAPI/Django）/ Node（Express/Koa/NestJS）
- **范围可指定**：整个项目 / 某个模块目录 / 某 URL 前缀
- **格式**：`md`（默认）或 `json`；统一 Endpoint 模型（path/method/参数/请求体/响应），可当 OpenAPI 中间层
- **必须写文件**（默认 `docs/api/`），不能只在对话里展示
- **话术**：「扫描 backend/user-service 生成接口文档，json 格式」

### 3.2 api-scenario-generator（场景设计）

- 输入：接口文档；产出**固定两份**：`<name>_scenario.json` + `<name>_scenario.xlsx`（给人评审用，含「场景类型」列）
- 覆盖策略：每接口至少 1 条正向；写操作补必填缺失/非法值/资源不存在/业务冲突；数值补边界
- **登录必须沉淀到顶层 dependencies**（如 `dep_login_admin`），不要每条 case 重复写
- 造数三层：准备 → 验证 → 清理；破坏性操作（删除类）放末尾
- **话术**：「根据接口文档设计订单模块的测试场景，输出场景 JSON 和 Excel」

### 3.3 api-test-generator（生成可执行用例）

- 输入：scenario.json + 接口文档 → 由 Agent 按生成规则转换
- 登录去重与 `DEP` 注入：同一用户只留一条登录依赖；测登录本身的场景允许留在 steps
- **DB 断言开关**：`DB_ASSERT_ENABLED=false`（默认）→ 纯 HTTP；启用时必须先跑 `export_db_schema.py` 查表结构再写 SQL
- SQL 里 `STEP:/DEP:/ENV:` 占位符**禁止手工加引号**（runner 自动按类型生成字面量）
- 14 项输出自检全过后才导出 Excel（2-sheet：dependencies 9 列 + cases）
- **话术**：「把 docs/order_scenario.json 转成可执行用例」

### 3.4 api-test-runner（执行）★ 只执行不修改

```bash
python ApiAutoTest2.0/api-test-runner/scripts/run_tests.py --cases-json <cases.json> [--base-url <url>] [--serve]
```

- pytest 参数化执行每条 case；session 先跑 dependencies（拓扑排序）
- **红线**：不自动改断言、请求体、路径参数、依赖引用、账号密码；失败只输出：
  - 失败用例 ID
  - 预期 vs 实际
  - 根因判断
  - 修复建议（**高**=阻断 / **中**=数据不稳定 / **低**=断言优化）
- 敏感信息走环境变量，不写入计划文件
- **话术**：「执行 docs/order_cases.json，base-url https://test.example.com」

### 3.5 api-test-report（Allure 报告查看）

- 不执行测试，只从**已有** `allure-results` 生成/打开报告（默认 `allure serve allure-results`）
- 未装 Allure CLI 时不乱装，只给安装指引
- **话术**：「打开 Allure 报告」

### 3.6 api-test-config（.env 配置助手）

- 维护 `config/.env`：必含 `BASE_URL`；按前置依赖梳理 `LOGIN_USER/LOGIN_PASS` 等变量
- 默认补齐 **DB 断言模板且关闭**：`DB_ASSERT_ENABLED=false` + `DB_HOST/PORT/NAME/USER/PASS/CHARSET`
- 合并策略：只新增缺失变量，保留已有注释与顺序
- **话术**：「帮我配置前置依赖和数据库断言环境变量」

## 4. 完整走一遍（5 句话跑通接口自动化）

```text
1. 「扫描 backend/ 生成接口文档」                          → api-doc-generator
2. 「根据接口文档生成订单模块测试场景」                      → api-scenario-generator
3. （首次先说「帮我配置前置依赖和数据库断言」）→ 「生成可执行用例」 → api-test-config / api-test-generator
4. 「执行 docs/order_cases.json，base-url http://...」      → api-test-runner
5. 「打开 Allure 报告」                                     → api-test-report
```

## 5. 常见问题

**Q：跑挂了它会不会偷偷改我的用例？**
不会，这是硬规矩。它只报「失败 ID / 预期 vs 实际 / 根因 / 建议」，你（或让 AI 按你的指示）改完再跑。

**Q：接口要登录怎么办？**
登录写成 dependency，token 自动 extract，后续接口用 `DEP:登录名.token` 引用，不用每条都登录。

**Q：想验证接口写库的结果对不对？**
开 DB 断言：设 `DB_ASSERT_ENABLED=true` + 配数据库环境变量 + 先跑 `export_db_schema.py`，然后 case 里写 `db_assert`（SQL + 检查条件）。

**Q：和 spectest 的 API 用例什么关系？**
两条独立链路：spectest 从**需求**设计用例（25 列里有 API URL 的行是线索）；ApiAutoTest2.0 从**源码**生成用例（cases.json）。两者**不互转**，只在统一报告（testflow 阶段 4）汇合。

---

*本册基于 ApiAutoTest2.0（2026-10-29 现状）整理。*
