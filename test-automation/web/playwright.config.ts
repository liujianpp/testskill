import { defineConfig } from '@playwright/test';

/**
 * 界面层配置：
 * - BASE_URL 未设置时仅本地自检用例可跑（真实环境用例自动 skip）
 * - 运行目录约定：main/ = 主干（CI 只跑这个），iterations/<版本>/ = 迭代新增
 * - 报告输出到仓库级 reports/web/（.gitignore 已排除，CI 以 artifact 归档）
 */
export default defineConfig({
  testDir: '.',
  testMatch: '**/*.spec.ts',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [
    ['list'],
    ['html', { outputDir: '../reports/web/playwright-report', open: 'never' }],
    ['json', { outputFile: '../reports/web/playwright-results.json' }],
  ],
  use: {
    baseURL: process.env.BASE_URL,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
    locale: 'zh-CN',
  },
  outputDir: 'test-results',
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
