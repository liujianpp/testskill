# 09 · 技能详解：testerarmy-e2e（探索式 E2E 五件套）

> **一句话**：封装开源 AI E2E 框架 [tester-army/e2e](https://github.com/tester-army/e2e)——你给需求或网址，**AI 自主探索**系统、自己写测试草稿、执行、修复、出报告。适合想体验「AI 自主探索式测试」的场景。

[← 返回总导读](README.md) | 套件自带文档：[testerarmy-e2e/使用说明.md](../../testerarmy-e2e/使用说明.md)

---

## 1. 五个技能与流水线

```
@e2e-init ──► @e2e-explore-draft ──► @e2e-run ──失败──► @e2e-fix ──► 回 @e2e-run 验证
                    （报告随时可 @e2e-report 或 npm run report:e2e）
```

| 技能 | 职责 | 不做 |
|------|------|------|
| `e2e-init` | 初始化脚手架：选引擎（Web/Mobile）+ 选模型厂商（6 家），写配置文件；然后**停手等你填 API Key** | 不跑探索/执行 |
| `e2e-explore-draft` | 需求/用例/URL → 一句一条 charter → AI 探索 → 落 `*.e2e.ts` 草稿 | 默认不执行 |
| `e2e-run` | 执行指定测试文件，出 MD+HTML 报告 + 摘要失败原因 | 不改脚本/定位器 |
| `e2e-fix` | 按失败报告/trace 修复脚本与定位器；同一失败点最多 **2 轮** | 默认不重跑、不改业务代码 |
| `e2e-report` | 从 `.e2e/report.json` 生成 MD + 单文件 HTML 报告（证据链+视频内嵌） | 不执行测试 |

> ⚠️ 五个技能都设了「禁止自动触发」，**必须显式调用**（如 `@e2e-init`）。所有操作发生在**你的应用目录**（不会在 skill 目录乱装东西）。

## 2. e2e-init（第一次用必跑）

- **必选两项**（选齐才动手）：
  - 引擎：`Web` / `Mobile`（Mobile 平台按系统自动定：Mac→iOS，否则→Android）
  - 厂商：`DeepSeek / OpenAI / Claude / 通义千问 / 智谱 GLM / 月之暗面 Kimi`
- **静默默认（不问）**：Web 的 `APP_URL` 默认 `http://localhost:3000`
- 写 `e2e.config.ts`、`.env`（逐键带注释）、npm scripts（`test:e2e` / `explore` / `report:e2e`）
- **API Key 由你本地填 `.env`**，禁止出现在对话/仓库
- 完成后明确停手（不会瞎跑探索）

## 3. e2e-explore-draft（AI 探索写草稿）

- **输入三分支**：有需求/用例 → 拆成一句一条的 charter；只有网址 → 主成功路径 charter；都没有 → 只问不动
- 探索命令：`npx e2e explore '<charter>' --max-steps 8 [--headed]`
- **登录态复用**：≥2 条业务主路径需登录 → 先落 `auth.setup.e2e.ts` 保存会话，业务 charter 复用且不再写登录步骤
- 草稿规矩：一条主路径一个 test；文件头标 `draft`；密码只走 credentials
- **遇付费/删除/真实订单等不可逆操作：停下问你，不继续**

## 4. e2e-run / e2e-fix / e2e-report

| 技能 | 要点 |
|------|------|
| `e2e-run` | 默认只跑你点名的文件（不全量）；跑完对话里只摘「通过/失败/跳过数 + 每条失败的一句话原因 + trace 路径」 |
| `e2e-fix` | 输入三选一：失败摘要 / 报告文件 / 你的描述；只改测试脚本、定位器、setup；**同一失败点 2 轮没进展就停** |
| `e2e-report` | 产物 `reports/e2e-report-<日期>.md` + `.html`；HTML 是**单文件**（离线可开），失败块带可点证据（trace/视频/截图） |

## 5. 环境变量速查（你应用目录的 .env）

| 变量 | 说明 |
|------|------|
| 厂商 API Key | 你本地填，禁入仓库 |
| `APP_URL` | Web 被测地址（默认 localhost:3000） |
| `E2E_BUNDLE_ID` | Mobile 应用包名 |
| `E2E_HEADED` | `1` 有头 / `0` 无头 |
| `E2E_VIDEO` / `E2E_TRACE` | 默认失败时保留 |
| `E2E_USER_<NAME>_PASSWORD` | 测试账号密码 |

## 6. 使用话术（完整流程 5 句话）

```text
1. 「初始化 e2e，引擎 Web，厂商 DeepSeek」           → @e2e-init（然后自己去 .env 填 Key）
2. 「按这份 PRD 探索并写草稿，地址 https://xxx」      → @e2e-explore-draft
3. 「跑 tests/order.e2e.ts」                          → @e2e-run
4. 失败 → 「按报告修复」                               → @e2e-fix → 再 @e2e-run 验证
5. 「导出报告」                                        → @e2e-report
```

## 7. 和其他技能的关系

- 独立小工具，不参与 testflow 主链；适合「AI 自主探索」尝鲜或补充性探索测试；
- 与 browser-use-case-runner 的区别：case-runner 按**你给的用例**逐条执行；e2e-explore-draft 让 AI **自己探索**系统写测试。

---

*本册基于 testerarmy-e2e 2026-10-29 现状整理。*
