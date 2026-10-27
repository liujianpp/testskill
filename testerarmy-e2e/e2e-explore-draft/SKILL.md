---
name: e2e-explore-draft
description: >-
  用 tester-army/e2e 的 e2e explore，根据需求文档、测试用例或网站地址探索界面，
  再生成 *.e2e.ts 测试草稿（默认不执行）；多条需同一账号的已登录流程时用 session
  复用登录态。在用户要探索页面、从 PRD/用例/URL 生成 e2e 草稿、或提到 explore
  写脚本时使用。
disable-model-invocation: true
---

# 探索界面并生成 e2e 草稿

在**用户的应用目录**里用 [tester-army/e2e](https://github.com/tester-army/e2e) 做 `e2e explore`，再把走通路径写成测试草稿。不在 skill 目录安装 `e2e`。

API、配置和 CLI 以应用目录已安装包的 `npx e2e guide` 为准；不一致时以包为准。charter、草稿模板、登录态复用与 explore 产物字段见 `<skills-root>/reference.md`。

本 skill **默认不跑** `e2e run`。执行交给 `e2e-run`（跑完会出报告）；失败修复交给 `e2e-fix`；也可单独用 `e2e-report` 再导出报告。

## 先读一篇说明

动手前，在应用目录按当前要做的事只读一篇：

- 没有 `e2e.config.ts` / `e2e.config.mts`，或模型鉴权未就绪：先走 `e2e-init`（本 skill 不直接 `npx e2e init`）
- 探索：`npx e2e guide explore`
- 写草稿：`npx e2e guide writing-tests`
- 要用 `agent.*`：`npx e2e guide agent`

## 先看输入

1. **有需求或用例**（可同时给地址）→ 拆成 1–N 条一句 charter，再 explore。
2. **只有页面地址** → charter 围绕该入口的主成功路径。
3. **都没有** → 只问需求/用例或地址，不探索、不写码。

用例/需求是用户给出的步骤、预期或功能说明。页面上自己看到的内容不算用例。

## 应用目录就绪

没有 `e2e.config.ts` / `e2e.config.mts`：引导用户使用 **`e2e-init`**（选厂商、生成脚手架、设 API Key），本 skill **不要**直接跑 `npx e2e init`。

explore 前若模型鉴权明显缺失（`.env` / 环境变量未设对应 Key、或上次出现 `MODEL_PROVIDER_FAILED` / Unauthenticated）：停下来提示先完成 `e2e-init` 或在 `.env` 填 Key，不要继续 explore。

explore 需要配置里有 target，以及带可用 `model` 的 agent。密钥从 `.env` / 环境变量读取，不写进测试或 config 明文。

## 登录态是否复用

落草稿 / 跑后续业务 explore 前判断：

- **复用**：同一 `credentials` 账号下，≥2 条业务主路径都需要先登录（Web，且引擎支持 `test.setup` / `session`）。
- **不复用**：只测登录本身；不同角色；仅 1 条已登录用例；引擎无 session（如 Mobile）。

## 探索

1. 按 `<skills-root>/reference.md` 把输入写成一句一条的 charter（区域 + 姿态）。
2. 每条 charter 在应用目录跑一次。先读 `.env` 的 **`E2E_HEADED`**（`1`/`true`/`yes` → 加 `--headed`；`0`/`false`/未设 → 无头）。用户本轮口头要求有头/无头时以口头为准：

```bash
npx e2e explore '<charter>' --max-steps 8
# 有头时再加 --headed
npx e2e explore '<charter>' --max-steps 8 --headed
```

项目若有 `npm run explore`（`scripts/e2e.mjs`），会按 `.env` 自动带 `--headed`；参数接在 `--` 后。另可加 `--session <name>`、`--output <dir>`、`--target <id>`。包管理器是 pnpm / bun 时用 `pnpm exec e2e explore` / `bunx e2e explore`（同样按 `E2E_HEADED` 决定是否加 `--headed`）。

3. **登录后多条业务路径（复用）**：仅登录 charter 成功后，先按 reference 落 `test.setup`（`session.save('<name>')`），再跑业务 explore（`--headed` 规则同上）：

```bash
npx e2e explore '<业务 charter>' --session <name> --max-steps 8
```

业务 charter **不要**再要求重新登录。

4. 读终端 Findings / Assessment，以及默认 `.e2e/report.json` 里的 `run.explore`（字段见 `<skills-root>/reference.md`）。
5. 遇到付费、删除、提交真实订单等不可逆操作：停下来问，不继续编 charter 去点。
6. 账号：用户已给则用配置 `credentials` / `--session`；没给且必须登录才停下来问，不编造密码。

## 落草稿

把「走通路径 + 可断言结果」写成应用已有测试目录下的文件；没有约定时用 `tests/<流程>.e2e.ts`。

- 一条主路径或一条用例对应一个 `test`。
- finding 的 `reproduction` → `agent.act` 或 `screen.*`；`expected` → 断言。
- 已知字段、按钮文案：优先 `screen` + `expect`。多步才完成的一个结果：一次 `agent.act`，紧跟一条断言。
- **`agent.act('…')` / `agent.assert('…')` 提示词默认中文**；UI 控件名保持屏幕原文（如「新建项目」）；`{name}` 等 params 占位不变。
- 文件头注释标明 `draft`（来自 explore，定位器可能需二次核对）。模板见 `<skills-root>/reference.md`。
- 每个 `agent`、`screen`、`expect` 都要 `await`。密码只用 `credentials`，不写明文。

**满足「复用」时**（模板见 reference）：

1. 写 `tests/auth.setup.e2e.ts`（或项目约定名）：`test.setup(..., { sessions: ['<name>'] }, …)`，用 `fill` 填密，断言离开登录页后 `session.save('<name>')`。
2. 业务 `test(..., { session: '<name>' }, …)` 开头 `app.open` 业务入口，**禁止**再写登录步骤。
3. 原「仅登录」草稿收成 setup（或删除），避免双份填密。

**不要**在本 skill 里自动 `e2e run`。

## 对用户交代

说明：用了哪些 charter、草稿文件路径、explore 的 issue/warning 摘要（含证据路径若有）、**是否复用 session**（是则给出 setup 路径与 session 名）。并提示下一步：用 `e2e-run` 执行（自动出报告）；失败用 `e2e-fix`；需要时可再调 `e2e-report`。
