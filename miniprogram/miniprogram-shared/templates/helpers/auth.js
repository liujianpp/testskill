/**
 * 登录与会话 helper（模板）。
 * 账号密码仅从环境变量读取，勿在模板中写死业务账号。
 *
 *   MP_ACCOUNT / MP_PASSWORD / MP_ID_CARD
 */
const PHONE = process.env.MP_ACCOUNT || '';
const PASSWORD = process.env.MP_PASSWORD || '';
/** 完整身份证号（测身份证登录时）；未设置则相关用例应自行跳过或失败提示 */
const ID_CARD = process.env.MP_ID_CARD || '';

function isTrace(x) {
  return !!(x && typeof x.step === 'function');
}

async function findByText(page, selector, text) {
  const els = await page.$$(selector);
  for (const el of els) {
    const t = await el.text();
    if (t && t.includes(text)) return el;
  }
  return null;
}

async function mockConfirmModal(miniProgram) {
  await miniProgram.mockWxMethod('showModal', function mockShowModal(options) {
    const res = { confirm: true, cancel: false };
    if (options && typeof options.success === 'function') options.success(res);
    if (options && typeof options.complete === 'function') options.complete(res);
    return res;
  });
}

async function isLoggedIn(miniProgram) {
  const token = await miniProgram.callWxMethod('getStorageSync', 'accessToken');
  return !!(token && String(token).trim());
}

async function loginWithAccount(miniProgram, account, password, { clearFirst = true } = {}) {
  if (!account || !password) {
    throw new Error('Missing account/password. Set MP_ACCOUNT and MP_PASSWORD (or pass explicitly).');
  }
  if (clearFirst) {
    await miniProgram.callWxMethod('clearStorageSync');
  }
  let page = await miniProgram.reLaunch('/pages/login/login');
  await page.waitFor(800);
  const inputs = await page.$$('.form-input');
  if (!inputs || inputs.length < 2) {
    throw new Error('login form inputs missing — adjust selectors for your mini program');
  }
  await inputs[0].input(account);
  await inputs[1].input(password);
  const btn = await page.$('.login-btn');
  if (!btn) throw new Error('login button .login-btn missing — adjust selectors');
  await btn.tap();
  await page.waitFor(2500);
  page = await miniProgram.currentPage();
  return page;
}

async function withOptionalTrace(trace, stepName, fn) {
  if (isTrace(trace)) {
    return trace.step(stepName, fn);
  }
  return fn();
}

async function forceLogin(miniProgram, account = PHONE, password = PASSWORD, trace) {
  if (isTrace(password)) {
    trace = password;
    password = PASSWORD;
  }
  return withOptionalTrace(trace, 'forceLogin', () =>
    loginWithAccount(miniProgram, account, password, { clearFirst: true })
  );
}

async function ensureLoggedIn(miniProgram, account = PHONE, password = PASSWORD, trace) {
  if (isTrace(account)) {
    trace = account;
    account = PHONE;
    password = PASSWORD;
  } else if (isTrace(password)) {
    trace = password;
    password = PASSWORD;
  }
  return withOptionalTrace(trace, 'ensureLoggedIn', async () => {
    if (await isLoggedIn(miniProgram)) {
      let page = await miniProgram.currentPage();
      const p = String((page && page.path) || '');
      if (p.includes('login') || !p.includes('pages/')) {
        page = await miniProgram.switchTab('/pages/home/home');
        await page.waitFor(800);
      }
      return page || (await miniProgram.currentPage());
    }
    return loginWithAccount(miniProgram, account, password, { clearFirst: false });
  });
}

async function loginWithPhone(miniProgram, trace) {
  return ensureLoggedIn(miniProgram, trace);
}

module.exports = {
  PHONE,
  PASSWORD,
  ID_CARD,
  findByText,
  mockConfirmModal,
  isLoggedIn,
  loginWithAccount,
  forceLogin,
  ensureLoggedIn,
  loginWithPhone,
};
