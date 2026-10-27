---
name: 00-playwright-explore-plan
description: >-
  探索 Web 界面并生成测试计划（用例矩阵 + explore report），不写 spec。
  稳定 locator 用 playwright-cli；动态 UI 标记 midscene driver。
  Use when the user asks to explore a page, write explore report, 探索计划,
  用例矩阵, 探索页面, or mentions 00-playwright-explore-plan.
---

# 00 探索 & 生成计划

`<skill-root>`：本目录（`00-playwright-explore-plan/`）。

**本 skill 只做探索与计划，禁止生成 `tests/*.spec.ts`。** 结束后提示 `@01-playwright-gen-code`。

## 触发条件

- 用户提供 URL 或用例文件，要求探索 / 出测试计划
- 用户说「探索页面」「探索计划」「写 explore report」「用例矩阵」

## 输入确认

上下文已有则跳过：

1. **目标**：URL 或用例文件路径
2. **测试场景**：如登录、下单、搜索
3. **登录态**：账号密码或已有 cookie
4. **case-name**：report 用 `tests/reports/{case-name}-report.md`；snapshot / 截图 / auth 用 `tests/explore/{case-name}-*`

## 工作流

```
- [ ] Step 1: 读取并理解 → 用例矩阵写入 report.md
- [ ] Step 2: playwright-cli 探索 → 补全 driver / locator / prompt
- [ ] 交接：报告完整 → 提示 @01-playwright-gen-code
```

混合判定：稳定 DOM → Playwright；canvas / 不稳定 DOM / Shadow-iframe / snapshot 失败 → `driver: midscene`。详见 [references/midscene-hybrid.md](references/midscene-hybrid.md)。探索阶段**不调用** Midscene Agent。

---

## 前置：playwright-cli

```bash
npx @playwright/cli --version
# 未安装：
npm install -D @playwright/cli@latest
npx playwright-cli install
```

**禁止**用 `cursor-ide-browser` 或 Playwright MCP 探索，只用 Shell 执行 `playwright-cli`。

**探索有头**：`playwright-cli open {url} --headed`（后续跑测由 02 skill 无头执行）。

---

## Step 1: 读取并理解

### URL 模式

提取 URL，按功能拆成多条用例矩阵（默认不合并）。

### 用例文件模式

不调用解析脚本、无固定 schema。

1. Read 读取文件（二进制见 [references/case-reading.md](references/case-reading.md)）
2. 输出用例矩阵（[references/test-case-design.md](references/test-case-design.md)）：ID、名称、起始 URL、前置、步骤、数据、预期
3. 不确定则询问，不猜测
4. 多场景默认拆多条
5. **门禁**：矩阵必须先写入 `tests/reports/{case-name}-report.md`，未写入不得进入 Step 2
6. 简要复述矩阵后再探索

---

## Step 2: 界面探索

### 模式 A：直接打开

```bash
playwright-cli open {url} --headed
playwright-cli snapshot --filename=tests/explore/{case-name}-snapshot.md
```

