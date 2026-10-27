---
name: e2e-report
description: >-
  根据 tester-army/e2e 最近一次运行产物（.e2e/report.json、trace、explore
  findings）生成 Markdown 与自包含 HTML 可视化测试报告。在用户要 e2e 报告、
  测试总结、导出结果时使用；也可由 e2e-run 跑完后自动执行写出步骤。
disable-model-invocation: true
---

# 生成 e2e 测试报告

在**用户的应用目录**读 e2e 运行产物，写出人可读 **Markdown + HTML** 报告。不在 skill 目录安装 `e2e`。

产物字段以应用内 `npx e2e guide running` / `explore` 为准。报告模板见 `<skills-root>/reference.md`。

**优先用命令自动生成**（不必每次调本 skill）：

```bash
npm run test:e2e          # 跑完后 scripts/e2e.mjs 自动调用 e2e-report.mjs
npm run report:e2e        # 仅根据已有 .e2e/report.json 写出 MD+HTML
```

产物默认：`reports/e2e-report-<日期>[.HHmm].md` / `.html`。`e2e-run` 对话收尾也可按本 skill 再导出或换路径；与脚本重复时可不覆盖已有文件（脚本会加时间后缀）。

## 输入

1. 确认应用目录与 output 根（默认 `.e2e`；配置或上次命令若指定了 `--output` 则用该目录）。
2. 主数据源：`<output>/report.json`。
3. 失败用例：对应 `<output>/results/.../trace.md`（只摘失败步骤与断言，不整文件灌进报告）。
4. 若存在 `run.explore`：把 findings 写入报告的探索小节。

没有 `report.json`：说明需先跑 `e2e-run` 或 `e2e explore`，不编造结果。

## 写出报告

1. 按 `<skills-root>/reference.md` 的 **Markdown 模板**与 **HTML 骨架**各填一份（同一 `report.json` 数据，不编造）。须含 **用例一览**（每条状态/文件/耗时）与 **用例详情**（每条步骤表），不能只有概览数字。
2. 默认路径（相对应用目录）：
   - `reports/e2e-report-<YYYY-MM-DD>.md`
   - `reports/e2e-report-<YYYY-MM-DD>.html`
3. 目录不存在就创建。不覆盖用户已有同名报告，除非用户明确要求覆盖；冲突时 MD/HTML **共用**同一时间后缀。
4. 用户指定路径时：
   - 仅 `.md` / 仅 `.html` → 只写该格式；
   - 无扩展名 → 写 `.md` + `.html` 一对。
5. HTML 须为**单文件**：CSS 写在 `<style>` 内，**禁止**外链 CDN（离线可打开）。截图/录像用相对路径（如 `../.e2e/results/...`），勿强制 base64。
6. 失败块「证据」：按 `report.json` attempt artifacts + 结果目录实际文件列出可点链接（`trace.md`、`video/*.webm`、失败截图、`screen-at-failure.txt`）；有 `.webm` 时再内嵌 `<video controls>`（见 `reference.md`）。**不要**做成 Playwright 式逐步 Trace Viewer。

## 对用户交代

优先给出 **HTML 路径**（可用浏览器打开，点证据链 / 播录像），并附带 Markdown 路径。用两三句话概括：通过/失败数、最严重失败或 explore issue。有失败时建议下一步用 **`e2e-fix`**；需重跑用 **`e2e-run`**。
