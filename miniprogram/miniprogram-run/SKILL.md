---
name: miniprogram-run
description: >-
  Executes existing Jest mini program UI test specs (single or suite) via
  miniprogram-automator against WeChat DevTools simulator. Writes execution
  ledger and artifacts. Use when running mini program automation scripts,
  suite regression, or validating generated specs. Does not author test scripts.
disable-model-invocation: true
---

# 小程序执行（miniprogram-run）

详见 [conventions.md](../miniprogram-shared/conventions.md)、[selectors.md](../miniprogram-shared/selectors.md)。

**职责**：执行 Jest spec、写入 `reports/miniprogram-executions.md`、`reports/artifacts/`，以及 Session 批量报告 `reports/miniprogram-report-<sessionId>.md/.html`（由 `run-with-reports.sh` 生成）。编写 spec 请 `@miniprogram-script-author`。

---

## 用户配置

编辑 **[`miniprogram-run.config`](miniprogram-run.config)**（与本 Skill 同目录）：

```bash
RECORD_TRACE=true         # 伪 Trace：步骤 meta/wxml/截图 → artifacts/.../trace/
RECORD_SCREENSHOT=false   # 收尾整页截图（可选；走 miniProgram.screenshot）
OPEN_HTML=true            # 执行结束后自动打开 batch HTML 报告
STOP_ON_FAIL=false        # false=失败后继续（同一 Session）；true=遇失败即停
JEST_REPORTER=default
```

截图须用 `miniProgram.screenshot({ path })`（Page 无此 API；仅模拟器）。Trace 步骤图与 `RECORD_SCREENSHOT` 均经 `helpers/screenshot.js`。

**Trace 不截图的步骤**：`ensureLoggedIn` / `forceLogin` / `login*`，或页面 path 含 `login`（仍写 meta/wxml）。

执行前须：

1. 用户仓库已脚手架（`bash <skills-root>/miniprogram-shared/scaffold.sh .`）
2. 配置 `miniprogram.local.config`（`projectPath`、`cliPath` 或 `wsEndpoint`）
3. 可选：编辑 **[`miniprogram-run.config`](miniprogram-run.config)**

---

## 执行偏好

在 **小程序自动化项目仓库根**（含 `miniprogram/suite.json`）执行：

```bash
<skills-root>/miniprogram-run/run-with-reports.sh <子命令> [参数]
```

| 子命令 | 用途 |
|--------|------|
| `single <spec.js>` | 跑该文件全部 describe（模块级调试）+ 独立 artifact + 台账 |
| `suite` | 读 `miniprogram/suite.json`，**逐条**按 `cases[].id` 用 `--testNamePattern` 跑对应 describe；默认失败后继续（`STOP_ON_FAIL=false`），同一 Session |
| `suite-json` | 与 `suite` 相同 |

可选：

- `--file <path>` 覆盖 suite 路径
- `--from <TC-ID\|spec.js>` 从该条起执行，不重跑前序（续跑；优先匹配 `cases[].id`）

**已移除**：一次 Jest 跑整个目录；**禁止**用文件夹遍历顺序代替 suite。

**一模块一文件**：suite 中同模块多条共用 `tests/<模块>/<模块>.spec.js`，靠 `id` + `--testNamePattern` 只跑该 TC 的 `describe`；`CASE_KEY` 用 `cases[].id`。单条调试用 `suite --from TC-xxx`（或临时 `STOP_ON_FAIL`）；模块级调试用 `single` 跑整文件。

### 示例

```bash
<skills-root>/miniprogram-run/run-with-reports.sh suite
<skills-root>/miniprogram-run/run-with-reports.sh suite --from TC-MP-003
<skills-root>/miniprogram-run/run-with-reports.sh single miniprogram/tests/auth/auth.spec.js
```

---

## 台账与产物

- **single** / **suite 每条**：`artifacts/<session>/<caseKey>/jest-results.json`、`console.log`（可选 `screenshot.png`、`trace/`）
- **批量 md**：`reports/miniprogram-report-<sessionId>.md`
- **批量 html**：`reports/miniprogram-report-<sessionId>.html`（含 Trace viewer 链接；**默认** `OPEN_HTML=true` 时执行结束后自动用系统浏览器打开）
- **伪 Trace**：`artifacts/<session>/<caseKey>/trace/viewer.html`（非 Playwright video/trace.zip）

---

## 失败探索与重试

- **suite / single**：读 `artifacts/<session>/<caseKey>/console.log`、`jest-results.json`、`trace/viewer.html`
- 至多再重试 2 次（修订 spec 须 `@miniprogram-script-author`）
- **全量**：`suite`（一次调用 = 一个 Session；失败标 FAIL 后默认继续）
- **遇失败即停**：`STOP_ON_FAIL=true`，后续为 **NOT_RUN**；可用 `suite --from` 续跑
- **续跑**：`suite --from TC-xxx`（会新开 Session；一般仅在 STOP_ON_FAIL 或中断后使用）
- **单条 / 模块调试**：`suite --from TC-xxx`；或 `single <模块.spec.js>`（整模块）

默认 `STOP_ON_FAIL=false`：某条 FAIL 后仍跑完 suite，全部结果写入同一 Session 报告。

---

## 回复格式（执行任务）

1. 命令、SessionId、config 摘要。
2. suite：各 TC 状态 + 各 `artifacts/<session>/<caseKey>/` 路径；single：artifact 路径。
3. 失败摘录与是否建议 `@miniprogram-script-author`；优先给 Trace viewer 路径。
4. `reports/miniprogram-report-<sessionId>.md` / `.html`（suite / single 均会生成；脚本已尝试自动打开 HTML，Agent 无需再手动打开）。

---

## 边界

- 无日志依据不得宣称 PASS。
- 不得臆造 FAIL 为 PASS。
- 不从零写用例 spec。
- automator **不提供** Playwright 级 video / trace.zip；伪 Trace 为步骤证据链。
- 截图禁止调用 `page.screenshot`；必须用 `miniProgram.screenshot`。
- Trace 对 `ensureLoggedIn` / `forceLogin` / 登录页步骤跳过 png。
