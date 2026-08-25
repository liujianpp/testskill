---
name: browser-use-case-runner
description: >-
  Executes web UI test cases from structured inputs (.xlsx tables, Markdown, or user-pasted
  bullets) using the browser-use CLI in headed mode, streams step-by-step progress to the terminal,
  and writes a Markdown report (PASS/FAIL/BLOCKED). Defaults to run cases sequentially in one
  session until blocked (FAIL/BLOCKED, CLI errors, captcha/human input, etc.); on PASS with no
  pending human step, continues to the next case. User may request per-case pause or continue-on-fail.
  When state cannot reveal captcha or pixel-only UI, uses browser-use screenshot plus a vision-capable
  Agent to read images, then manual fallback after pausing for the user.
  Each invocation generates reports/run-config-<UTC>.json from the case set (see
  scripts/generate_run_config.py), asks the user about session strategy and (only if they want it)
  optional full-screen external recording; default retention is key-frame screenshots (方式1), not ffmpeg.
  Login suites default fresh-per-case; others default single-session. Template defaults live in runner-config.json (--defaults). Use when the user wants
  用例执行、连续跑批直至遇阻、逐条停顿或失败也继续覆盖、人工介入、headed browser-use、当轮 run-config、
  可选整屏录屏开关、会话策略、验证码截图与视觉识别、执行日志与报告，或提供表格/MD/手动用例与 URL 联跑。
allowed-tools: Bash(browser-use:*), Bash(python3:*), Bash(brew:*), Bash(ffmpeg:*), Bash(apt:*), Bash(apt-get:*), Bash(dnf:*), Bash(winget:*), Bash(choco:*)
---

# 浏览器用例执行（表格 / Markdown / 手动）

在用户提供**被测 URL**与**用例来源**时，按本流程用 **有头** `browser-use` 按条顺序执行，**终端持续输出过程**，并将每条结果写入 **Markdown 报告**（跑批过程中可追加同一 `case-run-*.md` 或在末条后补汇总）。**是否「同一会话连续执行」** 以当轮 **`reports/run-config-*.json`** 中的 `sessionStrategy` 为准（`single-session` 时本条 **PASS** 且无未决人工/验证码则自动下一条；`fresh-per-case` 时每条前重启浏览器，见下文）；遇失败、阻塞、工具错误或需人工介入时停止，见「执行节奏」。

详细 CLI（`state` / `input` / `click` / `screenshot` 等）以 sibling skill [browser-use](../browser-use/SKILL.md) 为准；本 skill 还约定 **当轮 `reports/run-config-*.json`**（可选整屏外部录屏与会话策略）、skill 目录 **`runner-config.json` 仅作默认模板**（`--defaults`），以及**输入形态、执行顺序、日志、验证码/不可解析元素的视觉兜底与报告**。

`screenshot` 的路径参数、无路径时的 base64 行为、以及 `--full` 等选项，均以 [browser-use SKILL](../browser-use/SKILL.md) 为准；**不要假设**存在 `browser-use ocr` 等未文档化的子命令。

**默认留痕（方式 1）**：`videoRecording.enabled` 由模板与生成脚本默认为 **`false`**。不启 ffmpeg、不要求桌面整屏录屏；每条用例在**关键步骤后**及 **PASS/FAIL/BLOCKED** 定稿前，用 **`browser-use screenshot`** 将视口（或按需 `--full`）保存到 `reports/screenshots/`，终端可打印 `SCREENSHOT=<路径>`，**Markdown 报告须引用**这些路径（验证码等另有专用路径规则见下文）。仅当用户**显式要**整屏/桌面级外部录屏时，才将 `videoRecording.enabled` 置为 `true` 并走「外部录屏：ffmpeg（可选）」；该路径录的是**桌面采集**，不是 browser-use 自带的「只录浏览器视口」API。

## 用例来源（三选一或组合）

