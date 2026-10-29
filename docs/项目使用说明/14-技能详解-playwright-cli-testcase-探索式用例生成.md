# 14 · 技能详解：playwright-cli-testcase（探索式 Web 用例生成）

> **一句话**：给一个网址（需求文档可选），AI 用 playwright-cli **真实打开网站逛一圈**，先给你一份测试点计划、**你确认后**再展开成完整用例，导出 10 列 Excel（或 XMind）。**不生成自动化脚本**。

[← 返回总导读](README.md) | 套件自带文档：[playwright-cli-testcase1.0.1/使用说明.md](../../playwright-cli-testcase1.0.1/使用说明.md)

---

## 1. 什么时候用它（与 spectest 的区别）

| 对比项 | spectest（03 册） | playwright-cli-testcase（本册） |
|--------|-------------------|--------------------------------|
| 出发点 | **需求文档** | **真实界面**（需求文档可选） |
| 产出格式 | 25 列 Excel（全工作区通用） | 10 列 Excel / XMind |
| 适合 | 有正式 PRD、要走全流程 | 没需求文档/文档不全，或想**对照真实界面**找用例 |
| 确认点 | design.md 等中间产物 | **测试点计划必须你确认后才展开用例**（硬门禁） |

## 2. 四步工作流

```
① 解析输入 ──► ② playwright-cli 探索界面 ──► ③ 出测试点计划（必须等用户确认）──► ④ 展开用例并导出 Excel/XMind
```

### ① 解析输入

- **有需求文档**：抽取功能模块、角色/权限、主流程、规则/校验、异常、数据约束，再对照界面验证；
- **无需求文档：不索要**，直接按 URL 自主探索推断功能，计划中标明「基于界面探索推断」；
- 账号/环境信息不足时做少量假设写入「假设说明」，不反复追问（**登录墙除外**——会停下问你）。

### ② 探索界面（有头，看得见）

```bash
npm install -g @playwright/cli@latest      # 前置安装（首次）
playwright-cli install-browser
playwright-cli open <url> --headed         # 默认有头
playwright-cli snapshot                    # 可加 --depth=N 控制深度
playwright-cli find "关键词"
```

探索规则：
- 盘点导航、菜单、表单、弹窗、列表、空态；无需求时覆盖**一级可达页面**、默认 2 层深度；
- **遇登录**：停下问测试账号；禁止猜密码、绕过鉴权、伪造验证码；
- **遇图形验证码**：截图 → 识别 → 回填，只自动试一次；失败或滑块/点选/短信 → 保持浏览器打开，等人工完成后你回复「继续」；
- 破坏性操作（删全量、支付真单）、外链、登出：**跳过或只记测试点不实操**。

### ③ 测试点计划（硬门禁）

- 产出 `{需求简称或页面标题}-test-plan.md`，测试点 `TP_001` 起编号，覆盖正常/异常/边界/UI；
- **本阶段不写用例**（无 TC 编号、无完整步骤/预期）；
- **有需求时**，「需求 vs 界面」必须拆三块：

| 块 | 内容 |
|----|------|
| 已对齐 | 一致项压缩列举 |
| 不一致 | 对照表（需求怎么写 \| 界面实际怎样 \| **验收基准** \| 对应测试点）——**验收基准必须由你选**（按需求/按界面），技能不替你拍板 |
| 探索未实操 | 缺账号、未点破坏性操作等：写原因 + 是否保留测试点 + 执行前置 |

> ⚠️ **硬门禁**：测试点未获你「确认」→ 禁止导出、禁止生成完整用例。

### ④ 确认后展开并导出

确认后的测试点展开为统一 `cases.json`（字段：`case_id / module / title / priority / precondition / steps / expected / method / page / notes`），再导出：

```bash
pip3 install -r "$SKILL_DIR/scripts/requirements.txt"    # 首次：openpyxl
python3 "$SKILL_DIR/scripts/export_excel.py" <cases.json> <output.xlsx>    # Excel（默认）
python3 "$SKILL_DIR/scripts/export_xmind.py" <cases.json> <output.xmind>  # XMind（明确要求时）
```

## 3. Excel 产物格式（10 列）

Sheet 名「测试用例」，首行冻结，步骤/预期在单元格内换行：

| 列 | 说明 |
|----|------|
| 用例编号 | `TC_001` 起 |
| 模块 | 功能子系统名（如「登录」「订单列表」） |
| 用例标题 | 一句话说明测什么 + 条件，禁止「测试xxx」空标题 |
| 优先级 | 仅 `P0`（冒烟）/ `P1`（核心）/ `P2`（次要） |
| 前置条件 | 账号、数据、环境、入口页；无则写「无」 |
| 测试步骤 | 编号步骤，每步一个动作 |
| 预期结果 | 可观察、可判定 |
| 设计方法 | 如「等价类」「边界值+场景法」，必填可组合 |
| 页面 | 页面路径/标题/路由（如 `/login`） |
| 备注 | 风险、依赖、数据准备；可空 |

## 4. 质量红线与不做的事

**红线**：步骤可执行、预期可判定（禁止「验证功能正常」空用例）；至少覆盖正常路径、关键异常、关键边界；每条必标设计方法。

**不做**：不生成 `.spec.ts` 脚本；测试点未确认不导出；仅给 URL 时不索要需求文档；「需求 vs 界面」不一致时不擅自选定验收基准；登录墙/验证码不绕过不伪造。

## 5. 使用话术

**场景 1：没需求文档，直接从界面出用例**
> 「用 playwright-cli-testcase 探索 https://test.example.com，基于界面生成测试点计划，确认后导出 Excel」

**场景 2：有需求文档，对照界面找差距**
> 「用 playwright-cli-testcase，URL https://test.example.com，需求文档 docs/PRD.md，重点做需求与界面的对照」

**场景 3：确认测试点后导出**
> 「测试点确认，按计划展开用例，导出 Excel 到 test-data/」

## 6. 常见问题

**Q：它和 web-script-author（07 册）能接力吗？**
能但格式不同：本技能出的是 10 列用例文档，不是 25 列；如需走资产库/执行支线，用例需先整理为 25 列（或让 AI 按列映射转换）。

**Q：XMind 什么时候导？**
你明确要才导（Excel 是默认）；XMind 导出无第三方依赖。

**Q：环境要求？**
Node.js（playwright-cli）+ Python3 + openpyxl（仅 Excel 导出需要）。

## 7. 与其他套件的关系

- 思想上被 web-script-author（先采真实 selector）与 miniprogram（先采 WXML）继承；
- 与 playwright-midscene（[15 册](15-技能详解-playwright-midscene-混合UI自动化.md)）互补：本技能出**用例文档**，那套出**可执行代码**。

---

*本册基于 playwright-cli-testcase 1.0.1（2026-10-29 现状）整理。*
