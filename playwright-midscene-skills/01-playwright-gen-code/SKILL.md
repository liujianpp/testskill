---
name: 01-playwright-gen-code
description: >-
  根据 tests/reports 探索报告生成 Playwright（可混合 Midscene Instant Actions）测试代码。
  不探索、不跑测。已有 Playwright 时增量补充，不另起一套。Use when the user asks to
  generate spec from explore report, 根据计划生成代码, 写 playwright test,
  midscene fixture, or mentions 01-playwright-gen-code.
---

# 01 基于计划生成代码

`<skill-root>`：本目录（`01-playwright-gen-code/`）。

**只生成代码，不探索、不执行测试。** 结束后提示 `@02-playwright-run-report`。

## 触发条件

- 已有 explore report，要求生成 / 写出自动化代码
- 「根据计划生成代码」「写 spec」「生成 Playwright/Midscene 测试」

## 前置门禁

1. 存在 `tests/reports/{case-name}-report.md`
2. 报告含：**用例矩阵**、**用例 → 代码映射**、每步 **driver** 标注
3. 否则停止，提示先跑 `@00-playwright-explore-plan`

确认 `case-name` 与输出路径（默认见下方「输出路径」；已有 Playwright 时跟存量目录）。

## 工作流

```
- [ ] 读取 report.md
- [ ] 探测存量 Playwright（config / 依赖 / testDir / PO / fixture）
- [ ] 执行 design-checklist 自检
- [ ] 无 Playwright → init；已有 → 跳过全量 init，仅按需补 Midscene
- [ ] 增量生成 / 扩展 spec / PO / fixture（不覆盖无关存量）
- [ ] 列出实际写入路径，提示 @02-playwright-run-report
```

---

## 生成前自检

必须逐项通过 [references/design-checklist.md](references/design-checklist.md) 后再写码。

模板与规范：

- [references/test-template.ts](references/test-template.ts)
- [references/test-case-design.md](references/test-case-design.md)
- [references/locator-strategy.md](references/locator-strategy.md)
- [references/midscene-hybrid.md](references/midscene-hybrid.md)（有 midscene 步时）

写法风格：优先模仿仓库里已有 `*.spec.ts`；没有则用 [references/test-template.ts](references/test-template.ts) 与 [examples/case-chart-hybrid.md](examples/case-chart-hybrid.md)。

---

## 探测存量 Playwright

生成前**必须**探测。任一信号即判定「已有 Playwright」：

- 存在 `playwright.config.ts` / `.js` / `.mts` / `.mjs`
- `package.json` 依赖含 `@playwright/test`

已有时读取并沿用：

| 项 | 规则 |
|----|------|
| `testDir` | 读 config；未配则看现有 `*.spec.ts` 所在目录；再回退 `tests/` |
| Page Object 目录 | 已有 `pages/` / `page-objects/` / `pom/`（相对 testDir 或仓库常见位置）则用那个；否则 `{testDir}/pages/` |
| Midscene fixture | 已有则复用其导出的 `test`，**禁止**再写第二份 |
| `auth.setup.ts` / helpers | 已有则扩展；不另起平行文件 |
| 写法 | 优先对齐仓库现有 spec 风格 |

**硬约束（存量项目）**：

- **禁止**再跑会执行 `npm init playwright` 的全量 init（`init-playwright.sh` 在已有 config 时会跳过基础安装；skill 侧也不得主动全量 init）
- **禁止**整文件覆盖已有 PO / fixture / helper / 无关 spec
- **禁止**重写 `projects`、自定义 reporter 列表；只在缺失时追加 `video` / `trace` / `timeout` / `@midscene/web/playwright-reporter`
- 同 `case-name` 的 spec 已存在：在该文件内按矩阵 1:1 更新用例，不新建第二份
- 同页面已有 PO 类：补方法 / locator，不新建 `LoginPage2` 之类平行类
- 结束时列出**实际**写入路径，供 `@02-playwright-run-report` 使用

---

## 项目初始化

**无 Playwright**（无 config 且无 `@playwright/test`）时：

```bash
bash <skill-root>/scripts/init-playwright.sh
```

报告含 `driver: midscene`：

```bash
bash <skill-root>/scripts/init-playwright.sh --with-midscene
```

**已有 Playwright**：跳过全量 init；若需 Midscene 且未装，仅执行 `--with-midscene`（脚本会跳过基础安装，只补依赖 / 缺失的 fixture）。探测完成后在对话中简要列出沿用的 `testDir`、PO 目录、fixture 路径。

---

## 纯 Playwright vs 混合 Midscene

| 探索报告 | 行为 |
|----------|------|
| 全部 `driver: playwright` | `import { test, expect } from '@playwright/test'` |
| 存在任一步 `driver: midscene` | 安装 `@midscene/web`；使用存量或默认 `{testDir}/fixture.ts`；spec 从 fixture 导入 `test`；`expect` 仍来自 `@playwright/test` |

