# charter、草稿模板与 explore 产物

配合 `<skills-root>/SKILL.md`。细节以应用目录 `npx e2e guide explore` / `writing-tests` 为准。

`agent.act` / `agent.assert` 与 explore **charter 默认中文**；界面控件名用屏幕原文。工具/API 名（如 `type_secret`、`screenshot`）可保留英文术语。

## Charter 写法

一句、可执行：写清**区域**和**姿态**。不要写成测试步骤清单。

| 输入 | Charter 示例 |
|------|----------------|
| 需求：结账支持游客购买 | `以首次访问的游客身份探索结账流程，并报告异常` |
| 用例：会员升级 Pro | `以已登录会员身份探索计费页升级到 Pro 的主路径` |
| 只有 URL `/settings` | `从该 URL 进入设置页，走通主成功路径并报告异常` |

- 一条用例或一块需求 → 一条 charter；相关但可独立的区域拆开。
- 默认 `--max-steps 8`；范围很小可降到 4。
- 需要已登录会话时用 `--session <name>`（配置里需有对应 setup）。

### 图片验证码

- 不要为 explore 关掉真实防刷；用视觉读码。模型须支持图像（如 DeepSeek `deepseek-flash`），纯文本 chat 模型通常读不出。
- **两段 `agent.act`（强制）**：第一段只 `screenshot` + 填验证码/账号，禁止 `type_secret`、禁止提交；第二段才 `type_secret` 填密码并提交。过早 `type_secret` 会 `PIXEL_TAINTED`，刷新验证码也无法再读。
- explore：**先单独跑仅登录** charter（`--max-steps 4`），成功后再跑业务 charter；不要一条 goal 塞登录+建项目+需求+用例。
- 示例登录 charter：`仅在 /login：先 screenshot，若有验证码则读图填入验证码，用 credentials.admin 的用户名填账号，最后用 type_secret 填密码并提交，直到进入 /projects。不要逛其他路由。`

## 登录态复用（Web + 多条已登录业务路径）

同一账号下 ≥2 条业务主路径需要登录时：先 `test.setup` 保存 session，业务草稿与后续 explore 共用。

```ts
// tests/auth.setup.e2e.ts
// draft: from e2e explore — verify locators before relying on this file
import { test } from '@e2e-dev/web';
import { credentials, expect } from 'e2e';

test.setup('authenticate as admin', { sessions: ['admin'] }, async ({ app, screen, session, browser }) => {
  const admin = credentials.user('admin');
  await app.open('/login');
  await screen.getByLabel('账号').fill(admin.username);
  await screen.getByLabel('密码').fill(admin.password);
  await screen.getByRole('button', '登录').tap();
  await expect(browser).toHaveURL(/\/projects/);
  await session.save('admin');
});
```

```ts
// 业务草稿 — 禁止再写登录步骤
// draft: from e2e explore — verify locators before relying on this file
import { test } from '@e2e-dev/web';
import { expect, unique } from 'e2e';

test('新建项目并出现在列表', { session: 'admin' }, async ({ app, agent, screen }) => {
  const name = unique(`探索项目-${Date.now()}`);
  await app.open('/projects');
  await agent.act('打开新建项目，填写名称 {name}，然后提交', { params: { name } });
  await expect(screen.getByText(name.value, { exact: true })).toBeVisible();
});
```

## `E2E_HEADED`（`.env`）

与 `e2e-run` 相同：`E2E_HEADED=1`/`true`/`yes` 时 explore 加 `--headed`；`0`/`false`/未设则无头。e2e 本身不读该变量；由 skill 或应用 `scripts/e2e.mjs`（模板在 `e2e-init`）在调用时追加。

业务 explore（setup 已存在后；`--headed` 按 `E2E_HEADED`）：

```bash
npx e2e explore '在 /projects 探索新建项目流程；不要重新登录' --session admin --max-steps 8
```

- 不复用：只测登录；不同角色；仅 1 条已登录用例；Mobile 等无 `session` 的引擎。
- 密码：`fill(credentials.user(...).password)`，不要靠 `agent.act` 口头要密码。

## 草稿模板

用到 `browser` 时，`test` 从 `@e2e-dev/web` 引入。`expect` 和 `credentials` 从 `e2e` 引入。

```ts
// draft: from e2e explore — verify locators before relying on this file
import { test } from '@e2e-dev/web';
import { credentials, expect } from 'e2e';

test('会员升级到 Pro', async ({ app, agent, screen, browser }) => {
  const member = credentials.user('member');
  await app.open('/settings/billing');

  await screen.getByLabel('Email').fill(member.username);
  await screen.getByRole('button', 'Upgrade').tap();
  await expect(screen.getByRole('heading', 'Pro plan')).toBeVisible();

  await agent.act('选择 Pro 方案并确认升级');
  await expect(screen.getByRole('status')).toContainText('Pro');
  await expect(browser).toHaveURL('/settings/billing');
});
```

- 定位器优先：`getByRole`，其次 `getByLabel`，最后 `getByTestId`。
- 文案用屏幕上的原文。
- 一个 `agent.act` 只做一个可检查的结果；提示词默认中文。
- 会变的测试数据：`unique(\`前缀-${Date.now()}\`)` 放进 `agent.act` 的 `params`；断言用 **`.value`**（不要 `String(unique(...))`，也不要用裸前缀以免撞历史数据）。需要唯一匹配时加 `{ exact: true }`。

## `run.explore` 字段（写草稿时用）

`.e2e/report.json`（或 `--output` 目录下的 `report.json`）中：

| 字段 | 用途 |
|------|------|
| `goal` | 本次 charter |
| `summary` | 收尾评估，写进对用户的摘要 |
| `steps[]` | `title` / `instruction` / `status` → 草稿步骤线索 |
| `findings[]` | `kind`（issue/warning）、`severity`、`title`、`expected`、`actual`、`reproduction[]`、`path` |

- `reproduction` → 写成中文 `agent.act` 目标或 `screen.*` 动作。
- `expected` → `expect` / 中文 `agent.assert`。
- finding 是模型主张加证据，不是已验证复现；截图与 `actual` 对不上时，草稿里标待确认，不要当成已确认 bug。

证据目录示例：`.e2e/results/explore-<slug>-<id>/attempt-1/`（含 `finding-*.png`）。
