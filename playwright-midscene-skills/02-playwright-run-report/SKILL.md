---
name: 02-playwright-run-report
description: >-
  无头执行 Playwright 测试，打开 HTML 报告并做合规校验（video/trace、通过数）。
  不含 heal；失败时提示调用 03-playwright-heal。Use when the user asks to run
  playwright tests, show-report, 打开测试报告, 执行用例, or mentions 02-playwright-run-report.
---

# 02 执行 & 产出报告

`<skill-root>`：本目录（`02-playwright-run-report/`）。

**只跑测与报告，不实现 heal。** 失败且用户同意修复时提示 `@03-playwright-heal`。

## 触发条件

- 跑 Playwright 测试、打开报告、`show-report`、执行已生成的 spec

## 前置

1. 存在待跑文件：`tests/{case-name}.spec.ts`（或用户指定路径）
2. 建议存在 `tests/reports/{case-name}-report.md`（用于核对矩阵通过数）
3. 若无 Playwright：`bash <skill-root>/scripts/init-playwright.sh`
4. 若 spec 使用 Midscene 且未装依赖：`bash <skill-root>/scripts/init-playwright.sh --with-midscene`（会生成 `.env.example`），并确认已 `cp .env.example .env` 且 `MIDSCENE_MODEL_*` 已填写（模型须支持视觉/多模态）

## 工作流

```
- [ ] 确认配置 video/trace
- [ ] npx playwright test（无头）
- [ ] 释放报告端口后 npm run show-report（后台）
- [ ] 合规校验 → 通过完成 / 失败询问是否 @03-playwright-heal
```

---

## 1. 运行测试

```bash
npx playwright test tests/{case-name}.spec.ts
```

默认无头。`playwright.config.ts` 中 `use.video` 与 `use.trace` 须为 `'on'`；缺失则先补再跑。

含 Midscene 的用例跑完后可告知：`midscene_run/report/`（最新 merged 若存在则给出路径）。

## 2. 打开报告（强制）

先释放 Playwright HTML 报告默认端口（9323），再启动，避免二次启动 EADDRINUSE：

```bash
(lsof -ti:9323 | xargs kill -9 2>/dev/null; true); npm run show-report
```

- Shell **后台**（`block_until_ms: 0`）
- 告知地址（默认 `http://localhost:9323`）
- 无 script 则补：`"show-report": "playwright show-report"`

## 3. 合规验证

- **矩阵通过数** = explore report 用例矩阵行数（只计矩阵对应的 `test()`；`setup` / 其它 project **单独说明**，禁止用含 setup 的总 `passed` 直接当矩阵行数）
- 每个矩阵用例有 video 与 trace；setup 有则一并说明
- 缺录制配置则回补 `playwright.config.ts` 并说明

## 4. 结果判定

**全部通过**：输出矩阵通过数（及 setup 若有）+ 报告已打开，提示完成（不询问修复）。有 Midscene 时附带 merged 报告路径。

**有问题**（任一）：

- failed / flaky
- 矩阵通过数 ≠ 矩阵行数
- 缺少 video / trace

在对话中直接询问（**不要**调用不存在的 `AskQuestion` 工具）：

> 测试报告已打开，发现 N 条失败 / 合规问题。是否需要自动修复？请回复是/否；若需要请调用 `@03-playwright-heal`。

- **是** → 提示用户调用 **`@03-playwright-heal`**（本 skill **不**执行 heal、不改 locator/prompt）
- **否** → 输出失败摘要（用例名、错误、报告链接），结束

---

## 参考

- 录制与运行相关自检：[references/design-checklist.md](references/design-checklist.md)（「运行与修复收尾」）
- Midscene 报告说明：[references/midscene-hybrid.md](references/midscene-hybrid.md)
