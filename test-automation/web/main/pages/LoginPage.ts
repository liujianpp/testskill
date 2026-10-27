import { Page, Locator } from '@playwright/test';

/**
 * 登录页 Page Object —— 占位模板。
 *
 * 约定（对齐 miniprogram 三件套的规矩）：
 * 1. 禁止在未见过真实 DOM 前臆造 selector——由 web-script-author（P2-5）
 *    或人工在真实页面上采集后回填本文件。
 * 2. 每个页面一个 Page Object，放本目录；用例只调方法，不直接写定位器。
 * 3. 主干用例的账号一律走环境变量（WEB_USERNAME/WEB_PASSWORD），经 fixtures/auth.ts 注入。
 */
export class LoginPage {
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(private readonly page: Page) {
    // TODO(P2-5)：采集真实 selector 后替换下面三个占位定位器
    this.usernameInput = page.locator('[data-testid="username"]');
    this.passwordInput = page.locator('[data-testid="password"]');
    this.submitButton = page.locator('[data-testid="login-submit"]');
  }

  async goto(): Promise<void> {
    await this.page.goto('/login');
  }

  async login(username: string, password: string): Promise<void> {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
