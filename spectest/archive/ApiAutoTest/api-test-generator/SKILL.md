---
name: api-test-generator
description: Generate API test case files from API documentation. The AI designs test cases (normal + abnormal) from the doc and outputs JSON; a script converts the JSON to Excel (or CSV). Use when users ask to generate API test cases, export interface tests to Excel/CSV, or create test case sheets from API docs.
---

# API 测试用例生成

根据接口文档（Markdown 或 OpenAPI）生成符合约定格式的接口测试用例（默认 Excel）。**用例设计由大模型完成，脚本只做 JSON → Excel/CSV 转换。**

## 工作流

1. **大模型**：阅读用户提供的接口文档（Markdown 或 OpenAPI）与 [references/excel-column-spec.md](references/excel-column-spec.md)，思考应覆盖的测试用例（正常场景与异常场景），输出为符合列定义的 **JSON 文件**。生成的用例 JSON 输出到项目 **docs** 目录（如 `docs/<用例文件名>.json`），不要放在 skill 的 references 下。
2. **脚本**：将上述 JSON 转为 **Excel**（推荐）。不解析文档、不内置业务规则。

```bash
python scripts/doc_to_excel.py -i <用例JSON路径> -o <输出Excel路径>
```

示例（JSON 与 Excel 均输出到项目 **docs** 目录）：

```bash
python scripts/doc_to_excel.py -i docs/user_api_cases.json -o docs/user_api_cases.xlsx
```

输入为 **JSON 文件**（数组或 `{ "cases": [...] }`），不再支持 `-f markdown|openapi` 与 `--no-abnormal`。生成用例时，AI 应先阅读接口文档与 excel-column-spec，将 JSON 输出到 **docs**（如 `docs/<用例文件名>.json`），**然后自动执行上述脚本命令**将 Excel 输出到 **docs**（如 `docs/<用例文件名>.xlsx`）；脚本路径为 skill 目录下 `scripts/doc_to_excel.py`，可用 `python3` 调用。

**需要 CSV 时**（可选）：执行 `scripts/doc_to_csv.py`，例如 `python scripts/doc_to_csv.py -i docs/user_api_cases.json -o docs/user_api_cases.csv`。

## 生成约定

生成用例时，**路径参数**、**请求体/参数**一律使用**写死的具体值**（字面量），不要使用 `__RANDOM__`、`__RANDOM_INT__`、`__DEP:依赖名:字段名__` 等占位符。需要唯一值时使用固定示例值（如 `user001`、`test@demo.com`、`1`）。

### 「预期响应校验」字段约定（与 api-test-runner 对齐）

生成 `预期响应校验` 时，请严格遵循以下规则（由大模型执行，脚本只做格式转换）：

- **支持的运算符**：`==`, `!=`, `>`, `>=`, `<`, `<=`。
- **多条件 AND**：使用 `&&` 连接多个子条件（也兼容 `;`，最终 runner 会统一按 AND 处理），例如：

  - `$.code==200 && $.data.token && $.data.userId`
  - `$.code==200 && $.data.list && $.data.total>=0`

- **右值（等号右边）的写法**：
  - 纯数字（整型或小数）直接写：`$.data.id==1`、`$.data.total>=0`。
  - 字符串可以直接写“裸值”（不需要再包一层引号）：  
    - 正例：`$.data.username==user001`、`$.data.email==user001@demo.com`  
    - 如确有需要，也可以写成 `"user001"` 形式，runner 会自动去掉最外层引号，两种写法均兼容。
  - 无运算符时视为“存在性/真值”校验：  
    - 例如：`$.data.token`、`$.data.userId`，表示字段存在且为真。

- **推荐基础模式**：
  - **状态码/业务码**：`$.code==200` 或 `$.code!=0`。
  - **关键字段存在**：`$.data.token`、`$.data.id`、`$.data.list`。
  - **数值比较**：`$.data.total>=0`、`$.data.total>0`、`$.data.age<120`。

> 生成时不要使用形如 `$.data.username=="user001"`（双重引号）这种旧写法，如出现也能被兼容，但推荐统一为 `$.data.username==user001`。

### 常见接口类型的推荐校验模板

生成用例时，大模型应尽量复用下列模板，并根据接口字段名做适配：

- **登录类接口（如 `/auth/login`）**

  - 成功用例：
    - `$.code==200 && $.data.token && $.data.userId`
  - 失败用例（账号/密码错误、缺少字段等）：
    - `$.code==400` 或 `$.code==401`
    - 可选再加：`&& $.msg`

- **获取当前用户（如 `/api/v1/user`）**

  - 成功用例：
    - `$.code==200 && $.data.userId && $.data.username`
  - 未登录/未授权用例：
    - `$.code==401`

- **列表查询（如 `/api/v1/users`）**

  - 成功用例：
    - `$.code==200 && $.data.list && $.data.total>=0`
  - 未授权用例：
    - `$.code==401`

- **详情查询（如 `/api/v1/users/{id}`）**

  - 成功用例（使用文档中的示例 ID，如 1）：
    - `$.code==200 && $.data.id==1`
  - 资源不存在：
    - `$.code==404`

- **创建接口（如 `POST /api/v1/users`）**

  - 成功用例（示例用户名 `user001`）：
    - `$.code==200 && $.data.id && $.data.username==user001`
  - 参数缺失/唯一性冲突等异常用例：
    - `$.code==400`

- **更新接口（如 `PUT /api/v1/users/{id}`）**

  - 成功用例（例如修改邮箱为 `new_admin@demo.com`）：
    - `$.code==200 && $.data.email==new_admin@demo.com`
  - 目标资源不存在：
    - `$.code==404`

- **删除接口（如 `DELETE /api/v1/users/{id}`）**

  - 成功用例：
    - `$.code==200`
  - 目标资源不存在或未授权：
    - `$.code==404` / `$.code==401`

在设计用例时，建议每条用例的 `预期响应校验` 控制在 1～3 个子条件之内（一个状态码/业务码条件 + 一到两个关键字段存在或等值/比较条件），确保表达式既能充分覆盖关键行为，又保持易读、易维护。

## 列定义与 JSON 格式

见 [references/excel-column-spec.md](references/excel-column-spec.md)，含列顺序、JSON 输入格式说明与示例（列定义同时适用于 Excel 与 CSV）。

## 资源

- **列定义与 JSON 格式**：[references/excel-column-spec.md](references/excel-column-spec.md)
- **脚本（主推）**：[scripts/doc_to_excel.py](scripts/doc_to_excel.py)（依赖 openpyxl，输出 Excel）
- **脚本（备用）**：[scripts/doc_to_csv.py](scripts/doc_to_csv.py)（仅依赖标准库 csv，输出 CSV）