### 模式 B：seed attach（有登录/fixture 时优先）

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/seed.spec.ts --debug=cli
playwright-cli attach tw-XXXX
playwright-cli resume
playwright-cli snapshot --filename=tests/explore/{case-name}-snapshot.md
```

### 探索 Checklist

1. snapshot → `tests/explore/{case-name}-snapshot.md`
2. 逐步操作：`fill` / `click` / `select` / `check`；每步后重新 snapshot；收集 CLI 输出的 TS 片段
3. 关键步截图 → `tests/explore/{case-name}-step{N}.png`
4. 动态元素：`run-code` / `eval` 探测 iframe、shadow、canvas
5. **每步判定 driver**：`playwright` 或 `midscene`
6. 需登录态：`state-save tests/explore/{case-name}-auth.json`
7. `close`（模式 B 停掉 debug 进程）

### 定位优先级

| 优先级 | 策略 |
|--------|------|
| 1 | `data-testid` |
| 2 | role + 可访问名称 |
| 3 | `id` |
| 4 | CSS 类 + 标签 |
| 5 | XPath（尽量避免） |
| 降级 | Midscene Instant Actions（标记 driver，不写代码） |

```bash
playwright-cli eval "el => el.getAttribute('data-testid')" eN
playwright-cli generate-locator eN --raw
playwright-cli eval "() => !!document.querySelector('canvas')"
```

详见 [references/locator-strategy.md](references/locator-strategy.md)。

### 动态步判定（满足任一 → midscene）

- Canvas / WebGL，目标不在 a11y tree
- Closed Shadow / 跨域 iframe，snapshot 无内部节点
- 无可用 `eN`，或 locator 仅 hash class / 深层 XPath
- 无 testid、无语义 role、id 不稳定
- 图形验证码：字符在图片中，需 `aiQuery` 读图（输入框仍用 Playwright）

不切：表单/按钮/表格/链接且 testid 或 role+name 可用。

动态步：`screenshot` + `eval` → 报告写 `driver: midscene`、`reason`、`prompt` 草稿。

### 探索报告（交接契约）

写入 `tests/reports/{case-name}-report.md`，必须含：

- 用例矩阵 + 用例 → 代码映射表
- 步骤摘要
- 每步：`driver`、CLI 代码或 Midscene prompt、locator 层级 / 降级 reason
- 备选 locator、URL 变化、断言点
- 缺 testId 建议、与用例差异、阻塞说明
- auth 路径（若有）
- 若有 midscene 步：汇总「需 Midscene」清单
- **涉及图形验证码时**（无则标未知）：图片定位方式、字符长度/字符集、刷新控件、失败文案、成功跳转
- **涉及模态/弹窗时**：dialog 可访问名、建议作用域 locator；是否存在「testid 在不可见根上」现象

---

## 图形验证码（禁止传统 OCR）

- **探索**：可用视觉识别截图 → fill；失败后请用户手动登录 + `state-save`，并按上文字段写入报告。
- **spec（01 生成）**：**允许** Midscene `aiQuery` 读验证码图 + Playwright `fill` 输入框；逻辑进 `tests/helpers/captcha.ts`；登录按钮等稳定控件仍用 Playwright。
- **禁止**：Tesseract / 第三方 OCR 库；禁止用 `aiAct` 写整段登录。
- **分层**：测登录本身的用例自包含读码；其它业务模块可继续 `storageState`；同时存在两类时由 01 生成 `auth.setup` 刷新登录态。
- **分层重试**（文案/长度以报告为准）：读码格式不合格默认最多 3 次；提交后验证码类错误默认最多 5 次；仍失败则用例失败（CI 不等人手）。详见 midscene-hybrid。

## 阻塞处理

短信验证码、人工弹窗、缺账号、VPN、（仅记录）后续 Midscene 需模型配置 → 停止并报告原因 + 截图 + 建议下一步。

---

## playwright-cli 命令清单

| 命令 | 用途 |
|------|------|
| `open {url} --headed` | 有头打开 |
| `goto` / `snapshot` / `click` / `fill` / `select` / `press` | 导航与操作 |
| `screenshot --filename=...` | 截图 |
| `run-code` / `eval` / `generate-locator` | 探测与定位 |
| `state-save` / `state-load` | 登录态 |
| `attach` / `resume` / `close` | debug 会话 |

---

## 结束

1. 确认 `report.md` 完整（矩阵、映射、每步 driver）
2. 简要列出产出路径
3. 提示：**下一步请调用 `@01-playwright-gen-code`**（不自动串跑）

## 参考

- [references/case-reading.md](references/case-reading.md)
- [references/test-case-design.md](references/test-case-design.md)
- [references/locator-strategy.md](references/locator-strategy.md)
- [references/midscene-hybrid.md](references/midscene-hybrid.md)
- 示例：[examples/](examples/)
