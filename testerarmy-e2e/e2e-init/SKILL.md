---
name: e2e-init
description: >-
  在应用目录初始化 tester-army/e2e：缺 package.json 时自动生成最小脚手架；用户需选择
  Web 或 Mobile（App）引擎，再从 DeepSeek、OpenAI、Claude、通义千问、智谱 GLM、
  月之暗面 Kimi 中选厂商并自行设置 API Key。在用户要初始化 e2e、选引擎/模型厂商、
  配置 APP_URL 或 E2E_BUNDLE_ID/密钥、或缺少 e2e.config 时使用。
disable-model-invocation: true
---

# 初始化 e2e：选择引擎与模型厂商

在**用户的应用目录**里用 [tester-army/e2e](https://github.com/tester-army/e2e) 搭脚手架，按引擎与厂商写好 `targets` / `agents.default.model`，然后**停手**让用户设置 API Key。不在 skill 目录安装 `e2e`。缺 `package.json` 时先生成最小文件再 init；**用户主要只需选引擎与厂商**。

厂商与引擎模板、依赖、`baseURL`、环境变量见 `<skills-root>/reference.md`。CLI 细节以应用目录 `npx e2e guide setup` / `agent` 为准。

本 skill **不**跑 `e2e explore` / `e2e run`。探索草稿交给 `e2e-explore-draft`；执行交给 `e2e-run`。

## 确认目录

1. 应用目录 = 当前工作区，或用户显式指定路径。
2. **无 `package.json`**：在该目录生成最小 `package.json`（模板见 `<skills-root>/reference.md`），再继续脚手架；**不要**因缺文件只问路径就停。
3. 已有 `e2e.config.ts` / `e2e.config.mts`：说明已初始化。若只是缺 Key：对照 `<skills-root>/reference.md` 说出变量名；缺 `.env` / `.gitignore` 时仍按「脚手架」补齐密钥相关文件，然后停手让用户在 `.env` 填 Key，**不**重复 `e2e init`。

## 选引擎与厂商（未选齐不动手）

向用户一次列出下列两步，**等引擎与厂商都明确后再装依赖、改 config**：

**引擎**

1. Web  
2. Mobile（App）  

**厂商**

1. DeepSeek  
2. OpenAI  
3. Claude  
4. 通义千问  
5. 智谱 GLM  
6. 月之暗面 Kimi  

未选齐：不执行 `e2e init`、不安装 provider、不改 `e2e.config`。不提供 `none` 引擎。

### Mobile 平台（不问）

与官方 `e2e init --engine mobile` 一致：本机 `darwin` → `platform: 'ios'`，否则 `platform: 'android'`。改写 config 时按此写入，**不要**追问 iOS / Android。

## APP_URL / E2E_BUNDLE_ID（不问，静默默认）

**Web**

- 用户已给地址 → 写入 config：`process.env.APP_URL ?? '<该地址>'`。
- 未给 → 不追问，使用 `process.env.APP_URL ?? 'http://localhost:3000'`。

**Mobile**

- 不问 `bundleId`。config：`process.env.E2E_BUNDLE_ID ?? '<占位>'`。
- 占位与官方 scaffold 一致：iOS `Settings`，Android `com.android.settings`。
- `.env` 写空键 `E2E_BUNDLE_ID=`；**不写** `APP_URL`。

## 脚手架

无 e2e 配置时，在应用目录按序执行（按包管理器二选一）：

1. 若无 `package.json` → 写入 `<skills-root>/reference.md` 中的最小模板（已有则不覆盖）。
2. 再执行（`<web|mobile>` 为用户所选引擎）：

```bash
npx e2e init --yes --engine <web|mobile> --skills none --mcp none --install
```

pnpm / bun：`pnpm dlx e2e init ...` / `bunx e2e init ...`（同样带 `--yes --engine <web|mobile> --skills none --mcp none --install`）。

然后按所选厂商与引擎：

1. 安装 `<skills-root>/reference.md` 中的**厂商**依赖（引擎包已由 `--engine` 装好；Mobile 不必再装 `@e2e-dev/web`）。
2. 用同文件中的**厂商块 + 引擎块**改写 `e2e.config.ts`（替换默认 `gateway(...)`）；**文件顶部**加 `process.loadEnvFile('.env')`（e2e 本身不读 `.env`）。完整文件 = `loadEnvFile` + 厂商块 + 引擎块。
3. **credentials**：仅当用户已提供账号时写入；密码用 `() => process.env.E2E_USER_<NAME>_PASSWORD ?? ''`（或 `ADMIN_PASSWORD`），**不写进 config 明文**。
4. **包装脚本（模板在 skill）**：把 `<skills-root>/scripts/e2e.mjs` 与 `<skills-root>/scripts/e2e-report.mjs` **复制**到应用目录 `scripts/`（已有则不覆盖）。在 `package.json` 的 `scripts` 中写入（已有同名键则不改）：`test:e2e` → `node scripts/e2e.mjs run`，`explore` → `node scripts/e2e.mjs explore`，`report:e2e` → `node scripts/e2e-report.mjs`。`run`/`explore` 结束后会自动生成 `reports/e2e-report-*.md|.html`。真相源在 skill；应用内副本供 npm 调用。
5. **默认创建本地密钥文件**（模板见 `<skills-root>/reference.md`）：
   - 无 `.gitignore` 则新建；已有则**追加**缺失项：`.env`、`node_modules/`、`.e2e/`（不覆盖已有内容）。
   - 无 `.env` 则新建；已有则**只补缺失键**，不覆盖用户已填的值。
   - `.env` 写入：厂商对应 API Key 空值；Web 写 `APP_URL`（用户已给或默认 `http://localhost:3000`）；Mobile 写 `E2E_BUNDLE_ID=`（不写 `APP_URL`）；默认写 `E2E_HEADED=1`（有头；改 `0` 则无头，供 `e2e-run` / `e2e-explore-draft` / 应用 `scripts/e2e.mjs` 使用）；默认写 `E2E_VIDEO=retain-on-failure` 与 `E2E_TRACE=retain-on-failure`（供 `e2e.config.ts` 读入官方 `video`/`trace`）；用户已提供的 `E2E_USER_<NAME>_PASSWORD`（未提供则空值占位）。
   - **必须带注释**：新建或补键时，每个键（或键组）上方用 `# …` 写清用途与可选取值；完整注释模板见 `<skills-root>/reference.md`「`.env`」节。禁止只写裸 `KEY=` 无说明。
   - **禁止**把真实 API Key 写进对话、commit，或从别处抄进仓库；Key 由用户本地填入 `.env`。

已有 config、仅缺 Key 时：若缺 `.env` / `.gitignore` / `scripts/e2e.mjs` / 上述 npm scripts，仍按上款补齐，然后停手让用户填 Key（不重复 `e2e init`）。

## 停手

脚手架完成后：

1. 指出 `.env` 路径与待填变量名（见 reference）；可选补充 `export` 示例。
2. 明确「本 skill 到此结束」——**不要**探测 explore，避免未设 Key 时刷 `MODEL_PROVIDER_FAILED`。
3. 提示下一步：在 `.env` 填好 Key 后用 `e2e-explore-draft`；已有测试则用 `e2e-run`。

## 对用户交代

说明：config 路径、**所选引擎**（Mobile 时说明本机平台与 `E2E_BUNDLE_ID`）、所选厂商、`.env` / `.gitignore`、`scripts/e2e.mjs`（及 `test:e2e` / `explore`）、待填环境变量、Web 时的 `APP_URL`、下一步 skill 名。
