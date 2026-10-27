import { test, expect } from '@playwright/test';

/**
 * 真实环境冒烟模板（主干）。
 * BASE_URL 未设置时整文件跳过——见 web/.env.example。
 */
test.skip(!process.env.BASE_URL, '未设置 BASE_URL（见 web/.env.example），跳过真实环境冒烟');

test('被测系统冒烟：首页可达且已渲染', async ({ page }) => {
  await page.goto('/');
  // 标题非空：能进入且完成基本渲染
  await expect(page).toHaveTitle(/.+/);
});
