---
name: api-test-runner
description: Read user-specified Excel or CSV test case files, execute API tests via pytest, and generate Allure reports. This skill only runs tests and reports pass/fail with modification suggestions; it does not edit case content. Use when users want to run Excel/CSV-based API tests or generate Allure reports from case-driven tests.
---

# Excel/CSV 驱动接口测试执行

读取用户指定的 **Excel 或 CSV** 测试用例文件，执行 pytest 并生成 Allure 报告，支持前置依赖（如登录获取 cookie）。执行结束后将「运行结果」写回原文件。

## 原则

- **仅关注执行**：本 skill 只负责读取 Excel/CSV → 执行测试 → 写回运行结果 → 生成 Allure，不解析或改写用例设计。
- **不修改用例内容**：不替用户修改用例文件（如 JSON/Excel）中的路径参数、请求体、预期状态码等；失败时只反馈结果与修改建议，由用户自行改用例或环境。

## 输入方式

用户提供用例文件路径（支持 **.xlsx** 与 **.csv**），格式与 [api-test-generator](api-test-generator) 输出一致。路径参数与请求体均需填写精确参数，runner 不支持 __RANDOM__ 等占位符。

## 工作流

### Step 1：读取 Excel 或 CSV

- **Excel (.xlsx)**：使用 openpyxl 读取第一个 sheet，第一行为表头，数据从第二行起
- **CSV**：使用标准库 csv 读取，UTF-8 编码，第一行为表头
- 仅执行「是否运行」为 是/1/Y/true 或空的行
- 列定义见 [references/excel-format.md](references/excel-format.md)

### Step 2：执行测试

- 通过 `pytest_generate_tests` 将每行用例参数化到 `test_api_row`
- 若「前置依赖」为 `user_login`，session 开始时执行登录（config/dependencies.yaml），将 token/cookie 注入后续请求
- `run_tests.py` 在项目根目录 chdir 后调用 pytest 执行本 skill 下的 `scripts/test_api.py`（同目录 `conftest.py` 提供 fixture 与结果写回）

### Step 3：写回运行结果并生成 Allure 报告

- 按「用例ID」将 PASS/FAIL 写回用例文件的「运行结果」列（Excel 或 CSV）
- Allure 报告生成方式见下
- **使用本 skill 时**：执行完成后只做结果汇总与修改建议，不主动编辑用例文件（路径参数、请求体等）

```bash
allure generate allure-results -o allure-report --clean
allure serve allure-results  # 或直接打开查看
```

## 执行后输出

执行结束后应输出：

- **通过/失败汇总**：共 N 条，通过 M 条，失败 K 条；并列失败用例的用例ID与简要原因（如预期状态码 vs 实际状态码、响应摘要）。
- **修改建议**（若有失败）：根据失败原因给出具体建议，供用户自行修改用例或检查环境（例如「TC_010 预期 200 实际 404，接口按 UUID 查询用户，请将路径参数 id 改为环境中存在的用户 UUID」）。**不要**替用户编辑用例文件。

## 入口脚本

```bash
python scripts/run_tests.py --csv <用例文件路径> [--base-url <url>] [--serve]
```

示例（支持 .xlsx 与 .csv）：

```bash
python scripts/run_tests.py -e docs/user_api_cases.xlsx --base-url http://localhost:8080 --serve
python scripts/run_tests.py -e docs/user_api_cases.csv --base-url http://localhost:8080
```

## 配置

- **依赖定义**：项目根目录 `config/dependencies.yaml`，定义 user_login 的 URL、body、extract 规则
- **敏感信息**：账号密码从环境变量 `TEST_USER`、`TEST_PASS` 读取，参考 `config/.env.example`
- **BASE_URL**：环境变量或 `--base-url` 参数

## 资源

- **Excel/CSV 格式**：[references/excel-format.md](references/excel-format.md)（支持 .xlsx 与 .csv）
- **实现位置**：本 skill 的 `scripts/` 下含 [conftest.py](scripts/conftest.py)（auth_cookie、Excel/CSV 读取与结果写回）与 [test_api.py](scripts/test_api.py)（用例逻辑），自包含，不依赖项目根 `tests/`
- **测试入口**：[scripts/run_tests.py](scripts/run_tests.py)
