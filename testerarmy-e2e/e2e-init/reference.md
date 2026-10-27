# 厂商 / 引擎模板与环境变量

配合 `<skills-root>/SKILL.md`。模型 id 以厂商文档为准，可在 `e2e.config.ts` 中修改。密钥经 `.env` / 环境变量注入；**不**把真实 Key 写进 config 或提交进 git。

改写 `e2e.config.ts` 时按序拼接：`process.loadEnvFile('.env')` + **厂商块** + **引擎块**（替换 init 默认的 `gateway(...)`）。

## 最小 `package.json`（无则新建，已有不覆盖）

在应用目录尚无 `package.json` 时写入后再跑 `e2e init`：

```json
{
  "name": "<目录名或 e2e-app>",
  "private": true,
  "type": "module",
  "version": "0.0.0"
}
```

- `name`：取应用目录 basename；含非法 npm 名字符时改用 `e2e-app`。
- 已有 `package.json`：**不要**覆盖。

## `.gitignore`（默认创建 / 合并）

无文件则新建；已有则追加缺失行：

```
.env
node_modules/
.e2e/
```

## `scripts/e2e.mjs` / `e2e-report.mjs`（从 skill 复制到应用）

- **真相源**：`<skills-root>/scripts/e2e.mjs` 与 `e2e-report.mjs`（本 skill，勿在 skill 目录跑 e2e）。
- **应用副本**：脚手架时复制到应用目录 `scripts/`（已有则不覆盖），供 npm 调用。
- `e2e.mjs`：`process.loadEnvFile('.env')`；`E2E_HEADED` 为 `1`/`true`/`yes` 时自动追加 `--headed`；`run`/`explore` 结束后若有 `.e2e/report.json` 则调用同目录 `e2e-report.mjs`。
- `e2e-report.mjs`：读 `report.json`（及失败产物路径），写出 `reports/e2e-report-<日期>[.HHmm].md` + `.html`（与 e2e-report skill 模板同形；有 video 则页内可播）。

`package.json` 的 `scripts`（已有同名键不覆盖）：

```json
{
  "scripts": {
    "test:e2e": "node scripts/e2e.mjs run",
    "explore": "node scripts/e2e.mjs explore",
    "report:e2e": "node scripts/e2e-report.mjs"
  }
}
```

用法：`npm run test:e2e -- tests/foo.e2e.ts`（跑完自动出报告）；`npm run report:e2e`（仅重生成）；`npm run explore -- 'charter…' --max-steps 8`。

## `.env`（默认创建 / 补键）

e2e runner **不**自动加载 `.env`，须在 `e2e.config.ts` 顶部调用 `process.loadEnvFile('.env')`。

无 `.env` 则新建；已有则只补缺失键。API Key 与未提供的密码留空，由用户本地填写。

**注释（强制）**：写出或补键时必须带 `#` 行注释（用途 + 可选取值）。新建按下方完整模板；只补缺失键时，每个新键上方也要写对应注释，不要追加裸 `KEY=`。

**Web** 示例（厂商 Key 名换成当前所选厂商）：

```
# 厂商 API Key（e2e agent 模型；本地填写，勿提交真实值）
DEEPSEEK_API_KEY=

# 被测应用地址（e2e.config.ts → targets[].app.url）
APP_URL=http://localhost:3000

# admin 等账号密码（credentials；也可用 E2E_USER_<NAME>_PASSWORD）
E2E_USER_ADMIN_PASSWORD=

# 有头浏览器：1/true/yes → scripts/e2e.mjs 追加 --headed；0/false/未设 → 无头
E2E_HEADED=1

# 录像：off | on | retain-on-failure | on-first-retry | on-all-retries
# 由 e2e.config.ts 读取；默认 retain-on-failure（失败才保留 video.webm）
E2E_VIDEO=retain-on-failure

# 逐步文字 trace.md：取值同 E2E_VIDEO；默认 retain-on-failure
# 不是 Playwright Trace Viewer，只是 Markdown 步骤页
E2E_TRACE=retain-on-failure
```

