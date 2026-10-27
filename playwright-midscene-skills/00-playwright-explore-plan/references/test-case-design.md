# 测试用例设计规范

## 核心原则

| 原则 | 说明 |
|------|------|
| 原子性 | 1 个 `test()` = 1 个验证点，不将多个场景合并为一条用例 |
| 独立性 | 每条用例可单独运行，不依赖上一条用例的执行结果或顺序 |
| AAA 结构 | 用例内用 `test.step('准备'/'操作'/'验证')` 对应 Arrange / Act / Assert |
| 1:1 映射 | 用例矩阵中的每一行对应一个 `test()`，探索报告记录映射关系 |

## `test()` 与 `test.step()` 的职责

- **`test()`**：Playwright 统计的执行单位，HTML 报告中显示为独立用例
- **`test.step()`**：单条用例内的子步骤，仅用于报告分组，**不算独立用例**

反模式（禁止）：

```typescript
// 错误：多个验证点塞进一个 test()
test('搜索、重置与新增公寓', async ({ page }) => {
  await test.step('搜索', ...);
  await test.step('重置', ...);
  await test.step('新增', ...);
});
```

正确模式：

```typescript
test.describe('功能模块', () => {
  test.beforeEach(async ({ page }) => { /* 公共准备 */ });

  test('AL-001: 场景A', async () => { /* 仅验证场景A */ });
  test('AL-002: 场景B', async () => { /* 仅验证场景B */ });
});
```

## 用例拆解流程

```
理解输入 → 输出用例矩阵 → 界面探索 → 1:1 生成 test()
```

### Step 1：输出用例矩阵

探索前必须整理用例矩阵，每行包含：

| 字段 | 说明 |
|------|------|
| ID | 唯一编号，如 `AL-001` |
| 用例名称 | 简短描述验证点 |
| 前置条件 | 登录态、数据依赖 |
| 操作步骤 | 用户操作序列 |
| 预期结果 | 可断言的终态 |

多场景页面**默认拆为多条用例**，不合并。

### Step 3：代码生成结构

```typescript
test.describe('{模块名}', () => {
  test.use({ storageState: AUTH_STATE, baseURL: BASE_URL });

  let pageObject: SomePage;

  test.beforeEach(async ({ page }) => {
    pageObject = new SomePage(page);
    await pageObject.goto();
  });

  test('{ID}: {用例名称}', async () => {
    await test.step('准备', async () => { /* Arrange */ });
    await test.step('操作', async () => { /* Act */ });
    await test.step('验证', async () => { /* Assert */ });
  });
});
```

并非每条用例都需要三个 step——纯查询类用例可只有「验证」。

## 命名规范

- 格式：`{ID}: {动作} + {预期}`，如 `AL-002: 按名称搜索公寓`
- 使用中文或英文保持一致，与用例矩阵 ID 对应

## 数据隔离与自包含

- 新增/编辑/删除用例使用 `Date.now()` 或 UUID 生成唯一测试数据
- 删除用例必须操作本用例自建的数据，不删除共享数据
- **搜索用例**：优先「先创建目标数据再搜索」，不依赖外部种子数据
- **重置用例**：填入任意关键字即可，无需真实数据
- 禁止依赖分页敏感或可能被并行用例删改的共享数据（如 `E2E测试公寓`）

### AL-002 修正对比

```typescript
// 错误：依赖外部种子数据，分页或数据被删时失败
await apartmentPage.searchByName('E2E测试公寓');

// 正确：先创建唯一数据再搜索
const uniqueName = `PW搜索测试-${Date.now()}`;
await apartmentPage.createApartment({ name: uniqueName, ... });
await apartmentPage.searchByName(uniqueName);
```

## 登录态复用与验证码

位数、失败文案、成功 URL、刷新控件 **以 explore report 为准**。

- **测登录本身**：图形验证码用 Midscene `aiQuery` 读图 + Playwright fill（封装进 `tests/helpers/captcha.ts`）；登录 describe 不依赖已有 storageState（置空）
- **测其它模块**：`test.use({ storageState })`，路径来自报告；避免每条业务用例打模型
- **同时存在上述两类**：生成 `tests/auth.setup.ts` + config 中 `setup` project，业务 project `dependencies: ['setup']`，每次跑测刷新 auth，避免过期 token
- 禁止传统 OCR；禁止 `aiAct` 整段登录；分层重试见 midscene-hybrid

## 探索报告必填项

写入路径：`tests/reports/{case-name}-report.md`（与 `tests/explore/` 下 snapshot / 截图 / auth 分离）。

- 测试用例矩阵
- 用例 → 代码映射表（`AL-001` → `test('AL-001: ...')`）
- 每条用例的 locator 与断言点
- 有图形验证码时：图片定位、长度/字符集、刷新控件、失败文案、成功跳转（无则标未知）
- 有模态/弹窗时：dialog 可访问名、作用域 locator；testid 是否在不可见根上

## Playwright 配置要求

生成或更新 `playwright.config.ts` 时，`use` 中必须包含：

```typescript
headless: true,  // 默认无头运行（可省略，Playwright 默认为 true）
trace: 'on',     // 每条用例录制 trace，无头下照常生成
video: 'on',     // 每条用例录制视频，无头下照常生成
```

运行测试使用 `npx playwright test`（不加 `--headed`）。探索阶段使用 `playwright-cli open {url} --headed`（有头，便于观察页面与处理验证码）。

验证通过后执行 `npm run show-report`（后台运行），可查看视频与 Trace（逐步时间轴比视频更完整）。

## Page Object 提取时机

- 步骤 ≥ 5 或跨页面时提取到 `tests/pages/`
- 公共操作（`goto`、`create`、`delete`）封装为 Page 方法，避免在 spec 中重复
