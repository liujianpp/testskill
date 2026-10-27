# 图表页混合 Playwright + Midscene

URL: http://localhost:3000/dashboard/chart
账号: admin / 123456（登录态通过 storageState 复用）

说明：查询等稳定控件用 Playwright；图表 canvas 内操作/断言用 Midscene Instant Actions。

## 测试用例矩阵

| ID | 用例名称 | 前置条件 | 操作 | 预期结果 |
|----|---------|---------|------|---------|
| CH-001 | 查询后图表可见 | 已登录 | 打开图表页并点查询 | 图表区域可见 |
| CH-002 | 放大图表后可见明细 | 已登录 | 查询后点击图表放大 | 全屏且显示明细坐标轴 |
| CH-003 | 图例筛选后序列变化 | 已登录 | 点击图例隐藏某一序列 | 该序列从图表消失 |

## 探索步骤 driver 示例

| 步骤 | driver | 说明 |
|------|--------|------|
| 打开页面 / 点「查询」 | playwright | `getByRole('button', { name: '查询' })` |
| 点击图表放大 | midscene | canvas，a11y 无目标；prompt: `图表右上角的放大按钮` |
| 断言全屏明细 | midscene | `aiAssert('图表已全屏且显示明细坐标轴')` |
| 点击图例项 | midscene | canvas 图例；prompt: `图例中的「销售额」项` |

## 生成结构

```
tests/fixture.ts          # PlaywrightAiFixture
test.describe('图表页')
  test('CH-001: ...')     // 多为 Playwright
  test('CH-002: ...')     // page.click 查询 + aiTap 放大 + aiAssert
  test('CH-003: ...')     // aiTap 图例 + aiAssert
```

## 用例 → 代码映射

| 用例 ID | 生成代码 |
|---------|---------|
| CH-001 | `test('CH-001: 查询后图表可见')` |
| CH-002 | `test('CH-002: 放大图表后可见明细')` |
| CH-003 | `test('CH-003: 图例筛选后序列变化')` |

## 混合代码示意

```typescript
import { expect } from '@playwright/test';
import { test } from './fixture';

test.describe('图表页', () => {
  test.use({
    storageState: 'tests/explore/chart-hybrid-auth.json',
    baseURL: 'http://localhost:3000',
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/chart');
  });

  test('CH-001: 查询后图表可见', async ({ page, aiAssert }) => {
    await test.step('操作', async () => {
      await page.getByRole('button', { name: '查询' }).click();
    });
    await test.step('验证', async () => {
      await aiAssert('页面中央显示图表');
    });
  });

  test('CH-002: 放大图表后可见明细', async ({ page, aiTap, aiWaitFor, aiAssert }) => {
    await test.step('操作', async () => {
      await page.getByRole('button', { name: '查询' }).click();
      await aiTap('图表右上角的放大按钮');
      await aiWaitFor('图表已进入全屏', { timeoutMs: 5000 });
    });
    await test.step('验证', async () => {
      await aiAssert('图表已全屏且显示明细坐标轴');
    });
  });

  test('CH-003: 图例筛选后序列变化', async ({ page, aiTap, aiAssert }) => {
    await test.step('操作', async () => {
      await page.getByRole('button', { name: '查询' }).click();
      await aiTap('图例中的「销售额」项');
    });
    await test.step('验证', async () => {
      await aiAssert('图表中销售额序列已隐藏');
    });
  });
});
```

## 前置依赖

- `@midscene/web` + `tests/fixture.ts`
- 环境变量：`MIDSCENE_MODEL_API_KEY` / `BASE_URL` / `NAME` / `FAMILY`
- 详见 [../references/midscene-hybrid.md](../references/midscene-hybrid.md)
