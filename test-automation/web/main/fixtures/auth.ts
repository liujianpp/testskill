import { test as base } from '@playwright/test';

/**
 * 登录夹具模板 —— 占位。
 *
 * 两种用法（真实 selector 就绪前均不可用，先保留结构）：
 * 1. storageState 方式（推荐，主干回归用）：单独跑一次登录 spec 生成
 *    .auth/state.json，playwright.config.ts 的 use.storageState 引用之，
 *    其余用例免登录复用会话。
 * 2. 每 spec 内 LoginPage.login() 方式：迭代期验证用。
 *
 * 账号只从环境变量读取（WEB_USERNAME / WEB_PASSWORD），禁止硬编码。
 */

type AuthFixtures = {
  authedPage: void; // TODO(P2-5)：实现 storageState 注入后改为 Page 型夹具
};

export const test = base.extend<AuthFixtures>({
  authedPage: async ({}, use) => {
    // TODO(P2-5)：登录并保存 storageState 后交给用例
    await use();
  },
});
