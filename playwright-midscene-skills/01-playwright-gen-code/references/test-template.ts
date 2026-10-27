import { test, expect } from '@playwright/test';
// 有 Midscene 步时改为：
// import { expect } from '@playwright/test';
// import { test } from './fixture';
// import { {PageName} } from './pages/{PageName}';

/**
 * 模板：describe + beforeEach + 多条独立 test()
 * 每个 test() 对应用例矩阵中的一行，用例内用 test.step 做 AAA。
 * 无存量 spec 时以本模板为准；混合 Midscene：examples/case-chart-hybrid.md、references/midscene-hybrid.md
 * 详见 references/test-case-design.md、references/design-checklist.md
 */

const AUTH_STATE = 'tests/explore/{case-name}-auth.json';

test.describe('{模块名}', () => {
  test.use({
    storageState: AUTH_STATE,
    baseURL: 'http://localhost:3000',
  });

  let pageObject: {PageName};

  test.beforeEach(async ({ page }) => {
    pageObject = new {PageName}(page);
    await pageObject.goto();
  });

  test('{ID-001}: {用例名称}', async ({ page }) => {
    await test.step('验证', async () => {
      await expect(page.getByTestId('main-table')).toBeVisible();
    });
  });

  test('{ID-002}: {用例名称}', async () => {
    const uniqueName = `PW搜索测试-${Date.now()}`;

    await test.step('准备', async () => {
      await pageObject.createItem({ name: uniqueName, ... });
    });

    await test.step('操作', async () => {
      await pageObject.searchByName(uniqueName);
    });

    await test.step('验证', async () => {
      await expect(pageObject.getRowByName(uniqueName).first()).toBeVisible();
    });
  });

  test('{ID-003}: {用例名称}', async () => {
    const uniqueName = `PW编辑测试-${Date.now()}`;

    await test.step('准备', async () => {
      await pageObject.createItem({ name: uniqueName, ... });
    });

    await test.step('操作', async () => {
      await pageObject.editItem(uniqueName, { field: '新值' });
    });

    await test.step('验证', async () => {
      await expect(pageObject.getRowByName(uniqueName)).toContainText('新值');
    });
  });
});

/**
 * 混合 Midscene 模板（探索报告存在 driver: midscene 时使用）
 * fixture 见 references/midscene-hybrid.md
 */
/*
import { expect } from '@playwright/test';
import { test } from './fixture';

test.describe('{模块名}-图表', () => {
  test('{CH-001}: 放大图表后可见明细', async ({ page, aiTap, aiAssert, aiWaitFor }) => {
    await test.step('操作', async () => {
      // Playwright：稳定 DOM
      await page.getByRole('button', { name: '查询' }).click();
      // Midscene：canvas / 动态 UI
      await aiTap('图表右上角的放大按钮');
      await aiWaitFor('图表已进入全屏', { timeoutMs: 5000 });
    });

    await test.step('验证', async () => {
      await aiAssert('图表已全屏且显示明细坐标轴');
    });
  });
});
*/

/**
 * Page Object 模板（步骤 ≥ 5 或跨页面时使用）
 * Midscene 调用不要写死在构造函数；可留在 spec 或由方法接收 aiTap 等
 */
/*
// tests/pages/{PageName}.ts
import { type Page, type Locator, expect } from '@playwright/test';

export class {PageName} {
  readonly page: Page;
  readonly table: Locator;

  constructor(page: Page) {
    this.page = page;
    this.table = page.getByTestId('main-table');
  }

  async goto() {
    await this.page.goto('/path');
    await expect(this.table).toBeVisible();
  }
}
*/