**Mobile** 示例（不写 `APP_URL`）：

```
# 厂商 API Key（e2e agent 模型；本地填写，勿提交真实值）
DEEPSEEK_API_KEY=

# 被测 App bundleId（e2e.config.ts → mobile app.bundleId；可先留空用 config 占位）
E2E_BUNDLE_ID=

# admin 等账号密码（credentials；也可用 E2E_USER_<NAME>_PASSWORD）
E2E_USER_ADMIN_PASSWORD=

# 有头：1/true/yes → scripts/e2e.mjs 追加 --headed；0/false/未设 → 无头
E2E_HEADED=1

# 录像：off | on | retain-on-failure | on-first-retry | on-all-retries（config 读取）
E2E_VIDEO=retain-on-failure

# 逐步文字 trace.md：取值同 E2E_VIDEO（非 Playwright Trace Viewer）
E2E_TRACE=retain-on-failure
```

- 厂商 Key 名用下方「厂商一览」对应列；只写当前所选厂商那一行即可（注释里的 Key 名一并改掉）。
- Web：`APP_URL` 用户已给用用户值；未指定则默认 `http://localhost:3000`（**不要**为此追问用户）。
- Mobile：写空键 `E2E_BUNDLE_ID=`；config 占位见「引擎块」；**不要**追问 bundleId。
- `E2E_HEADED`：默认 `1`（有头）。`1`/`true`/`yes` → skill / 应用 `scripts/e2e.mjs`（由本 skill 模板复制）给 `e2e run`/`explore` 加 `--headed`；`0`/`false` → 无头。e2e runner **不**直接读此变量。
- `E2E_VIDEO` / `E2E_TRACE`：默认 `retain-on-failure`。e2e **无**内置这两项；须在 `e2e.config.ts` 映射到官方 `video` / `trace`（见 e2e-run reference）。
- 用户已提供某账号密码时，写入对应 `E2E_USER_<NAME>_PASSWORD=`；未提供则空值占位或不写该行。

## 厂商一览

| 选项 | 接入 | 依赖 | 默认 model id | 环境变量 | baseURL |
|------|------|------|---------------|----------|---------|
| DeepSeek | `createOpenAICompatible` | `@ai-sdk/openai-compatible` | `deepseek-flash`（多模态/验证码）；纯文本可用 `deepseek-chat` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/v1` |
| OpenAI | `openai()` | `@ai-sdk/openai` | `gpt-4o` | `OPENAI_API_KEY` | （SDK 默认） |
| Claude | `anthropic()` | `@ai-sdk/anthropic` | `claude-sonnet-4-5` | `ANTHROPIC_API_KEY` | （SDK 默认） |
| 通义千问 | `createOpenAICompatible` | `@ai-sdk/openai-compatible` | `qwen-plus` | `DASHSCOPE_API_KEY` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 智谱 GLM | `createOpenAICompatible` | `@ai-sdk/openai-compatible` | `glm-4-flash` | `ZHIPU_API_KEY` | `https://open.bigmodel.cn/api/paas/v4` |
| 月之暗面 Kimi | `createOpenAICompatible` | `@ai-sdk/openai-compatible` | `moonshot-v1-8k` | `MOONSHOT_API_KEY` | `https://api.moonshot.cn/v1` |

安装示例（仅厂商；引擎包由 `e2e init --engine` 安装）：

```bash
npm install --save-dev @ai-sdk/openai-compatible   # DeepSeek / 通义 / 智谱 / Kimi
npm install --save-dev @ai-sdk/openai               # OpenAI
npm install --save-dev @ai-sdk/anthropic            # Claude
```

## 填 Key（优先 `.env`）

在应用目录 `.env` 填写对应变量后即可。若不用 `.env`，也可：

