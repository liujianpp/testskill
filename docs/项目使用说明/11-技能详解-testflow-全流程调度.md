# 11 · 技能详解：testflow（测试全生命周期调度器）

> **一句话**：**总指挥**。你说一句「跑完整流程」，它就把「需求评审 → 用例设计 → 三支线执行 → 统一报告 → 归档」串成一条链，到每个环节就切换对应技能去干活，每阶段结束停下来向你汇报。

[← 返回总导读](README.md) | 套件自带文档：[testflow/使用说明.md](../../testflow/使用说明.md)、[用户指南](../../testflow/references/user-guide.md)

---

## 1. 它是什么（地图 + 转换器 + 汇总器）

testflow **自己不含任何测试能力**，只做三件事：

1. **画地图**：按流程调度各阶段技能（到某阶段就移交控制权，结束收回）；
2. **转格式**：25 列 Excel → 执行器 8 列（`convert_25col_to_ui_xlsx.py`，UI 与小程序支线共用）；
3. **汇报告**：五源统一报告（`aggregate_reports.py`）。

## 2. 全景流程（5 阶段 + 1 预热）

```
阶段0(可选)   阶段1        阶段2              阶段3                 阶段4       阶段5
需求预热   →  需求评审  →  用例设计        →  执行（三支线）     →  统一报告  →  归档
api-doc-gen   prd-review   spectest 9步        3A 接口(可选)         汇总脚本     spectest-archive
                                               3B Web UI(默认)                   (可选 operation-manual)
                                               3C 小程序(可选)
```

| 阶段 | 入口技能 | 关键产物 | 什么时候跑 |
|------|---------|---------|-----------|
| 0 预热 | api-doc-generator | 接口文档 | **只有源码、没需求文档**时垫底 |
| 1 需求评审 | prd-review | 5 维评审报告 MD | 默认起点 |
| 2 用例设计 | spectest（new→analysis→plan可选→points→generate→review→fix） | **25 列 `artifacts/<name>_testcases.xlsx`** | 阶段 1 后 |
| 3A 接口支线 | ApiAutoTest2.0 四技能链 | Allure 报告 | **仅你显式要求**（或有源码且你同意） |
| 3B UI 支线 | 转换器 + browser-use-case-runner | `ui_cases.xlsx` + MD 报告 + 截图 | **默认支线** |
| 3C 小程序支线 | 转换器 + miniprogram 三件套 | `mp_cases.xlsx` + Jest spec + Session 报告 | 仅你显式声明含小程序 |
| 4 统一报告 | aggregate_reports.py | `artifacts/unified-report.md` | 任一支线完成后 |
| 5 归档 | spectest-archive（可选 operation-manual） | 归档目录 / 操作手册 | 你确认后 |

**默认链路：1 → 2 → 3B → 4**。3A / 3C 不会自动启动。

## 3. 最重要的三条运行规则

1. **每阶段结束必汇报等你确认**（产物路径 + 统计 + 下一步选项），不自动串联——你始终握着方向盘；
2. **断点续跑**：中断后（哪怕直接关对话）再说一次 `/testflow`，它按产物存在性判断进度，告诉你「已完成阶段 X，可从 X+1 继续」；
3. **阶段 2 不停靠**：test-plan.md 与 design.md 自动生成不停等（供事后审阅）；单独跑 spectest 技能时才停靠确认。

## 4. 一次完整对话长什么样（真实剧本）

```
你：   /testflow docs/需求-登录改造.md
Agent: 定位状态目录 → 新建 spectest/changes/login-v2/
       ── 阶段1 需求评审 ──（调用 prd-review）
       ✅ 评审完成：test-review-report.md，发现 3 个可测性风险
       下一步：进入用例设计？[继续 / 调整 / 停]
你：   继续
Agent: ── 阶段2 用例设计 ──（依次 spectest-new→analysis→points→generate→review→fix）
       ✅ 用例就绪：artifacts/login-v2_testcases.xlsx（25列，共 42 条）
       下一步：转 UI 用例并执行？需要被测 URL
你：   https://test.example.com，继续
Agent: ── 阶段3B UI 支线 ──
       转换：42 行 → 导出 38 条（跳过 API 用例 4 条）
       （browser-use-case-runner 逐条有头执行……遇验证码会停下问你）
       ✅ 执行完成：reports/case-run-xxx.md（PASS 30 / FAIL 6 / BLOCKED 2）
       下一步：生成统一报告？
你：   继续
Agent: ── 阶段4 统一报告 ──
       ✅ artifacts/unified-report.md（总览 + 需求覆盖 + 明细 + 风险）
```

