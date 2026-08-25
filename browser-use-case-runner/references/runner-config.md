# 运行配置说明

## 两类文件

| 文件 | 路径 | 作用 |
|------|------|------|
| **默认模板** | [.claude/skills/browser-use-case-runner/runner-config.json](../runner-config.json) | 提供 `videoRecording` 默认值（**默认 `enabled: false`，方式 1：关键截图留痕**）；传给 `generate_run_config.py --defaults`。**不**作为当轮执行的唯一配置。 |
| **当轮配置（真源）** | `reports/run-config-<UTC>.json` | 每次执行本 skill 时**必须**生成；含 `sessionStrategy`、`videoRecording.enabled`、用例来源、推断的 `inferredSuiteKind` 等；**整轮 browser-use 只读此文件**。 |

## `reports/run-config-*.json` 字段

| JSON 路径 | 类型 | 说明 |
|-----------|------|------|
| `schema` | string | 固定为 `browser-use-case-runner/run-config/1`（便于演进）。 |
| `generatedAtUtc` | string | 生成时间 UTC，与文件名时间戳一致。 |
| `casesJsonl` | string | 当轮用例 JSONL 路径。 |
| `casesSource` | string | 人类可读来源（如 `xlsx:test-data/用户登录-测试用例.xlsx`）。 |
| `caseCount` | number | 用例条数。 |
| `inferredSuiteKind` | string | `login` 或 `other`；由脚本根据文件名、`id`、`module`、步骤/前置等**启发式**推断。 |
| `sessionStrategy` | string | `fresh-per-case`：每条用例前 `close --all` 再起 `headed open`。`single-session`：首条 `open` 后会话内连续执行。 |
| `sessionStrategyRationale` | string | 简短说明为何给出该默认策略。 |
| `videoRecording.enabled` | boolean | **`false`（默认）**：不启桌面级外部录屏；留痕靠 `browser-use screenshot` 落盘 + 报告引用（方式 1）。**`true`**：用户**显式要**整屏/桌面外部录屏时，在 `headed open` 前走 ffmpeg（或 OBS/手动）流程；**非**浏览器视口原生录像。 |
| `videoRecording.outputDir` | string | 外部录屏开启时，建议 ffmpeg 等输出目录（相对仓库根）。 |
| `videoRecording.notes` | string | 可选说明（模板里已写清方式 1 与整屏备选的边界）。 |
| `userOverrides` | object | 可选；记录用户是否已确认录屏与会话策略（由 Agent 在询问后写回）。 |

## 推断规则（脚本 `generate_run_config.py`）

- **登录类**（`inferredSuiteKind: login`）→ 默认 `sessionStrategy: fresh-per-case`，若：来源路径含「登录」或 `login`；或**多数**用例满足：`id` 以 `TC-LOGIN` 开头 / 文案中含「登录」等。
- **其它**（`inferredSuiteKind: other`）→ 默认 `sessionStrategy: single-session`。
- Agent **必须**在跑浏览器前向用户确认：是否采用默认会话策略；**外部整屏录屏**仅在用户显式需要时再问（默认 `videoRecording.enabled` 为 `false`，方式 1 不要求问「要不要录屏」）。用户可覆盖并**写回**当轮 JSON。确认话术**保持简短**（缺 URL 则优先只问 URL + 会话策略半句）。

## 默认留痕：方式 1（`videoRecording.enabled === false`）

1. **不**启动 ffmpeg / 不要求用户手动开桌面录屏。
2. 执行过程中用 **`browser-use screenshot`** 在关键步骤后、以及每条 **PASS/FAIL/BLOCKED** 定稿前将视口（或 `--full`）保存到 `reports/screenshots/`，终端可打印 `SCREENSHOT=<路径>`；报告小节**必须**引用相关截图路径（验证码链路等规则见主 SKILL）。

## 仅当用户显式开启外部录屏（`videoRecording.enabled === true`）

1. 读取当轮 `reports/run-config-*.json`，确认 `videoRecording.enabled === true`。
2. 终端打印 `VIDEO_RECORDING=enabled`（**非** browser-use 内置录像；**整屏/桌面**采集，不是「只录浏览器视口」的 API）。
3. **若用户未声明只用 OBS/系统录屏**：Agent 可走 **ffmpeg 全自动**（与主 SKILL「外部录屏：ffmpeg（可选）」一致）：`ffmpeg -version` → 缺失则按 OS 安装 → 后台写入 `videoRecording.outputDir`，打印 `FFMPEG_OUTPUT=` → 再 `browser-use --headed open ...`。
4. **例外**：用户明确不要 ffmpeg、或安装/启录失败 → 请用户手动录屏并回复「已开始录屏」，或「跳过本次录屏」后再 `open`。
5. 报告头部记录**录像文件路径**（若有）。

## 文件缺失

若当轮 `reports/run-config-*.json` 不存在（未生成或未询问用户），**不得**开始执行用例；应先完成「导出 JSONL → 生成 run-config → 询问用户 → 写回配置」。
