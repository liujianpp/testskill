# Midscene 混合写入规范

稳定 DOM 用 Playwright locator；仅动态/不可定位步骤用 Midscene Instant Actions。禁止 YAML、禁止用 `aiAct` 写整条用例。

## 何时降级 Midscene（满足任一）

| 条件 | 探测方式 | 报告 `reason` 示例 |
|------|----------|-------------------|
| Canvas / WebGL / 图表，操作目标不在 a11y tree | `eval` 查 `canvas`；snapshot 无目标 | `canvas: target not in a11y tree` |
| Closed Shadow DOM | snapshot 看不到内部；`eval` 探测 shadowRoot | `closed-shadow-dom` |
| 跨域 iframe | snapshot 无 iframe 内部节点 | `cross-origin-iframe` |
| snapshot 无可用 `eN` | 对目标操作拿不到 ref | `snapshot: no usable ref` |
| `generate-locator` 仅 hash class / 深层 XPath | 1–4 级均不可用 | `unstable-dom: hash-class/xpath-only` |
| DOM 有节点但无 testid / 无语义 role / id 不稳定 | 按 locator 优先级走完仍不可用 | `unstable-dom: no semantic locator` |
| 图形验证码：字符在图片中，locator 无法读出内容 | snapshot 有 img，无可读文本 | `captcha-image: not machine-readable via locator` |

**不切 Midscene**：普通表单、按钮、表格、链接——只要 testid 或 role+name 可用，即使 class 略动态也写 Playwright。验证码**输入框/登录按钮**仍用 Playwright，仅**读图**用 `aiQuery`。

## 探索阶段（不调用 Midscene Agent）

1. 仍用 `playwright-cli`；禁止探索时跑 Midscene（避免烧模型与 API Key）
2. snapshot 失败或无目标 ref → `screenshot` + `eval` 探测 canvas / shadowRoot / iframe
3. 该步写入报告：`driver: midscene`、降级原因、自然语言 prompt 草稿

### 报告步骤记录格式

```markdown
### Step 4: 点击图表放大

- **driver**: midscene
- **reason**: canvas: target not in a11y tree
- **prompt**: 图表右上角的放大按钮
- **备选 Playwright**: 无（canvas 无 DOM 节点）
```

```markdown
### Step 2: 点击查询

- **driver**: playwright
- **选用**: 优先级 2 — `getByRole('button', { name: '查询' })`
```

## Instant Actions 白名单（生成代码仅用这些）

| API | 用途 |
|-----|------|
| `aiTap(prompt)` | 点击 |
| `aiInput(text, prompt)` | 输入 |
| `aiHover(prompt)` | 悬停 |
| `aiScroll(options, prompt?)` | 滚动 |
| `aiWaitFor(prompt, options?)` | 等待可见状态 |
| `aiAssert(prompt)` | 视觉/语义断言 |
| `aiQuery<T>(prompt)` | 抽取结构化数据后配合 `expect` |

**禁止**：

- `aiAct` / `ai` / `aiAction` 写整段流程（破坏原子性与 1:1 映射）
- YAML 脚本
- Tesseract / 第三方 OCR 库读验证码

**图形验证码（允许 Midscene，通用模式）**：

位数、字符集、失败文案、刷新控件、成功 URL **一律以 explore report 为准**，禁止在 skill/模板里写死业务文案。

- 抽出 `tests/helpers/captcha.ts`（或报告约定路径）：`aiQuery` 读图 + Playwright 填输入框 / 点登录；**禁止**每条用例复制大段 prompt
- reason 示例：`captcha-image: not machine-readable via locator`
- Prompt **规则**（具体句子由报告填）：只描述读哪张图、字符形态、输出格式；明确忽略输入框已有文字与背景噪点；禁止解释性前缀/引号/空格
- 读码前清空输入框；对模型返回做 normalize（去引号与空白，按报告约定的长度/字符集抽取）
- **分层重试**：
  - 读码结果不符合约定格式 → 点刷新再读（默认上限 3）
  - 提交后出现报告记录的「验证码类错误」文案 → 刷新再读再提交（默认上限 5）
  - 出现报告记录的「账号密码错误」或已到登录成功 URL → 立即返回，不再当验证码重试
- 测登录的用例自包含读码；其它模块可继续 `storageState`（不必每条打模型）
- `aiQuery` 结果永不缓存；验证码图每次不同，勿依赖 cache
- **模型须支持视觉/多模态读图**；纯 chat 不可用。缺 key / 模型无视觉能力 → **阻塞**，不走 locator heal

## Fixture 模板