| 方式 | 说明 |
|------|------|
| **表格（.xlsx）** | 首行为表头；推荐列见 [xlsx-columns.md](references/xlsx-columns.md)。可用脚本导出为 JSONL。 |
| **Markdown** | `.md`，每个用例一个 `##` 小节；写法见 [markdown-cases.md](references/markdown-cases.md)。可用脚本导出为 JSONL。 |
| **手动输入** | 用户在对话中直接给出若干条用例字段（与 MD 子弹字段等价）。Agent 在内存中构成与 JSONL 相同的结构化列表后执行，无需文件。 |

执行前向用户确认：**URL**、**用例来源**；在完成「当轮运行配置」后，已（或同步）确认 **会话策略**。**外部整屏录屏**默认关闭（方式 1）；**仅当用户同轮明确要整屏/桌面录像** 时才问或写 `videoRecording.enabled: true`。**对话里向用户提问须极简**（两三行内）：缺什么问什么，默认策略可压成半句；勿复述 skill 全文。遇阻即停与 `sessionStrategy` 含义仅在用户问或首次跑批时再一句带过即可。可选覆盖（仅当用户显式声明时）：**逐条停顿**；**失败也继续**（`FAIL`/`BLOCKED` 仍如实写入报告后继续下一条；**CLI 硬错误**如会话崩溃仍须停止并提示 `browser-use close` 后重试）。

## 执行节奏与人工介入（默认）

**默认行为**

1. **连续执行（依赖 `sessionStrategy`）**：在 **`single-session`** 下，于**同一 browser-use 会话**中按 `id` 或文件顺序执行。每条仍输出终端阶段行，例如 `[id] START` → `STEP n: ...` → `STATE: 一句话摘要` → `[id] RESULT: PASS|FAIL|BLOCKED`；写完本条报告小节后，若结果为 **PASS** 且不存在未决人工输入、验证码等待等，**自动开始下一条**（无须每条 `close`/`open`）。在 **`fresh-per-case`** 下，「连续」仅表示顺序执行下一条，**每条开始前**仍须 `close --all` 与 `headed open`。若用户已声明 **逐条停顿**，则每条结束后停止并等待新指令，**不得**因「本条 PASS」而自动开下一条。
2. **遇阻即停**：**PASS 不属于遇阻**。执行过程中若出现以下任一情况，**立即停止**当前及后续自动化（**失败也继续**模式除外，见第 4 点），并汇报原因与建议下一步；默认遇阻后**不得**自动执行下一条；**不得**擅自多轮重试（除非本条开始前用户已声明允许「自动重试至多 N 次」）：
   - `browser-use` 命令失败、超时，或 `state` 中目标元素缺失；
   - 断言结论为 **FAIL** 或 **BLOCKED**；
   - 需要 **人工输入或人工确认**（验证码、短信码、扫码、U 盾、不确定的视觉识别结果、合规敏感操作等）。
3. **验证码 / 不可解析图形**：完成 **截图落盘** 并打印 `CAPTCHA_SCREENSHOT=...` 后，若计划使用视觉识别，识别出候选值须向用户 **简要说明置信度**；若识别失败、置信度低、或按策略一律走人工，则 **停止并明确请用户**在对话中回复验证码字符串（或「跳过本条」「刷新后再截」）。**收到用户回复前**不执行 `input` 验证码后的提交，除非用户已预先授权「我稍后自己会在浏览器里输好，你只负责点登录」等明确指令。
4. **可选覆盖模式**：
   - **逐条停顿**：用户显式要求时启用；每执行完一条（含 PASS）即停，等同旧版「每条后等待」。
   - **失败也继续**：用户显式要求时，出现 **FAIL** 或 **BLOCKED** 仍须照实写入报告，但可继续执行后续用例；遇 **CLI 硬错误**（会话崩溃等）仍须停止并提示 `browser-use close` 后重试。

## 推荐：先归一化为 JSONL（表格 / MD）

