---
name: web-script-author
description: Web 界面脚本生成 - 读取 25 列测试用例，采集真实页面 selector，逐条生成 Playwright spec 并落位测试资产库（主干/迭代）。当用户要生成界面脚本、Playwright 用例、把用例转脚本、或执行 web-script-author 时使用。Use when the user asks for 界面自动化脚本、Playwright 脚本生成、用例转界面脚本, or wants to turn 25-col web cases into maintainable Playwright specs.
---

# web-script-author：界面脚本生成（25 列用例 → Playwright spec）

## 职责

读取 25 列标准用例中的 **UI/功能用例**（「API URL」列为空），在**真实被测页面**采集 selector 后，逐条生成 Playwright spec，落位到测试资产库（默认 `E:\AI\test-automation\web\`）。**只生成与维护脚本，不执行、不下结论**——执行交给 `npx playwright test` / CI，结论只认其运行结果。

对齐 [../miniprogram/miniprogram-script-author/SKILL.md](../miniprogram/miniprogram-script-author/SKILL.md) 的范式：无 selector 依据不写定位器；suite/manifest 可追溯；不越权执行。

## 前置输入

1. **用例来源**（三选一）：
   - 测试资产库合表：`test-automation/cases/main/web/<模块>.xlsx`（主干补充）
   - spectest 产物：`spectest/changes/<name>/artifacts/<name>_testcases.xlsx`（新迭代，先经 `scripts/promote_cases.py` 分拣）
   - 用户直接指定的 25 列 xlsx
2. **被测系统**：`BASE_URL`（web/.env 或环境变量）；未提供则询问
3. **落位**：新迭代须给版本号（`web/iterations/<版本号>/`）；主干修正直接改 `web/main/`

## 执行步骤

1. **确定仓库与落位目录**（按上规则；迭代 spec 扁平放 `web/iterations/<版本号>/`）。
2. **解析用例**：读取 xlsx「测试用例」Sheet，过滤出 UI 用例；逐条提取：用例编号（测试项/测试点）、用例标题、模块、前置条件、测试步骤、测试数据准备、预期结果、用例优先级。
3. **采集 selector（核心纪律）**：
   - 用 playwright（`npx playwright codegen <URL>`）或 chrome-devtools 打开真实页面采集；
   - **禁止臆造 selector**——每条用例涉及的输入/按钮/断言元素必须有真实 DOM 依据（role/text/test-id 优先，绝不由 AI 编造 data-testid 假定其存在）；
   - 采集结果先写入 `web/main/pages/<Page>.ts` Page Object（一页一对象；迭代可先写 `web/iterations/<版本号>/selectors-draft.md` 草稿，晋级前由人工确认并入 Page Object）；
   - 登录态一律经 `fixtures/auth.ts`（storageState 或 LoginPage.login），账号只读 `WEB_USERNAME` / `WEB_PASSWORD` 环境变量。
4. **逐条生成 spec**（模板：[templates/spec.template.ts](templates/spec.template.ts)）：
   - 一条用例一个 `test`，标题格式 `[CASE:<用例编号>] <用例标题>`（供结果追溯与汇总对齐）；
   - `describe` 按模块组织；步骤与预期对照用例的「测试步骤/预期结果」，不擅自增删断言语义；
   - 需要测试数据时从「测试数据准备」列取；禁止把账号密码写进 spec。
5. **维护清单**：更新 `web/suite.json`（用例编号 → spec 文件路径 → 所属（main/迭代版本）→ 优先级），幂等合并、不删他人条目。
6. **告知用户**：生成的 spec 路径清单、selector 采集依据页面、suite.json 变更；下一步建议 `npx playwright test <路径>` 本地验证（由用户或后续流程执行，本技能不执行）。

## 产物

- `web/iterations/<版本号>/<模块>_<名称>.spec.ts`（或主干 `web/main/tests/`）
- `web/main/pages/*.ts`（Page Object 增量）/ `web/iterations/<版本号>/selectors-draft.md`（草稿）
- `web/suite.json`（清单）

## 边界（硬规则）

- **不执行不下结论**：不跑 playwright test、不报 PASS/FAIL
- **不臆造 selector**：未经真实页面采集的定位器一律不得写入
- **不改用例**：spec 与用例语义不一致时，反馈用户改用例或说明偏差，不擅自"修"用例意图
- 覆盖率目标参考 spectest 契约（正向≥40%、负向≥30%、边界≥20%、安全≥10%）

## 下一步

- `npx playwright test`（在 test-automation/web 下）验证生成的脚本
- 迭代完成后：`scripts/promote_iteration.py --version <版本号> --confirm` 晋级主干
