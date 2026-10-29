# 15 · 技能详解：playwright-midscene-skills（Playwright + Midscene 混合 UI 自动化，4 个技能）

> **一句话**：把用例变成**可进 CI 的代码化 UI 自动化**——稳定界面元素用 Playwright 定位；定位不了的（Canvas 图表、Shadow DOM、跨域 iframe、图形验证码）降级用 **Midscene 视觉模型**兜底。4 个编号技能走完「探索 → 生成代码 → 执行 → 修复」。

[← 返回总导读](README.md) | 套件自带文档：[playwright-midscene-skills/使用说明.md](../../playwright-midscene-skills/使用说明.md)

---

## 1. 三条 UI 自动化路线怎么选（新手第一问）

| 路线 | 代表 | 特点 | 适合 |
|------|------|------|------|
| LLM 现场驱动 | browser-use-case-runner（05 册） | 无代码、灵活，但每次都要 AI 在场 | 探索性测试、快速回归手工用例 |
| 纯 Playwright 代码化 | web-script-author（07 册） | 永久脚本进 CI，但定位不了 Canvas/验证码 | 常规 DOM 界面 |
| **Playwright + Midscene 混合（本册）** | playwright-midscene-skills | 代码化可进 CI **且**视觉模型兜底动态 UI | 界面含 Canvas/Shadow DOM/验证码等难定位元素 |

**核心思想**：稳定 DOM 用 Playwright locator；动态 UI 降级 Midscene Instant Actions（视觉模型驱动）——脚本在 CI/云端**稳定运行**，不依赖本地 AI 的多模态能力。

## 2. 四个技能与流水线

```
@00 探索&计划 ──► @01 生成代码 ──► @02 执行&报告 ──失败且同意修复──► @03 修复 ──► 回 @02 复跑
     (有头)                          (无头)                          (最多 2 轮)
```

| # | 技能 | 职责 | 产出 | 禁止 |
|---|------|------|------|------|
| 00 | `00-playwright-explore-plan` | 有头探索界面，生成探索报告（用例矩阵 + 代码映射 + 每步 driver） | `tests/reports/{case}-report.md`、`tests/explore/{case}-*` | 生成 spec 代码 |
| 01 | `01-playwright-gen-code` | 按探索报告生成/扩展测试代码（Playwright 为主，midscene 步混入） | `tests/{case}.spec.ts`、`tests/pages/*.ts`、fixture、captcha helper | 不探索、不跑测 |
| 02 | `02-playwright-run-report` | 无头执行 + HTML 报告 + 合规校验 | Playwright HTML 报告（localhost:9323） | 不做 heal |
| 03 | `03-playwright-heal` | 修复失败用例（Playwright 步修 locator；Midscene 步只改自然语言 prompt），最多 2 轮 | 修复后的 spec/PO/helper | 修完不自动循环跑 |

各技能结束时只**提示**下一步（不自动串跑），走不走由你。

## 3. 产物目录约定（都在被测项目内）

```
tests/
├── {case-name}.spec.ts            # 测试代码（01 生成）
├── pages/{PageName}.ts            # Page Object（稳定 locator）
├── fixture.ts                     # Midscene fixture（有 midscene 步才建）
├── helpers/captcha.ts             # 图形验证码 helper（有验证码时）
├── auth.setup.ts                  # 登录 setup
├── reports/{case-name}-report.md  # ★ 探索报告（00 产出，01/02/03 的契约源）
└── explore/{case-name}-*          # snapshot / 步骤截图 / auth.json
midscene_run/                      # Midscene 报告与缓存（gitignore）
.env / .env.example                # 模型配置（.env 不入库）
```

## 4. 必懂的关键契约

### 4.1 探索报告（00 交给 01/02/03 的「施工图」）

必须包含：**用例矩阵**（ID、名称、起始 URL、前置、步骤、数据、预期）、**用例 → 代码映射表**、每步 **driver**（`playwright` 或 `midscene`）+ locator/prompt + 降级原因、备选 locator、断言点、auth 路径。
**门禁**：矩阵未写入 report.md 不得继续；01 没有报告不得生成代码。

