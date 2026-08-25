---
name: api-test-config
description: 辅助用户编写 config/dependencies.yaml 前置依赖配置。根据用户描述的登录或其它前置接口（路径、请求体、响应结构）生成符合约定的 YAML 片段或完整 dependencies 块。适用于配置 CSV 接口测试的前置依赖、登录接口不是 /auth/login 等场景。
---

# 前置依赖配置助手

辅助用户编写或修改 `config/dependencies.yaml`，供 api-test-runner 在执行 CSV 用例前调用前置接口（如登录）并注入 token 等产出。

## 何时使用

- 用户要配置/新增前置依赖（登录、获取 tenant token 等）
- 登录或其它前置接口路径不是默认的 `/auth/login`
- 用户提供接口文档片段或口头描述，需要产出可直接粘贴的 YAML

## 工作流

1. **获取信息**：从用户处获取前置接口信息（可来自接口文档或用户描述）：
   - 接口路径（如 `/api/v2/signin`、`/sso/login`）
   - 请求方法（GET/POST 等）
   - 请求体字段（如 username、password；敏感信息用环境变量）
   - 响应中需要提取的字段及 JSONPath（如 token 在 `data.accessToken` → `$.data.accessToken`）
2. **阅读格式约定**：阅读 [references/dependencies-spec.md](references/dependencies-spec.md)，确保输出符合项目约定。
3. **生成 YAML**：生成或补全 `dependencies` 块，写入或合并到项目根目录的 `config/dependencies.yaml`。
4. **配置 .env.example**：
   - 路径：项目根目录下的 `config/.env.example`。
   - 必须包含 `BASE_URL`（示例值如 `http://localhost:11011`，可带简短注释）。
   - 根据本次生成/更新的 `dependencies.yaml` 中所有依赖的 `body` 里出现的环境变量占位（如 `${TEST_USER}`、`${TEST_PASS}`、`${ADMIN_USER}` 等），在 `.env.example` 中列出对应键与示例值（示例值用占位或假数据，不要真实密码）。
   - 若文件不存在则创建；若已存在则合并：只新增当前 YAML 中用到的、且 `.env.example` 里尚未存在的变量，并保留原有注释与顺序；可在一段注释下集中「前置依赖相关」变量。
4.1. **配置 .env（可选）**：
   - 路径：`config/.env`。
   - 若 `config/.env` **不存在**：从 `config/.env.example` 复制一份生成 `.env`，作为本地配置起点（用户后续可改真实值）。
   - 若 `config/.env` **已存在**：仅追加「当前 YAML 中用到的、且 .env 中尚未存在的」变量名，值为空或与 .env.example 相同的占位，避免覆盖用户已有敏感配置。
5. **提醒用户**：
   - 已在 `config/.env.example` 中配置了本次依赖所需的变量；若使用 `config/.env`，请将示例值改为实际值并注意不要提交敏感信息。
   - CSV 中「前置依赖」填依赖名（如 `user_login`），「注入方式」填如 `Header:Authorization:Bearer {token}`，占位符与 `extract` 的键名一致。

## 输出约定

- URL 使用 `${BASE_URL}` 拼接路径，例如：`${BASE_URL}/api/v2/login`。
- `extract` 的键名（如 `token`、`userId`）与 CSV「注入方式」中的占位符 `{token}`、`{userId}` 一一对应。
- 可配置多个依赖（如 `user_login`、`admin_login`），每个依赖名在 CSV 中单独引用。

## 资源

- **格式与示例**：[references/dependencies-spec.md](references/dependencies-spec.md)
