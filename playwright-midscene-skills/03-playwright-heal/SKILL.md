---
name: 03-playwright-heal
description: >-
  修复 Playwright / Midscene 测试失败：locator 用 playwright-cli 调试，Midscene 只改
  自然语言 prompt。最多 2 轮。Use when tests fail, heal, 修复报错, locator broken,
  midscene prompt fail, or mentions 03-playwright-heal.
---

# 03 修复报错

`<skill-root>`：本目录（`03-playwright-heal/`）。

**只修复失败用例代码，最多 2 轮。** 修完后提示 `@02-playwright-run-report` 复跑（本 skill 不强制无限循环跑测）。

## 触发条件

- 测试失败、flaky、locator 失效、Midscene prompt 不准
- 用户在 02 询问后选择自动修复，或直接要求 heal

## 前置

1. 明确失败用例：`tests/{case-name}.spec.ts`、失败信息、可选报告 URL / `midscene_run/report/`
2. 建议对照 `tests/reports/{case-name}-report.md` 中该步的 `driver`（文案、dialog 名、验证码约定以报告为准）
3. 缺 `MIDSCENE_MODEL_*`、或模型无视觉能力导致的失败 → **阻塞**，请用户补 env，不走 locator heal

## 工作流

```
- [ ] 按 driver 分流
- [ ] 修复（最多 2 轮）
- [ ] 提示 @02-playwright-run-report 复跑
```

---

## 分流（强制）

| 失败类型 | 处理 |
|----------|------|
| Playwright 步（locator） | CLI attach + snapshot，修正 locator（见定位策略） |
| 元素 hidden / 点到不可见 overlay/modal 根 | Playwright：改为可见 `dialog`（或报告中的可见容器）+ 作用域内操作 |
| Midscene 步（非验证码） | **只改**自然语言 prompt，**不补 XPath**；可对照 Midscene 报告截图 |
| 验证码读错 / 验证码类服务端错误 | 改 helper（`tests/helpers/captcha.ts`）内 prompt、normalize、清空输入、分层重试；算 Midscene 步，计入 2 轮 |
| 模型无视觉 / 401 / 未配置 `MIDSCENE_MODEL_*` | 阻塞报告用户；不走 locator heal |

定位规则：[references/locator-strategy.md](references/locator-strategy.md)。  
Midscene 约束：[references/midscene-hybrid.md](references/midscene-hybrid.md)。

---

## Playwright 步 heal

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/{case-name}.spec.ts:<line> --debug=cli
playwright-cli attach tw-XXXX
playwright-cli snapshot
playwright-cli console
playwright-cli requests
# 按优先级修正 locator 后更新 .spec.ts / Page Object
```

定位优先级：testid → role+name → id → CSS →（尽量不用）XPath；动态 UI 应改为 Midscene Instant Actions 而非脆弱 XPath。  
不可见根节点：见 locator-strategy「可见容器 vs 不可见根节点」。

## Midscene 步 heal

1. 读失败断言 / Midscene 报告中的截图与 prompt
2. 收紧或改写 `aiTap` / `aiInput` / `aiAssert` / `aiWaitFor` / `aiQuery` 的自然语言（内容仍应对齐 explore report）
3. 验证码：优先改 helper，勿在每条用例内复制 prompt；分层重试上限见 midscene-hybrid
4. 禁止引入 YAML 或 `aiAct` 整段流程

---

## 轮次与结束

- 最多 **2** 轮修复尝试
- 每轮修完后可本地快速验证单条，但正式复跑与开报告交给 **`@02-playwright-run-report`**
- 2 轮后仍失败：输出失败摘要 + 报告链接，停止并说明需人工介入

## 结束语

提示：**请调用 `@02-playwright-run-report` 复跑并打开报告。**
