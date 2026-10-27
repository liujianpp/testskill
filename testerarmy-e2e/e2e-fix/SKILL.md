---
name: e2e-fix
description: >-
  根据 e2e-run 的失败摘要、reports/e2e-report、.e2e/report.json+trace，或用户
  提供的失败原因，修复 tester-army/e2e 测试脚本与定位器（默认不自动重跑）。
  在用户要修 e2e 失败、改草稿定位器、或根据报告修脚本时使用。
disable-model-invocation: true
---

# 修复 e2e 测试脚本

在**用户的应用目录**里根据失败原因修改 e2e 测试 / setup / 定位器。不在 skill 目录安装 `e2e`。

调试与写法以应用内 `npx e2e guide debugging` / `writing-tests` 为准；不一致时以包为准。错误码速查见 `<skills-root>/reference.md`。

执行与出报告交给 **`e2e-run`**；本 skill **默认不**自动 `e2e run`。

## 先读一篇说明

动手前只读一篇：

- 理解失败：`npx e2e guide debugging`
- 改脚本 / 定位器 / session：`npx e2e guide writing-tests`

## 输入（有一即可）

1. 上一对话 **`e2e-run`** 的失败摘要，或刚写出的 `reports/e2e-report-*.md`
2. 应用目录 `.e2e/report.json` 与对应 `.e2e/results/.../trace.md`
3. 用户书面说明的失败原因（可含文件路径、错误码、期望行为）

都没有：只问失败原因或请先跑 **`e2e-run`**，**不**猜测着改代码。

## 修复范围

- **只改**测试脚本、定位器、`test.setup` / session 相关文件（如 `tests/*.e2e.ts`）。
- **不**编辑 `.e2e/cache/`；**不**把密码写进文件明文。
- **默认不**改产品业务代码；仅当用户明确要求且根因在应用时才动应用代码，否则只动 e2e 脚本。

## 流程

1. 归纳每条失败：文件、错误码、原因假设、拟改点（对照 `<skills-root>/reference.md` 速查）。
2. 修改脚本；若回放缓存可能过时，在交代中提示下次 `e2e-run` 加 `--no-cache`。
3. **不要**在本 skill 里自动跑 `e2e run`；改完提示用户用 **`e2e-run`** 验证。
4. 同一失败点（同一文件同一错误表现）用户连续要求再修时，最多改 **2** 轮仍无合理进展 → 停下，说明已试改法、trace 路径、建议人工看界面或补充原因。

不把整份 AI trace 读进上下文；需要时只看失败步骤与断言摘要。

## 对用户交代

说明：依据了哪些输入（报告路径 / 用户原因）、改了哪些文件、每条失败的改法要点。提示下一步用 **`e2e-run`** 验证；需要再出报告时由 run 自动写出或单独用 `e2e-report`。