```bash
export DEEPSEEK_API_KEY=sk-...
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
export DASHSCOPE_API_KEY=sk-...
export ZHIPU_API_KEY=...
export MOONSHOT_API_KEY=sk-...
export APP_URL=http://localhost:5173          # Web only
export E2E_BUNDLE_ID=com.example.app          # Mobile only
export E2E_HEADED=1                           # 1=headed, 0=headless
```

---

## 组合说明

完整 config 结构：

```ts
import type { E2EConfig } from 'e2e';
// + 引擎 import（见引擎块）
// + 厂商 import（见厂商块）

process.loadEnvFile('.env');

// 厂商：const provider = ...（如需要）

export default {
  agents: {
    default: {
      // 厂商：model + system
      // Mobile 另加：tools: mobileTools(device),
    },
  },
  // 引擎：targets（+ Mobile 的 workers: 1）
} satisfies E2EConfig;
```

下方「厂商块」只含 import / provider / `agents.default` 的 model 部分；「引擎块」含 engine import、`targets`，以及 Mobile 的 `tools` / `workers`。拼接时把引擎的 `tools` 并入同一个 `agents.default`。

---

## 引擎块

### Web

```ts
import { web } from '@e2e-dev/web';

// …厂商块…

export default {
  agents: {
    default: {
      // …厂商 model / system…
    },
  },
  targets: [
    {
      engine: web(),
      app: {
        url: process.env.APP_URL ?? 'http://localhost:3000',
      },
    },
  ],
} satisfies E2EConfig;
```

### Mobile

本机 `darwin` → `ios` + 占位 `Settings`；否则 `android` + 占位 `com.android.settings`。

```ts
import { mobile } from '@e2e-dev/mobile';
import { mobileTools } from '@e2e-dev/mobile/tools';

// …厂商块…

const device = mobile({ platform: 'ios' }); // 或 'android'

export default {
  agents: {
    default: {
      // …厂商 model / system…
      tools: mobileTools(device),
    },
  },
  targets: [
    {
      name: 'ios', // 或 'android'
      engine: device,
      app: {
        bundleId: process.env.E2E_BUNDLE_ID ?? 'Settings', // Android 占位：'com.android.settings'
      },
    },
  ],
  workers: 1,
} satisfies E2EConfig;
```

---

## 厂商块

### DeepSeek

```ts
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

const deepseek = createOpenAICompatible({
  name: 'deepseek',
  baseURL: 'https://api.deepseek.com/v1',
  apiKey: process.env.DEEPSEEK_API_KEY ?? '',
});

// agents.default:
// Prefer deepseek-flash when the app has image captchas (vision).
// model: deepseek.chatModel('deepseek-flash'),
// system: 'You are a thorough QA agent. Verify every outcome.',
```

### OpenAI

```ts
import { openai } from '@ai-sdk/openai';

// agents.default:
// model: openai('gpt-4o'),
// system: 'You are a thorough QA agent. Verify every outcome.',
```

### Claude

```ts
import { anthropic } from '@ai-sdk/anthropic';

// agents.default:
// model: anthropic('claude-sonnet-4-5'),
// system: 'You are a thorough QA agent. Verify every outcome.',
```

### 通义千问

```ts
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

const qwen = createOpenAICompatible({
  name: 'dashscope',
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: process.env.DASHSCOPE_API_KEY ?? '',
});

// agents.default:
// model: qwen.chatModel('qwen-plus'),
// system: 'You are a thorough QA agent. Verify every outcome.',
```

### 智谱 GLM

```ts
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

const zhipu = createOpenAICompatible({
  name: 'zhipu',
  baseURL: 'https://open.bigmodel.cn/api/paas/v4',
  apiKey: process.env.ZHIPU_API_KEY ?? '',
});

// agents.default:
// model: zhipu.chatModel('glm-4-flash'),
// system: 'You are a thorough QA agent. Verify every outcome.',
```

### 月之暗面 Kimi

