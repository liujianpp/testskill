# 07 · 技能详解：web-script-author（25 列用例 → Playwright 界面脚本）

> **一句话**：把 25 列用例里的 UI 用例，逐条转成 **Playwright 自动化脚本**放进测试资产库——以后不需要 AI 在场也能反复跑、进 CI 每日回归。

[← 返回总导读](README.md) | 套件自带文档：[web-script-author/SKILL.md](../../web-script-author/SKILL.md)

---

## 1. 它和 browser-use-case-runner 的区别（新手最常混淆）

| 对比项 | browser-use-case-runner（05 册） | web-script-author（本册） |
|--------|----------------------------------|---------------------------|
| 本质 | AI 现场逐条「手动」点浏览器（LLM 驱动） | 生成**永久脚本**（Playwright spec） |
| 产出 | 当轮 MD 报告 + 截图（无代码产物） | `.spec.ts` 脚本文件 + Page Object + suite.json |
| 以后还要 AI 吗 | 每次执行都要 | **不要**，`npx playwright test` 就能跑，可进 CI |
| 适合 | 探索性测试、手工用例回归、快速验证 | 稳定用例的长期回归沉淀 |

## 2. 输入与前置

| 项 | 说明 |
|----|------|
| 用例来源（三选一） | ① 资产库合表 `test-automation/cases/main/web/<模块>.xlsx`（主干补充）；② spectest 产物 `spectest/changes/<name>/artifacts/<name>_testcases.xlsx`（新迭代，先分拣）；③ 你直接指定的 25 列 xlsx |
| 被测系统 | `BASE_URL`（web/.env 或环境变量）；没给会问你 |
| 落位 | 新迭代必须给版本号（`web/iterations/<版本号>/`）；主干修正直接改 `web/main/` |

## 3. 它怎么干活（6 步）

1. **确定仓库与落位目录**（按上表规则；迭代 spec 扁平放 `web/iterations/<版本号>/`）；
2. **解析用例**：读 xlsx「测试用例」Sheet，过滤出 UI 用例（「API URL」列为空），逐条提取编号/标题/模块/前置/步骤/数据/预期/优先级；
3. **采集 selector（核心纪律）**：
   - 用 `npx playwright codegen <URL>` 或 chrome-devtools 打开**真实页面**采集；
   - **禁止臆造 selector**——每个输入框/按钮/断言元素必须有真实 DOM 依据（role/text/test-id 优先，绝不编造 `data-testid` 假定它存在）；
   - 采集结果写入 Page Object（一页一对象，`web/main/pages/<Page>.ts`；迭代可先落 `selectors-draft.md` 草稿，晋级前人工确认）；
   - 登录态统一走 `fixtures/auth.ts`，账号只读 `WEB_USERNAME` / `WEB_PASSWORD` 环境变量；
4. **逐条生成 spec**：一条用例一个 `test`，标题格式 **`[CASE:<用例编号>] <用例标题>`**（供结果追溯与统一报告对齐）；断言语义对照用例，不擅自增删；
5. **维护清单**：更新 `web/suite.json`（用例编号 → spec 路径 → 所属 → 优先级），幂等合并不删别人条目；
6. **交付说明**：告诉你 spec 路径清单、selector 采集依据、suite.json 变更；建议下一步 `npx playwright test <路径>` 本地验证。

## 4. 产物与验证

```
test-automation/web/
├── main/pages/<Page>.ts          # Page Object（主干）
├── iterations/<版本号>/*.spec.ts  # 迭代 spec（扁平）
│   └── selectors-draft.md        # （迭代时）selector 草稿，晋级前人工确认
└── suite.json                    # 用例 ↔ 脚本清单
```

**它只生成不执行、不下结论**——执行交给 `npx playwright test` 或 CI，结论只认运行结果。

## 5. 使用话术

**场景 1：把本次迭代的用例转脚本**
> 「用 web-script-author 把 test-automation/cases/iterations/2026Q4-login/登录.xlsx 转成 Playwright 脚本，落位 web/iterations/2026Q4-login，被测地址 https://test.example.com」

**场景 2：补充主干脚本**
> 「用 web-script-author 按 cases/main/web/订单.xlsx 补充主干订单模块脚本」

**场景 3：跑起来验证（转交执行）**
> 「npx playwright test web/iterations/2026Q4-login」

## 6. 常见问题

**Q：为什么有的 selector 它不直接写？**
铁规矩：没在真实页面见过的元素不写定位器。避免脚本一生成就跑不通。

**Q：脚本跑挂了找谁？**
先看是不是页面变了（selector 失效）→ 让 AI 按失败报告修订脚本（对照真实页面重新采集）；结论以运行结果为准。

**Q：和 CI 什么关系？**
它生成的脚本落在 `test-automation/web/`，主干部分每天 02:17 被 CI 自动回归（见 [10 册](10-技能详解-test-automation-资产库与CI.md)）；Playwright JSON 结果是统一报告的第五源。

---

*本册基于 web-script-author 2026-10-29 现状整理。*
