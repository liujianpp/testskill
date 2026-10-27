# 失败原因与改法速查

配合 `<skills-root>/SKILL.md`。细节以应用目录 `npx e2e guide debugging` / `writing-tests` 为准。

## 输入从哪读

| 来源 | 用途 |
|------|------|
| `reports/e2e-report-*.md` | 失败用例块：错误码、摘要、trace 路径 |
| `.e2e/report.json` | 机器可读结果列表 |
| `.e2e/results/<test>/trace.md` | 失败行、定位器、断言 observed |
| 用户口述 | 补全报告未写清的期望或环境差异 |

## 常见错误码 → 改法

| 错误码 / 现象 | 优先改法 |
|---------------|----------|
| `SECRET_UNAVAILABLE` / agent 要不到密码 | 用 `screen.getByLabel('密码').fill(credentials.user('…').password)` 再点登录；**不要**靠中文 `agent.act` 口头要求 `type_secret` 且未传入 Secret |
| 改写 `agent.act` 文案 | 提示词默认中文，控件名用屏幕原文；改完后下次 `e2e-run` 建议 `--no-cache` |
| `LOCATOR_AMBIGUOUS` / `getByText` 命中多条 | 名称用 `unique(\`前缀-${Date.now()}\`)`，断言 `name.value` + `{ exact: true }`；或收窄到行/卡片内定位 |
| `ASSERTION_FAILED` + toast（如「已创建」）已消失 | 断言稳定结果：列表中的标题、`toHaveURL`、heading；勿依赖短时 toast |
| `ASSERTION_FAILED` + `states: hidden` | 换可见节点；或等列表刷新后再断言；必要时 `exact` / role |
| `getByText("[object Object]")` | `unique()` 返回对象，断言用 **`.value`**，不要 `String(unique(…))` |
| `SESSION_UNAVAILABLE` / `SESSION_CONTRACT` | 检查 `test.setup(..., { sessions: ['name'] })` 与 `session.save('name')`；业务测用 `{ session: 'name' }` |
| `SESSION_EXPIRED` / `SESSION_INVALID` | 重跑含 setup 的套件；勿手改 `.e2e` 会话产物 |
| `MODEL_PROVIDER_FAILED` / Unauthenticated | 不改脚本；提示填 `.env` Key 或走 `e2e-init` |
| `CONFIG_LOAD_FAILED` / `INVALID_CONFIG` | 修 `e2e.config.ts` / 环境变量（属配置；用户确认后再动） |
| 回放与界面不一致 | 提示下次 `e2e-run` 使用 `--no-cache`；**不**手改 `.e2e/cache/` |

## 登录与 session

多条业务测共享账号时：登录放在 `tests/auth.setup.e2e.ts`，业务测 `{ session: 'admin' }` 且**不要**再写登录步骤。参见 `e2e-explore-draft` reference。

## 改完检查清单

- [ ] 密码只经 `credentials` / `.env`
- [ ] 可变数据经 `unique(\`…-${Date.now()}\`)` 且断言 `.value`
- [ ] 未编辑 `.e2e/cache/`
- [ ] 未在本 skill 内自动 `e2e run`（交给 `e2e-run`）