```ts
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

const moonshot = createOpenAICompatible({
  name: 'moonshot',
  baseURL: 'https://api.moonshot.cn/v1',
  apiKey: process.env.MOONSHOT_API_KEY ?? '',
});

// agents.default:
// model: moonshot.chatModel('moonshot-v1-8k'),
// system: 'You are a thorough QA agent. Verify every outcome.',
```

### 完整拼接示例（Web + DeepSeek）

```ts
import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

process.loadEnvFile('.env');

const deepseek = createOpenAICompatible({
  name: 'deepseek',
  baseURL: 'https://api.deepseek.com/v1',
  apiKey: process.env.DEEPSEEK_API_KEY ?? '',
});

export default {
  agents: {
    default: {
      // Prefer deepseek-flash when the app has image captchas (vision).
      model: deepseek.chatModel('deepseek-flash'),
      system: 'You are a thorough QA agent. Verify every outcome.',
    },
  },
  targets: [
    {
      engine: web(),
      app: {
        url: process.env.APP_URL ?? 'http://localhost:3000',
      },
    },
  ],
} satisfies E2EConfig;
```

### 完整拼接示例（Mobile iOS + DeepSeek）

```ts
import type { E2EConfig } from 'e2e';
import { mobile } from '@e2e-dev/mobile';
import { mobileTools } from '@e2e-dev/mobile/tools';
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

process.loadEnvFile('.env');

const deepseek = createOpenAICompatible({
  name: 'deepseek',
  baseURL: 'https://api.deepseek.com/v1',
  apiKey: process.env.DEEPSEEK_API_KEY ?? '',
});

const device = mobile({ platform: 'ios' });

export default {
  agents: {
    default: {
      // Prefer deepseek-flash when the app has image captchas (vision).
      model: deepseek.chatModel('deepseek-flash'),
      system: 'You are a thorough QA agent. Verify every outcome.',
      tools: mobileTools(device),
    },
  },
  targets: [
    {
      name: 'ios',
      engine: device,
      app: {
        bundleId: process.env.E2E_BUNDLE_ID ?? 'Settings',
      },
    },
  ],
  workers: 1,
} satisfies E2EConfig;
```

## credentials（仅用户已给账号时追加）

```ts
credentials: {
  admin: {
    username: 'admin',
    password: () =>
      process.env.E2E_USER_ADMIN_PASSWORD ?? process.env.ADMIN_PASSWORD ?? '',
  },
},
```

优先写入 `.env` 的 `E2E_USER_ADMIN_PASSWORD=`（或 `export` / `ADMIN_PASSWORD`）。不要把密码写进 config。

## 已有 config 时对照 env

| config 里出现的符号 | 需要的环境变量 |
|---------------------|----------------|
| `DEEPSEEK_API_KEY` / `name: 'deepseek'` | `DEEPSEEK_API_KEY` |
| `openai(` / `@ai-sdk/openai` | `OPENAI_API_KEY` |
| `anthropic(` / `@ai-sdk/anthropic` | `ANTHROPIC_API_KEY` |
| `DASHSCOPE_API_KEY` / `name: 'dashscope'` | `DASHSCOPE_API_KEY` |
| `ZHIPU_API_KEY` / `name: 'zhipu'` | `ZHIPU_API_KEY` |
| `MOONSHOT_API_KEY` / `name: 'moonshot'` | `MOONSHOT_API_KEY` |
| `gateway(`（init 默认未改） | `AI_GATEWAY_API_KEY` |
| `APP_URL` / `web()` | `APP_URL`（可选，有默认） |
| `E2E_BUNDLE_ID` / `mobile(` | `E2E_BUNDLE_ID`（可选，有占位） |
| （skill / 应用 `scripts/e2e.mjs`） | `E2E_HEADED`（`1` 有头，`0` 无头） |
| `video` / `trace`（config 读 env） | `E2E_VIDEO` / `E2E_TRACE`（默认 `retain-on-failure`） |
