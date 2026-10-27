import { test, expect } from '@playwright/test';

/**
 * 工具链自检（本地 data: 页面，不依赖网络与被测系统）。
 * 作用：验证 Playwright 安装/浏览器可启动——新环境跑通这一条即布线成功。
 */
test('工具链自检：浏览器可启动并渲染本地页面', async ({ page }) => {
  await page.goto(
    'data:text/html;charset=utf-8,<html><head><title>self-check</title></head><body><h1 id="hello">骨架 OK</h1></body></html>'
  );
  await expect(page).toHaveTitle('self-check');
  await expect(page.locator('#hello')).toHaveText('骨架 OK');
});
