---
name: testflow
description: >-
  测试全生命周期调度：需求评审(prd-review) → 用例设计(spectest) → 三支线执行
  (ApiAutoTest2.0 接口 / browser-use-case-runner Web UI / miniprogram 微信小程序)
  → 统一报告汇总。
  Use when the user asks for 完整测试流程、从需求到报告、testflow、端到端测试工作流、
  小程序端到端测试, or wants to chain 需求评审/用例设计/用例执行/统一报告 in one run.
---
> 本文件中 <testflow-skill-dir></testflow> 指本 SKILL.md 所在技能目录（部署后为 C:\Users\admin\.claude\skills\testflow）。

# testflow：测试全生命周期调度

本技能是「地图 + 转换器 + 汇总器」，**不实现任何测试能力**。各阶段技能独立可用；
执行到某阶段时读取对应技能的 SKILL.md 并完整移交控制权，阶段结束后收回。

## 全景流程

阶段图与各阶段入口技能详见 [references/workflow-map.md](references/workflow-map.md)。

```
阶段1          阶段2            阶段3                阶段4        阶段5
需求评审   →   用例设计      →  执行（三支线）     →  统一报告  →  归档
prd-review     spectest 9步      3A 接口(可选)        汇总脚本     spectest-archive
                                 3B Web UI(默认)
                                 3C 小程序(可选)
```

**默认链路：1 → 2 → 3B → 4**。3A 需用户显式要求或有后端源码且用户确认才启动；
3C 需用户显式声明被测端含微信小程序（或需求/用例明确指向小程序端且经用户确认）。
阶段 0（api-doc-generator 预热）仅在「只有源码、没有需求文档」时使用。

## Task Progress

- [ ] Step 1: 定位状态目录（新建或恢复）
- [ ] Step 2: 阶段1 需求评审（prd-review）
- [ ] Step 3: 阶段2 用例设计（spectest new→analysis→plan(可选)→points→generate→review→fix）
- [ ] Step 4: 阶段3B UI 支线（转换 + browser-use-case-runner）
- [ ] Step 5:（可选）阶段3A 接口支线（ApiAutoTest2.0）
- [ ] Step 6:（可选）阶段3C 小程序支线（miniprogram 三件套）
- [ ] Step 7: 阶段4 统一报告（aggregate_reports.py）
- [ ] Step 8: 阶段5 归档（spectest-archive；可选 operation-manual）

## Step 1：定位状态目录

状态根 = **目标项目**的 `spectest/changes/<name>/`（复用 spectest 约定，不另起炉灶）。

- 用户给了变更名 → 检查 `spectest/changes/<name>/` 是否存在
- **已存在** → 按产物存在性判断进度，向用户复述「已完成阶段 X，可从 X+1 继续」：| 产物                                                  | 说明阶段           |
  | ----------------------------------------------------- | ------------------ |
  | `artifacts/*_testcases.xlsx`                        | 阶段 2 已完成      |
  | `artifacts/ui_cases.xlsx`                           | 阶段 3B 转换已完成 |
  | UI MD 报告（case-runner 产物）                        | 阶段 3B 已执行     |
  | `artifacts/api/ 下有说明文件（如 allure_path.txt）` | 阶段 3A 已执行     |
  | `artifacts/mp/ 下有说明文件（如 report_path.txt）`  | 阶段 3C 已执行     |
  | `artifacts/unified-report.md`                       | 阶段 4 已完成      |
- **不存在** → 走 Step 2 从头开始
- 每完成一个阶段，向用户复述（产物路径 + 统计 + 下一步选项），**用户确认后才推进**

## Step 2：阶段1 需求评审

1. 调用 **prd-review** 技能（读取其 SKILL.md 并移交控制权），输入需求文档
2. 产出 5 维评审报告（MD）
3. 暂存评审报告路径；在 Step 3 的 spectest-new 创建变更目录并生成 proposal.md 后，将报告路径补记入 proposal.md（作为输入附件）

## Step 3：阶段2 用例设计

调用 **spectest** 9 步（report/archive 两步由本流程的阶段 4/5 承接；plan 为可选步骤；每步都是独立技能，依次移交）：
`spectest-new` → `spectest-analysis` → `spectest-plan`（可选）→ `spectest-points` → `spectest-generate` → `spectest-review` → `spectest-fix`

**停靠策略**：`test-plan.md` 与 `design.md` 在本流程内为「不停等」产物——生成后直接继续下一步，供事后审阅与修改（单独运行 spectest 技能时才停靠确认）。

关键产物：`artifacts/<name>_testcases.xlsx`（25 列，Sheet「测试用例」）。

**分流判断**：25 列中「API URL」列非空的行是 API 用例（线索供 3A 参考）；
其余为 UI/功能用例 → 3B。

## Step 4：阶段3B UI 支线（默认）

1. **转换**（在 `spectest/changes/<name>/` 下执行）：

   ```bash
   python <testflow-skill-dir>/scripts/convert_25col_to_ui_xlsx.py \
     -i artifacts/<name>_testcases.xlsx \
     -o artifacts/ui_cases.xlsx
   ```

   检查自检输出（总行数/导出/跳过分类）。导出 0 行时停下询问用户。
2. 调用 **browser-use-case-runner** 技能执行 `artifacts/ui_cases.xlsx`（需向用户确认被测 URL 与会话策略）
3. 记录其 MD 报告与截图目录路径（供 Step 6 汇总）

## Step 5：（可选）阶段3A 接口支线