### 4.2 定位优先级（探索与生成强制）

`data-testid` → role+可访问名称 → `id` → CSS 类+标签 → XPath（尽量避免）→ **降级 Midscene**（不硬扛脆弱 XPath）。

### 4.3 什么时候降级 Midscene（满足任一）

Canvas/WebGL 目标不在可访问树；closed Shadow DOM；跨域 iframe；snapshot 无可用 ref；只有 hash class / 深层 XPath；图形验证码（读图用 `aiQuery`，输入框和按钮仍 Playwright）。

### 4.4 Midscene 只用白名单动作

`aiTap` / `aiInput` / `aiHover` / `aiScroll` / `aiWaitFor` / `aiAssert` / `aiQuery`。
**禁止**：`aiAct` 整段流程、YAML 脚本、第三方 OCR 读验证码。

### 4.5 图形验证码通用模式

逻辑集中在 `tests/helpers/captcha.ts`（不在每条用例复制）；`aiQuery` 读图 + Playwright 填框；分层重试（读码不合格默认最多 3 次、提交后验证码错误默认最多 5 次）；位数/字符集以探索报告为准，不写死。

### 4.6 存量项目硬约束（01）

已有 playwright 配置/依赖时：禁止全量初始化、禁止整文件覆盖已有 PO/fixture/helper；config **只补缺**（timeout、video/trace、Midscene reporter）；同 case-name 的 spec **1:1 原地更新**，不建平行文件。

### 4.7 合规校验（02）

矩阵通过数 = 探索报告矩阵行数（setup 等单独说明，不得混入总 passed）；每条矩阵用例必须有 video 与 trace；报告服务默认端口 9323。

## 5. 环境与依赖

```bash
npm install -D @playwright/cli@latest && npx playwright-cli install   # 00 探索 / 03 调试
npm install -D @midscene/web                                          # 有 midscene 步时
```

`.env`（从 `.env.example` 复制；**模型必须支持视觉/多模态**）：

| 变量 | 说明 |
|------|------|
| `MIDSCENE_MODEL_API_KEY` | 模型 API Key（禁入仓库） |
| `MIDSCENE_MODEL_BASE_URL` | OpenAI 兼容 endpoint |
| `MIDSCENE_MODEL_NAME` | 视觉模型名 |
| `MIDSCENE_MODEL_FAMILY` | 坐标处理族（与模型匹配） |

> 缺 Key / 模型无视觉能力 → **阻塞上报**，不走 locator 修复兜底。

## 6. 使用话术（完整流程 5 步）

```text
1. 「@00-playwright-explore-plan 按用例文件 docs/登录用例.md 探索 https://test.example.com」
2. （看探索报告没问题后）「@01-playwright-gen-code 按报告生成代码」
3. 「@02-playwright-run-report 执行并开报告」
4. 失败 → 它问你修不修 → 回「是」→「@03-playwright-heal 修复」（最多 2 轮）
5. 修完 → 回 @02 复跑验证
```

## 7. 常见问题

**Q：为什么 Midscene 步修复只改「自然语言描述」？**
Midscene 靠视觉模型理解指令，定位问题改 prompt 就够；硬补 XPath 反而更脆。

**Q：没有多模态模型 Key 能用吗？**
能用纯 Playwright 部分，但一旦有 midscene 步会**阻塞上报**——先配好视觉模型。

**Q：能接到统一报告/CI 吗？**
可以：02 产出的 Playwright 结果可转 JSON（playwright-results.json 是 testflow 统一报告第五源）；脚本本身无 AI 依赖，适合 CI。

## 8. 与其他套件的关系

- 与 playwright-cli-testcase（[14 册](14-技能详解-playwright-cli-testcase-探索式用例生成.md)）互补：那边出**用例文档**，这边出**可执行代码与报告**；
- 与 browser-use-case-runner 是两条技术路线：本套**代码化、可进 CI**；
- 与 web-script-author 定位相近，差异在本套有 **Midscene 视觉降级**（专治难定位元素）。

---

*本册基于 playwright-midscene-skills（2026-10-29 现状）整理。*
