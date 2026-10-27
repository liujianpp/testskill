---
name: e2e-run
description: >-
  在用户应用目录执行 tester-army/e2e 测试文件（含探索生成的草稿），跑完按
  e2e-report 写出 Markdown 与 HTML 报告并在对话中摘要失败原因；不修改测试脚本。
  在用户要跑 e2e、执行草稿、重跑失败用例时使用。修复交给 e2e-fix。
disable-model-invocation: true
---

# 执行 e2e 测试

在**用户的应用目录**里跑 `e2e run`。不在 skill 目录安装 `e2e`。

CLI 以应用内 `npx e2e guide running` 为准；不一致时以包为准。常用 flags 见 `<skills-root>/reference.md`。

本 skill **只执行、出报告、总结失败原因**；**不**改测试脚本或定位器。修复交给 **`e2e-fix`**。

## 先读一篇说明

- 跑法与产物：`npx e2e guide running`
- 需要理解失败码时：`npx e2e guide debugging`（只读，不据此改代码）

## 确认范围

1. 确认应用目录（含 `e2e.config.ts` 或 `e2e.config.mts`）。
2. 目标文件：用户点名的路径，或上一对话 `e2e-explore-draft` 刚写出的文件。
3. **默认只跑这些文件，不全量套件。** 用户明确要求全量时再跑配置里的全部测试。

没有可跑文件时：问清路径，不猜测全仓扫描。

## 执行

跑之前读应用目录 `.env` 的 **`E2E_HEADED`**（见 `<skills-root>/reference.md`）：

- `1` / `true` / `yes` → 命令加 `--headed`（已有该 flag 则不加）。
- `0` / `false` / 未设 → 无头（不加 `--headed`）。
- 用户本轮口头要求有头/无头时，以口头为准，可临时覆盖 `.env`。

```bash
npx e2e run tests/<file>.e2e.ts
# 有头时：
npx e2e run tests/<file>.e2e.ts --headed
```

项目若有 `npm run test:e2e`（`scripts/e2e.mjs`），它会按 `.env` 自动带 `--headed`；参数接在 `--` 后。pnpm / bun：`pnpm exec e2e run` / `bunx e2e run`（同样按上款决定是否加 `--headed`）。其他 flags 见 reference（如 `--no-cache`）。

## 跑后报告

执行结束后（无论通过或失败）：

1. 若项目有 `scripts/e2e.mjs` + `e2e-report.mjs`（`npm run test:e2e`），报告已自动写出；也可 `npm run report:e2e`。无脚本时再按 **`e2e-report`** skill 写出 **Markdown + HTML**：默认 `reports/e2e-report-<YYYY-MM-DD>.md` 与同名 `.html`。无 `report.json` 则说明本次未产出，不编造。
2. 在对话中摘要（字段指引见 `<skills-root>/reference.md`）：
   - 通过 / 失败 / 跳过数量
   - 每条失败：标题、错误码、一两句原因、trace 路径
3. **禁止**在本 skill 中修改 `tests/`、定位器或 setup；**禁止**为修失败而自动重跑改稿循环。

不把整份 AI trace / `report.json` 灌进对话；只摘失败步骤与断言摘要。

## 对用户交代

说明：跑了哪些文件、**优先给出 HTML 报告路径**（可浏览器打开）并附 MD 路径、通过/失败摘要。有失败时提示下一步用 **`e2e-fix`**（可带上报告路径或失败原因）；需要单独再导出报告时可用 `e2e-report`。