有 Midscene 步时：

1. `npm install -D @midscene/web`（或 init `--with-midscene`）
2. **已有** Midscene fixture → 复用；**无** → 按 midscene-hybrid 写入 `{testDir}/fixture.ts`（`PlaywrightAiFixture` + `cache: true`）
3. `playwright.config.ts`：**只补缺失项** — `timeout: 90_000`、HTML video/trace、`@midscene/web/playwright-reporter`；不重写已有 `projects` / reporter 整表
4. `.gitignore` 加入 `midscene_run/`、`.env`（已有则跳过）；生成/确保存在 `.env.example`
5. **检查** `MIDSCENE_MODEL_API_KEY` / `BASE_URL` / `NAME` / `FAMILY`；缺失则询问用户，**禁止**把 key 写入仓库
6. 仅 Instant Actions：`aiTap` / `aiInput` / `aiWaitFor` / `aiAssert` / `aiQuery`；**禁止** `aiAct` 整段；**禁止** YAML

混合示意：

```typescript
test('CH-001: 放大图表后可见明细', async ({ page, aiTap, aiAssert }) => {
  await test.step('操作', async () => {
    await page.getByRole('button', { name: '查询' }).click();
    await aiTap('图表右上角的放大按钮');
  });
  await test.step('验证', async () => {
    await aiAssert('图表已全屏且显示明细坐标轴');
  });
});
```

Page Object：稳定 locator → 存量 PO 目录（默认 `{testDir}/pages/`）；Midscene 调用留在 spec 的 `test.step`（或 PO 接收 `aiTap`）。

---

## 生成规范

- 矩阵 1:1 → 每个验证点一个 `test()`，禁止合并场景
- `test.describe` + `beforeEach`；AAA 用 `test.step('准备'/'操作'/'验证')`
- 优先采用 report 中 CLI 片段，再按定位优先级校验；1–4 不可用优先 Midscene
- 注释标注优先级或 `driver: midscene` + reason
- 敏感数据用 `process.env.*`（如 `LOGIN_USERNAME` / `LOGIN_PASSWORD`）
- **同时存在「测登录本身」与「业务用例用 storageState」**时：
  - 生成或扩展 `{testDir}/auth.setup.ts`（已有则扩展，不另起平行文件；用 captcha helper 登录后 `storageState` 写到报告中的 auth 路径）
  - `playwright.config.ts`：仅在缺失时补 `setup` project + 业务 project `dependencies: ['setup']` + `storageState`；**禁止**重写已有 `projects` 整表
  - 登录相关 describe：`storageState` 置空（`{ cookies: [], origins: [] }`），避免误用已登录态
- 图形验证码：逻辑进存量 helpers 目录下的 `captcha.ts`（默认 `{testDir}/helpers/captcha.ts`；已有则扩展）；矩阵登录类用例只调 helper（见 midscene-hybrid）；位数/文案以报告为准
- 模态/弹窗：可见性与交互用报告中的 dialog 可访问名作用域，勿对不可见 overlay 根做 `toBeVisible`（见 locator-strategy）
- **必须** `use.video: 'on'` + `use.trace: 'on'`（存量 config 缺失才追加）
- 数据依赖：写改删用 `Date.now()` 自建；搜索优先先创建再搜；禁止依赖易变种子数据
- 步骤 ≥ 5 或跨页 → Page Object（同页已有类则扩展）
- 复用已有 PO / fixture / helper；config **只补缺、不覆盖**

## 输出路径

默认（无存量 Playwright 或探测后回退）：

| 产出 | 默认路径 |
|------|----------|
| 测试文件 | `tests/{case-name}.spec.ts` |
| Page Object | `tests/pages/{PageName}.ts` |
| Midscene fixture（按需） | `tests/fixture.ts` |
| 验证码 helper（有图形验证码时） | `tests/helpers/captcha.ts` |
| 登录 setup（登录测 + 业务 storageState 时） | `tests/auth.setup.ts` |
| 环境变量模板（有 Midscene 时） | `.env.example` |
| 探索报告（只读） | `tests/reports/{case-name}-report.md` |

**已探测到存量 Playwright**：spec / PO / fixture / helper / setup 写入上表对应的**存量目录**（`testDir`、已有 `pages`/`page-objects`/`pom`、已有 fixture 路径），不要另起一套平行结构。探索报告路径仍为 `tests/reports/`（由 00 skill 约定；auth/snapshot 仍在 `tests/explore/`）。

---

## 结束

1. 列出**实际**生成 / 修改的文件路径（含存量路径）
2. 提示：**下一步请调用 `@02-playwright-run-report`**（不自动跑测；跑测时使用上述实际 spec 路径）