脚本与本 skill 同目录：`.claude/skills/browser-use-case-runner/scripts/test_cases_export.py`。在仓库**根目录**执行（便于 `test-data/...` 等相对路径）：

```bash
python3 .claude/skills/browser-use-case-runner/scripts/test_cases_export.py xlsx test-data/用户登录-测试用例.xlsx -o reports/cases.jsonl
python3 .claude/skills/browser-use-case-runner/scripts/test_cases_export.py md test-data/example-cases.md -o reports/cases.jsonl
```

无 `-o` 时打印到 stdout。字段键名：`id, name, module, priority, preconditions, steps, data, expected, source`（表格来源时 `source` 为 `xlsx`）。

手动用例：由 Agent 将用户粘贴内容整理为相同字段的对象列表（不必写文件）；若用例较多，可建议用户保存为 `.md` 再导出。手动用例若未落盘，可先写入临时 `reports/cases-manual-<UTC>.jsonl`（每行一个 JSON 对象，键同上）再调用生成脚本。

**生成当轮 `run-config`**（紧接导出之后，仓库根目录）：

```bash
python3 .claude/skills/browser-use-case-runner/scripts/generate_run_config.py \
  --jsonl reports/cases-<标签>.jsonl \
  --source "xlsx:<相对路径或来源描述>" \
  --defaults .claude/skills/browser-use-case-runner/runner-config.json
```

终端会打印生成的 **`reports/run-config-<UTC>.json`** 路径；字段说明见 [references/runner-config.md](references/runner-config.md)。

## 当轮运行配置（必做，先于 `doctor` / `open`）

1. **生成文件**：按上一节导出 JSONL 并执行 `generate_run_config.py`；不得跳过文件生成。
2. **默认推断（对用户可一句带过）**：如「非登录套件 → 默认单会话」；不必贴完整 `sessionStrategyRationale`。
3. **询问用户**（**短问短答**：一行列 `RUN_CONFIG=` 路径 + 默认 `sessionStrategy` 即可；默认 **`videoRecording.enabled=false`**（方式 1），**勿默认追问**整屏录屏；若用户同条消息已写明要整屏录屏或会话策略，直接写回 JSON，不问）：
   - 缺 **URL** 时：只问被测地址（或是否沿用上次环境），勿长段背景。
   - **整屏/桌面外部录屏** 仅用户显式要时：再问是/否 → `videoRecording.enabled` 与 `userOverrides.videoRecordingConfirmed`。
   - **会话策略** 是否改 → 否则保持 `sessionStrategy`，`userOverrides.sessionStrategyConfirmed`。
4. **写回 JSON 并打印**：终端输出 `RUN_CONFIG=<reports/run-config-*.json 路径>`。后续整轮**只读此文件**；**不要**再把 skill 目录 `runner-config.json` 当作当轮真源。

## 执行前检查

0. **读取当轮配置**：打开 `RUN_CONFIG` 指向的 `reports/run-config-*.json`（`Read` 或 `python3 -c`）。  
   - 若 **`videoRecording.enabled` 为 `false`（默认，方式 1）**：**不**启动 ffmpeg、不打印 `VIDEO_RECORDING=`；整轮以 **`browser-use screenshot`** 关键帧留痕（见「逐用例执行」与「截图与留痕」）。可打印 `RETENTION=screenshots` 便于日志检索。  
   - 若 **`videoRecording.enabled` 为 `true`**（用户显式要整屏/桌面外部录屏）：**在**首次 `browser-use --headed open` **之前**，打印 `VIDEO_RECORDING=enabled`（**非** browser-use 内置能力，参见 [browser-use SKILL](../browser-use/SKILL.md)）。在用户未同轮声明「只用 OBS/系统录屏、不要 ffmpeg」时，按下文「外部录屏：ffmpeg（可选）」由 Agent **检测 → 缺失则安装 → 后台启动录屏** 至 `videoRecording.outputDir`，打印 `FFMPEG_OUTPUT=<路径>`（若有 PID 可打 `FFMPEG_RECORDING_PID=`）；**无需**用户回复「已开始录屏」即可进入步骤 1 及后续 `headed open`。若用户声明不用 ffmpeg、或 ffmpeg 安装/启录均失败，再改为：请用户本机手动录屏并回复「已开始录屏」，或回复「跳过本次录屏」（报告中注明 `VIDEO_RECORDING=skipped_by_user`）。报告头记录最终采用的**录像文件路径**（若有）。  
   - 若 **`sessionStrategy === "fresh-per-case"`**：终端打印 `SESSION_STRATEGY=fresh-per-case`，每条用例见下文「每条用例前新会话」。  
   - 若为 **`single-session`**：终端打印 `SESSION_STRATEGY=single-session`；首条 `open` 后同会话连续执行直至遇阻或用户声明逐条停顿。  
