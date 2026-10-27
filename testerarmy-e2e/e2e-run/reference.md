# 运行 flags、产物与失败摘要

配合 `<skills-root>/SKILL.md`。完整 CLI 以应用目录 `npx e2e guide running` 为准。

本 skill **不修改**测试文件；修复见 `e2e-fix`。

## `E2E_HEADED`（`.env`）

e2e runner **本身不读** headed 环境变量；由本 skill 或应用内 `scripts/e2e.mjs`（模板在 `e2e-init/scripts/e2e.mjs`）在调用时决定是否加 `--headed`。

| `.env` 值 | 行为 |
|-----------|------|
| `E2E_HEADED=1` / `true` / `yes` | 有头（加 `--headed`） |
| `E2E_HEADED=0` / `false` / 未设 | 无头 |

```
E2E_HEADED=1
```

用户本轮明确要求有头/无头时，以口头为准。

## `E2E_VIDEO` / `E2E_TRACE`（`.env`）

e2e **无**内置这两个环境变量；由应用 `e2e.config.ts` 读 `.env` 后写入官方 `video` / `trace`（合法值：`off` | `on` | `retain-on-failure` | `on-first-retry` | `on-all-retries`）。未设或非法值时 **默认均为 `retain-on-failure`**。

| `.env` | 含义 |
|--------|------|
| `E2E_VIDEO=retain-on-failure` | 失败/超时/flaky 保留录像（`attempt-*/video/video.webm`） |
| `E2E_TRACE=retain-on-failure` | 同上，保留 `results/<test>/trace.md` 逐步文字页 |
| `E2E_VIDEO=off` / `E2E_TRACE=off` | 关闭 |
| `E2E_VIDEO=on` / `E2E_TRACE=on` | 每次都保留 |

```
E2E_VIDEO=retain-on-failure
E2E_TRACE=retain-on-failure
```

**不是** Playwright Trace Viewer：`trace.md` 是逐步文字；画面靠 video。CLI `--video` / `--trace` 仍优先于 config。Agent 逐步细节另用 `--ai-trace`。

## 常用命令

```bash
npx e2e run tests/upgrade.e2e.ts
npx e2e run tests/upgrade.e2e.ts --headed
npm run test:e2e -- tests/upgrade.e2e.ts
npx e2e run tests/upgrade.e2e.ts --no-cache
npx e2e run --last-failed
npx e2e run tests/upgrade.e2e.ts --reporter list,markdown
```

| Flag | 用途 |
|------|------|
| `[files...]` | 只跑指定文件/目录/裸名 |
| `--headed` | 可见浏览器（引擎支持时）；也可由 `E2E_HEADED` 触发 |
| `--no-cache` | 关闭回放缓存 |
| `--last-failed` | 重跑上次未通过项 |
| `--reporter` | `list` / `json` / `junit` / `markdown` |
| `--output <dir>` | 结果目录，默认 `.e2e` |
| `--debug` | 阶段耗时与 agent 步骤表 |
| `--trace` / `--video` | 保留 trace 页或录像 |

## 产物位置

| 路径 | 内容 |
|------|------|
| `.e2e/report.json` | 机器可读整次运行记录 |
| `.e2e/results/<test>/trace.md` | 失败/调试用逐步文字 trace（非 Playwright Viewer） |
| `.e2e/results/<test>/attempt-*/video/` | 失败录像（`E2E_VIDEO` / `--video` 开启时） |
| `.e2e/cache/` | 回放缓存；**只读，不手动改** |
| `reports/e2e-report-<日期>.md` | 人读 Markdown（`npm run test:e2e` 自动 / `npm run report:e2e`） |
| `reports/e2e-report-<日期>.html` | 可视化 HTML（同上，浏览器打开） |

配置里的 `output` 会改报告与 results 根目录，不移动 `cache/`。

## 退出码（摘要）

| 码 | 含义（常见） |
|----|----------------|
| 0 | 所选测试通过 |
| 1 | 有失败断言或产品级失败 |
| 2 | 用法/配置/收集等运行前错误 |
| 3 | 环境不可用等 |

精确含义以当前包的 `running` guide 为准。

## 对话中的失败摘要（摘什么）

从终端输出 + `.e2e/report.json` + 失败项的 `trace.md` **摘录**，不要整文件粘贴：

| 项 | 来源 |
|----|------|
| 测试标题 / 文件 | 终端 Failed Tests 或 report results |
| 错误码 | 如 `ASSERTION_FAILED`、`SECRET_UNAVAILABLE`、`LOCATOR_AMBIGUOUS` |
| 一两句原因 | 终端箭头说明或 trace 首段失败文案 |
| trace 路径 | 终端 `trace .e2e/results/.../trace.md` |

有失败时在交代中提示用户用 **`e2e-fix`**，并给出报告路径。

## 边界

- **不**修改 `tests/`、setup、config（密钥补缺除外，那属于 `e2e-init`）。
- **不**为修失败而改脚本后重跑；验证修复由用户再调 `e2e-run`。
- 缺少账号/密钥且无法从环境读取 → 停下提示 `e2e-init` / 填 `.env`，不编造。
- 不可逆生产操作（真实下单、删库等）→ 停下确认。