## 5. 你可能被问到的问题（提前准备）

| 问题 | 什么时候问 | 怎么答 |
|------|-----------|--------|
| 被测 URL？ | 阶段 3B 执行前 | 给测试环境地址 |
| 会话策略？ | 3B 执行前 | 登录类套件默认每条重开浏览器；其他默认同一浏览器连续跑——**用默认直接回「默认」** |
| 要跑接口支线吗？ | 有后端源码时 | 想跑就说「跑，源码在 backend/」 |
| 含微信小程序吗？ | 需求/用例指向小程序时 | 含就说「包含小程序端」（首次需一次性环境准备，见 [06 册](06-技能详解-miniprogram-小程序自动化.md)） |
| 验证码？ | 执行中弹出 | 在对话里回复验证码内容，或「跳过本条」 |

## 6. 统一报告（五源合一）

```bash
python <testflow-skill-dir>/scripts/aggregate_reports.py \
  --excel artifacts/<name>_testcases.xlsx \
  [--allure-dir <allure-results>] [--ui-report <UI MD 报告>] \
  [--mp-report <小程序台账或 Session 报告>] [--playwright-json <playwright-results.json>] \
  --output artifacts/unified-report.md
```

- **五源**：25 列 Excel 执行结果 / Allure / UI MD 报告 / 小程序报告 / Playwright JSON——**缺哪个跳哪个**；
- 报告四节：执行总览（通过率 = 通过/(通过+失败)，**阻塞单列不进分母**）/ 需求覆盖对照 / 各支线明细 / 风险与建议；
- ⚠️ `--ui-report` / `--mp-report` 路径不存在时**静默跳过**不报错——如果你明明跑了却显示「未生成」，检查传的路径对不对。

## 7. 硬性规则（它不会越权的事）

- 不修改各技能内部逻辑与产物格式；
- 不做 testcases.json ↔ cases.json 互转（需求驱动链与代码驱动链独立，仅在报告汇合）；
- 3B 与 3C 互不转换：同一 25 列源头分别转出 `ui_cases.xlsx` / `mp_cases.xlsx` 各自执行，结果在阶段 4 汇合分列展示；
- UI 执行遇验证码/人工介入遵循 case-runner 自身停等规则。

## 8. 使用话术

**标准全流程**
> 「跑一次完整 testflow，需求文档在 docs/PRD.pdf，被测地址 https://test.example.com」

**要接口支线**
> 「……同上，后端源码在 backend/，要跑接口支线」

**要小程序支线**
> 「……同上，包含微信小程序端」

**续跑**
> 「/testflow」（直接再发一次，它自动判断进度）

**只想要其中一段？** 各套件独立可用，不必走 testflow——见 [总导读 §5 速查表](README.md#5-场景速查表我该用什么)。

## 9. 产物清单（一次全流程跑完你手上有什么）

```
<被测项目>/spectest/changes/<变更名>/
├── proposal.md                  # 立项提案（附评审报告路径）
├── project_info/                # 需求分析产物
├── specs/                       # 测试点
├── artifacts/
│   ├── <变更名>_testcases.xlsx  # ★ 25 列标准用例
│   ├── ui_cases.xlsx            # UI 执行入口
│   ├── mp_cases.xlsx            # 小程序执行入口（如走 3C）
│   ├── api/                     # 接口支线记录（allure 路径等）
│   ├── mp/                      # 小程序支线记录（报告路径等）
│   └── unified-report.md        # ★ 统一报告
└── db_info/                     # DB 断言配置

另有运行期产物在被测项目根：reports/（UI 报告+截图；小程序 Session 报告）、docs/（接口支线文件）
```

## 10. 常见问题

**Q：转换后导出 0 行？**
说明 25 列全是 API 用例或全被过滤——它会停下与你核对，不硬跑空批次。

**Q：UI 跑一半失败，前面算数吗？**
算。每条结论实时写入报告；统一报告如实反映，失败/阻塞不会被隐藏。

**Q：能只用某个阶段吗？**
能。testflow 只是帮你按正确顺序串起来；单独 `/prd-review`、单独跑 api-test-runner 都没问题。

---

*本册基于 testflow 2026-10-29 现状整理。*