`tests/fixture.ts`（仅当用例含 `driver: midscene` 步时创建）：

```typescript
import { test as base } from '@playwright/test';
import type { PlayWrightAiFixtureType } from '@midscene/web/playwright';
import { PlaywrightAiFixture } from '@midscene/web/playwright';

export const test = base.extend<PlayWrightAiFixtureType>(
  PlaywrightAiFixture({
    waitForNetworkIdleTimeout: 2000,
    cache: true,
  }),
);
```

## 混合 spec 模板

```typescript
import { expect } from '@playwright/test';
import { test } from './fixture';
// import { ChartPage } from './pages/ChartPage';

test.describe('{模块名}', () => {
  test.use({
    storageState: 'tests/explore/{case-name}-auth.json',
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  });

  test('{ID}: {用例名称}', async ({ page, aiTap, aiAssert, aiWaitFor }) => {
    await test.step('操作', async () => {
      // Playwright：稳定 DOM
      await page.getByRole('button', { name: '查询' }).click();
      // Midscene：动态 / canvas
      await aiTap('图表右上角的放大按钮');
      await aiWaitFor('图表已进入全屏', { timeoutMs: 5000 });
    });

    await test.step('验证', async () => {
      await aiAssert('图表已全屏且显示明细坐标轴');
    });
  });
});
```

Page Object：稳定 locator 进 `tests/pages/`；Midscene 调用留在 spec 的 `test.step`（或 PO 方法接收 `aiTap` 等），不要把视觉 prompt 写死在 PO 构造函数。

## 项目配置（有 Midscene 步时）

### 安装

```bash
npm install -D @midscene/web
```

### playwright.config.ts

- `timeout: 90 * 1000`（含 Midscene 的项目）
- 保留 Playwright HTML reporter（video/trace）
- 追加 Midscene reporter：

```typescript
reporter: [
  ['list'],
  ['html', { open: 'never' }],
  ['@midscene/web/playwright-reporter', { type: 'merged' }],
],
```

- 浏览器：Chromium only（Midscene 部分能力依赖 CDP）

### 环境变量（运行前必检，缺失则停止询问用户）

| 变量 | 说明 |
|------|------|
| `MIDSCENE_MODEL_API_KEY` | 模型 API Key（勿写入仓库） |
| `MIDSCENE_MODEL_BASE_URL` | 兼容 OpenAI 的 endpoint，如 `.../v1` |
| `MIDSCENE_MODEL_NAME` | 模型名（须支持视觉/多模态；占位示例 `qwen3.7-plus`，不绑定唯一厂商） |
| `MIDSCENE_MODEL_FAMILY` | 坐标处理族（与所选模型匹配，占位示例 `qwen3`） |

可用 `.env` + `dotenv`，但 **禁止** 把 key 提交进 git。有 Midscene 步时 **必须** 生成可入库的 `.env.example`（init `--with-midscene` 或 01 写码时写入），并注明须视觉模型；用户 `cp .env.example .env` 后填写。

### gitignore

确保忽略：

```
midscene_run/
.env
```

**可入库**：`.env.example`（仅占位，无真实 key）

Cache（`midscene_run/cache/`）是否入库由用户决定；skill 默认不提交。

## Cache 与模型约束

- `cache: true` 可加速 **DOM 定位**（XPath）与部分 planning
- **不能走 XPath cache**（每次都会打模型）：Canvas、跨域 iframe、closed Shadow DOM、WebGL / 动态 SVG
- `aiQuery` / `aiAssert` / `aiBoolean` 等查询结果 **永不缓存**
- 测试执行依赖视觉模型；未配置 key → 阻塞，不进入 locator heal

## Heal 分流

| 失败类型 | 处理 |
|----------|------|
| Playwright 步（locator） | 沿用 playwright-cli attach + 修正 locator；不可见 overlay 根见 locator-strategy |
| Midscene 步（非验证码） | 只改自然语言 prompt，**不补 XPath** |
| 验证码读错 / 验证码类服务端错误 | 改 helper 内 prompt、normalize、清空输入、分层重试（算 Midscene 步） |
| 模型调用失败 / 未配置 key / 模型无视觉能力 | 阻塞报告用户，不走 2 轮 locator heal |

## 输出路径补充

| 产出 | 路径 |
|------|------|
| Midscene fixture | `tests/fixture.ts` |
| 验证码 helper（有图形验证码时） | `tests/helpers/captcha.ts` |
| 环境变量模板 | `.env.example` |
| Midscene 报告 | `midscene_run/report/` |
| Midscene cache | `midscene_run/cache/` |