**启动条件**（二选一，且需用户确认）：用户显式要求接口自动化；目标项目有后端源码且用户同意。

依次调用：**api-doc-generator** → **api-scenario-generator** → **api-test-generator** → **api-test-runner**（各为独立技能，依次移交）。

- 产物按各套件自身约定落在目标项目 `docs/`；allure-results 路径记录到 `artifacts/api/` 下的说明文件（如 `allure_path.txt`），供 Step 7 读取
- **api-test-runner 只执行不修改**的原则不变

## Step 6：（可选）阶段3C 小程序支线

**启动条件**（需用户确认）：用户显式声明被测端含微信小程序；或需求/用例明确指向小程序端、Agent 提议并经用户同意。

技能为与本技能同级的 **miniprogram 三件套**（`miniprogram-script-author` / `miniprogram-run` / `miniprogram-shared`，部署后位于 `C:\Users\admin\.claude\skills\`；文档中的 `<skills-root>` 即该目录）。调用方式与 3A 相同：读取对应 SKILL.md 并移交控制权。

1. **一次性前置**（首次使用，在目标项目根执行）：

   - `bash <skills-root>/miniprogram-shared/scaffold.sh .`（生成 scripts/、miniprogram/tests/、suite.json 空壳与 `miniprogram.local.config`）
   - 编辑 `miniprogram.local.config`：`projectPath` + `cliPath`（或 `wsEndpoint`）。**Windows 注意**：cliPath 须为本机微信开发者工具安装路径（示例中的 macOS 路径不可用），且需在开发者工具中开启服务端口
   - 安装依赖：`npm install --save-dev jest miniprogram-automator xlsx`
   - 设置 `MP_ACCOUNT` / `MP_PASSWORD`（及可选 `MP_ID_CARD`）环境变量
2. **转换**（与 3B 同一转换器，仅换输出名）：

   ```bash
   python <testflow-skill-dir>/scripts/convert_25col_to_ui_xlsx.py \
     -i artifacts/<name>_testcases.xlsx \
     -o artifacts/mp_cases.xlsx
   ```

   runner 8 列与 miniprogram `parse-testcases.js` 表头兼容（用例编号→id、用例名称→title、前置条件→precondition、测试步骤→steps、测试数据→data、预期结果→expected），无需额外转换。
3. **生成脚本**：调用 **miniprogram-script-author**，输入 `artifacts/mp_cases.xlsx` —— 其先解析用例、经模拟器采 WXML inspect，再逐条生成 Jest describe 并维护 `miniprogram/suite.json`（用例 ID 沿用 25 列「测试项/测试点」，供 trace 对齐）
4. **执行**：调用 **miniprogram-run**，在小程序自动化仓库根执行 `run-with-reports.sh suite`（逐条按 suite 顺序；STOP_ON_FAIL / 续跑遵循其自身配置）
5. **记录**：当轮 Session 报告与台账路径写入 `artifacts/mp/report_path.txt`（仿 3A 的 `allure_path.txt` 约定），供 Step 7 读取

**边界**：script-author 不对正式用例下 PASS/FAIL 结论；3C 结果只认 miniprogram-run 的 Session 报告 / 台账。3B 与 3C 可并存——同一 25 列源头分别转换为 `ui_cases.xlsx` 与 `mp_cases.xlsx` 各自执行。

## Step 7：阶段4 统一报告

```bash
python <testflow-skill-dir>/scripts/aggregate_reports.py \
  --excel artifacts/<name>_testcases.xlsx \
  [--allure-dir <当轮 allure-results 路径>] \
  [--ui-report <case-runner MD 报告路径>] \
  [--mp-report <miniprogram 台账或 Session 报告路径>] \
  [--playwright-json <test-automation/web 的 playwright-results.json>] \
  --output artifacts/unified-report.md
```

五源缺哪个跳过哪个。注意：`--ui-report` / `--mp-report` 路径不存在时该节静默跳过（报告显示「UI 报告未生成」/「小程序报告未生成」），不报错——若用户预期有该支线报告，应先核对路径再汇总。`--mp-report` 接受台账（`miniprogram-executions.md`，自动取最后一个 Session 段，label 为用例 ID）或 Session 批量报告（`miniprogram-report-<sessionId>.md`，含 NOT_RUN）。`--playwright-json` 对接测试资产库 web 层的 JSON 结果（label 为 spec 标题，web-script-author 约定含 `[CASE:<用例编号>]` 前缀）。生成后向用户展示报告摘要（总览表 + 风险条目）。

## Step 8：阶段5 归档

- 调用 **spectest-archive** 归档变更
- 用户需要手册时，调用 **operation-manual**（可选）

## 硬性规则

- 不修改现有各技能的内部逻辑与产物格式
- 不做 testcases.json ↔ cases.json 互转（两链路独立，仅在报告汇合）
- 每阶段结束必须向用户复述并等确认，不自动串联
- UI 执行遇验证码/人工介入，遵循 browser-use-case-runner 自身的停等规则
- 3C 不修改 miniprogram 三件套内部逻辑与产物格式；结论只认 miniprogram-run 的 Session 报告 / 台账（script-author 产物属「待校验」）
- 3B 与 3C 互不转换：同一 25 列源头分别转换执行，仅在阶段 4 汇合

## 参考

- 面向使用者的完整说明（快速开始、各阶段用户视角、FAQ）：[references/user-guide.md](references/user-guide.md)
- 全景流程图与格式契约：[references/workflow-map.md](references/workflow-map.md)
