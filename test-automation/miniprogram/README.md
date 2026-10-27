# miniprogram：小程序自动化层（Jest）

本层**不复制脚本**，复用技能仓库 `E:\AI\skills\miniprogram\` 三件套的脚手架与执行链：

- 生成脚本：`miniprogram-script-author`（读 cases 用例 → 模拟器采 WXML inspect → 逐条生成 Jest describe）
- 执行回归：`miniprogram-run`（`run-with-reports.sh suite` 逐条 + 台账 + Session 报告）
- 共享约定：`miniprogram-shared`（conventions / selectors / 模板）

## 主干/迭代约定（与 api/web 对齐）

- 脚本落在小程序自动化仓库（按三件套自身约定），本目录维护**主干清单**：
  - `suite-main.json`：主干回归集（引用主干 spec 文件，CI/发版前跑）
  - `iterations/<版本号>/suite.json`：迭代清单（迭代期日常跑）
- 晋级规则同根 README：迭代上线 + 回归 2 轮全绿 → spec 移入主干目录并更新 `suite-main.json`
- 用例 ID 沿用 25 列「测试项/测试点」，与 cases/ 用例库对齐

## 状态

- [ ] 脚手架初始化（首次真实项目接入时，跑 `scaffold.sh` 后回填本目录）