1. `browser-use doctor`
2. 若会话异常：`browser-use close` 或 `browser-use close --all`（与当轮策略一致）。
3. 需要隔离并行会话时：`browser-use --session <name> ...`（见 browser-use 多会话说明）

## 外部录屏：ffmpeg（可选，仅整屏/桌面）

**本节仅在 `videoRecording.enabled === true` 时执行**（用户显式要整屏/桌面外部录屏）。默认 `false` 时跳过整节，留痕走方式 1（`screenshot`）。

当 `videoRecording.enabled` 为 `true` 且**未**被用户明确排除 ffmpeg 时，**由 Agent 全自动处理**（检测、安装、启录），用户不必手动开终端录屏；与 QuickTime、OBS 等为**备选**（用户声明只用后者时，不走本节的自动安装/启录）。

1. **角色**：ffmpeg 在用户本机以**独立后台进程**运行，**不是** `browser-use` 的子命令；与 `browser-use --headed open` 及后续 CLI **并行**。
2. **检测**：执行 `ffmpeg -version`（或 `which ffmpeg`）。成功则进入第 4 步启录；失败则进入第 3 步安装。
3. **安装（Agent 执行，无需用户手敲）**：按当前 OS 选一条执行；失败（无 brew、权限、网络等）则终端说明原因，并**降级**为手动录屏 + 等「已开始录屏」或「跳过本次录屏」。
   - **macOS**：`brew install ffmpeg`（需已装 [Homebrew](https://brew.sh/)；若无 brew，说明安装 Homebrew 或改用手动录屏）
   - **Windows**：`winget install ffmpeg` 或 `choco install ffmpeg`
   - **Linux**：如 `sudo apt-get install -y ffmpeg`（Debian/Ubuntu）或 `sudo dnf install -y ffmpeg`（Fedora/RHEL 系）；`sudo` 若需交互密码而不可得，则降级手动录屏
4. **启录（Agent 执行）**：`mkdir -p <videoRecording.outputDir>`（相对仓库根），输出文件如 `<outputDir>/run-<UTC>.mp4`。
   - **macOS**：先 `ffmpeg -f avfoundation -list_devices true -i ""` 解析输出，取**第一个屏幕类** video 设备索引（勿写死文档常量）；解析失败可尝试常见主屏 `1:none`。用 `nohup` 或等价方式后台运行，例如 `ffmpeg -y -f avfoundation -framerate 30 -i "<索引>:none" <输出路径>`（参数以本机 ffmpeg 支持为准）。
   - **Windows / Linux**：选用本机可用的屏幕采集设备（如 gdigrab、x11grab 等），同样后台写入上述路径；若本 skill 未列全，以 ffmpeg 官方文档为准，**失败则降级**手动录屏。
5. **成功后**：终端打印 `FFMPEG_OUTPUT=<绝对或仓库相对路径>`；可打印 `FFMPEG_RECORDING_STARTED=1`。然后**可直接**执行首次 `browser-use --headed open`，**无需**用户回复「已开始录屏」。
6. **收尾（建议）**：跑批正常结束或 Agent 停止自动化时，若仍知 ffmpeg 录屏 PID，可 `kill` 该进程以免空转；写入报告时带最终文件路径。
7. **边界**：用户**明确**「只用 OBS / 系统录屏、不要自动 ffmpeg」时，不执行安装与启录，仍用「已开始录屏 / 跳过」人工确认分支。

## 启动有头浏览器并打开 URL

整次跑批使用可见窗口（第一条打开命令必须带 headed）。**若 `videoRecording.enabled` 为 `true`**：在 ffmpeg 自动启录成功**后**（或手动录屏分支下用户确认「已开始录屏」/「跳过本次录屏」**后**）再执行首次 `open`。**若为 `false`（默认）**：无需等待任何外部录屏，可直接：

```bash
browser-use --headed open "<用户提供的 URL>"
```

后续同会话内 `state` / `input` / `click` 等**不再切换为无头**（与 browser-use 文档一致：由首次 `open` 的会话决定）。

### 每条用例前新会话（当轮 `run-config` 中 `sessionStrategy: fresh-per-case`）

适用于**登录类**用例集（脚本默认推断）或用户在当轮 `run-config` 中**显式选择**的 `fresh-per-case`。

1. **每条用例开始前**（含第一条）：`browser-use close --all`，再 `browser-use --headed open "<被测 URL>"`；然后对该条照常 `state` / `input` / `click` 等。  
2. **密码等受控输入**：清空优先 `browser-use input <索引> ""` 或聚焦后键盘全选删除；**避免**仅用 `eval` 改 DOM 导致与 React 状态不同步。  
3. **与 `single-session` 的差异**：此策略下「连续」仅指**按条顺序跑**，**不是**共用一个浏览器进程；`PASS` 后若未遇阻，下一条仍须先 `close --all` 再 `open`。`逐条停顿`、`失败也继续`、遇阻即停等规则不变。

## 逐用例执行（Agent 驱动）

自然语言「测试步骤」无法在无 LLM 情况下稳定映射为 CLI，**每条用例由 Agent 阅读理解后操作浏览器**。

对每条用例（按 `id` 或文件顺序）：

1. **终端日志**（stderr 亦可）：打印清晰阶段行，例如  
   `[id] START` → `STEP n: ...` → `STATE: 一句话摘要` → `[id] RESULT: PASS|FAIL|BLOCKED`
2. `browser-use state` 获取可点击索引；按「测试步骤」「测试数据」选择 `input` / `click` / `select` / `wait text` / `screenshot` 等。
3. **图形 / 验证码与不可解析元素（必走顺序）**  
   当 `state` **无法给出**验证码字符、Canvas 内文字、或关键信息仅在像素中（仅有 `[n]<img ...>` 等而无可读文本），或步骤要求「与图片一致」时：
   - **截图落盘（必做）**：`browser-use screenshot reports/screenshots/<用例id>-captcha.png`（或视口/全页，按 [browser-use](../browser-use/SKILL.md) 选择参数）。终端打印 `CAPTCHA_SCREENSHOT=<路径>`。报告中记录该路径。  
   - **视觉识别**：将上述截图交给**带视觉能力的执行 Agent**（例如当前对话中的多模态模型读取附件/路径）或团队已集成的 **browser-use Python 库中带 vision 的 Agent**（按官方文档调用）。要求输出**结构化**结果（如 4 位验证码），并校验与页面约束（如 `maxlength`、字符集）。**禁止**在 skill 中臆造独立 OCR CLI。  
   - **回填**：在用户同意使用识别结果或用户已提供字符串后，再执行 `browser-use input <验证码输入框索引> "<值>"`。若提交后仍报验证码错误，须先 **停止并告知用户**，是否由用户改码或授权再「刷新 → 截图 → 视觉」至多 N 次；**不得**在未获用户确认时自行循环多轮。  
   - **人工兜底**：识别失败、置信度不足、或结果不符合输入规则时：**立即停止**，在终端与报告中列出截图路径并请用户**回复验证码或下一步**；用户回复后再 `input` 与继续；该条可记 `BLOCKED` 直至用户确认完成。  
   - **可选进阶**：若需缩小识别区域，可先 `browser-use get bbox <索引>` 再用仓库外脚本裁切——非本 skill 必需步骤。
4. **断言**：对照「预期结果」与当前页面文案或 `state`；无法自动判定（如「与产品文案一致」）→ **BLOCKED**，写明原因。
5. **截图与留痕（方式 1 默认）**：
   - 每条用例除验证码链外：在**关键步骤后**（例如进入目标页、提交查询后）至少一次 **`browser-use screenshot`**；在写入 **`[id] RESULT: PASS|FAIL|BLOCKED`** 前再抓一张**结论态**视口图（FAIL/BLOCKED 已含于「结论态」；PASS 亦须有结论截图）。路径建议 `reports/screenshots/<用例id>-step<n>.png` 与 `reports/screenshots/<用例id>-result.png`（或与现有 captcha 命名并存）；终端可打印 `SCREENSHOT=<路径>`。
   - 走**上一条视觉链**时，`reports/screenshots/<用例id>-captcha.png`（或等价路径）**必须保存**并在报告中引用。  
   - 其他失败或 BLOCKED 时，仍可将整页截图保存为 `reports/screenshots/<id>.png` 便于复盘。

## 报告文件

- 默认：`reports/case-run-<ISO8601_UTC或本地时间>.md`；用户可指定路径。
- 每条用例一小节：**编号、名称、结果、依据、截图路径（含验证码截图路径，如有）**。
- 末尾 **汇总**：总数、PASS、FAIL、BLOCKED。

报告模板示例：

```markdown
# 浏览器用例执行报告

- 被测 URL: ...
- 用例来源: xlsx | md | manual
- run-config: `reports/run-config-....json`（`sessionStrategy`、`videoRecording.enabled`；**方式 1** 下列主要截图路径；若曾开整屏录屏则附录像路径）
- 开始 / 结束时间: ...

## TC-LOGIN-001 页面展示与标题

- **结果**: PASS
- **依据**: state 中出现标题「用户登录」与用户名输入框
```

## 限制

- 不同页面结构需重新对照 `state`；索引会变化，禁止硬编码旧索引跨页复用。
- **默认执行节奏**与「遇阻即停、需人工则停」冲突时，以用户当次对话中的**明确覆盖指令**为准（例如 **逐条停顿**、**失败也继续**、或声明只跑子集等）。
- 验证码 / 短信 / 扫码：采用 **截图 → 视觉 Agent → 人工** 三级；**不得**伪造通过或绕过生产环境风控；**测试环境**优先关闭/固定验证码以降低不确定性。
- 视觉识别可能误判；关键用例应在报告中保留截图路径供人工复核。
- **留痕与视频**：默认 **`videoRecording.enabled` 为 `false`（方式 1）**——不启整屏外部录屏，以 **`browser-use screenshot`** 关键帧 + 报告引用为主。仅当用户显式开启时，Agent 才按上文驱动 **ffmpeg** 等整屏采集（仍非 browser-use 内置）；能否成功取决于 OS、包管理器、权限与设备能力；**不得**声称存在未在 [browser-use](../browser-use/SKILL.md) 中列出的 `browser-use` 录像子命令。

## 冒烟示例（1 条用例）

1. 准备仅含一条用例的 MD 或 xlsx，或用户手动粘贴一条。
2. `browser-use --headed open <url>`
3. 执行该条并写报告一节，确认 headed 与报告路径符合预期。
4. 若文件**仅一条**则自然结束；若含多条且未声明 **逐条停顿**，**默认可连续执行**后续条；若只想验证单条节奏，可声明「只跑第一条」或启用 **逐条停顿**。
