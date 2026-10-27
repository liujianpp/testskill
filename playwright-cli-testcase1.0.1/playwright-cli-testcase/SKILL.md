---
name: playwright-cli-testcase
description: >-
  用 playwright-cli 探索 Web 界面，结合可选需求文档先生成测试点，用户确认测试点后再生成完整用例并导出
  Excel（默认）或 XMind。Use when the user provides a URL and wants Web 测试用例、测试点、
  测试计划、自行探索、无需求、playwright-cli 探索，或要求导出 Excel/XMind 用例。
---

# Playwright 探索式 Web 测试用例

根据用户提供的 **URL（必填）** 与 **需求文档（可选）**，用 `playwright-cli` 探索真实界面，**先产出测试点**；**用户确认测试点 OK 后**再直接生成完整用例并导出。

不生成 Playwright 自动化脚本（`.spec.ts`）。

## 输入与输出

| 项目 | 说明 |
|------|------|
| URL | **必填**；缺地址则先问用户，不凭空编页面 |
| 需求文档 | **可选**；粘贴文本或工作区内 `.md` / `.txt` / `.docx` / `.pdf` |
| 无需求时 | **不要索要需求文档**；直接按地址自主探索并推断功能 |
| 默认输出 | `.xlsx` Excel |
| 可选输出 | `.xmind`（用户明确要求时）；可同时导出两种 |
| 路径 | 用户指定则用指定路径，否则当前工作目录 |

详细字段见 [references/excel-columns.md](references/excel-columns.md)。  
设计方法见 [references/test-methods.md](references/test-methods.md)。  
计划模板见 [references/plan-template.md](references/plan-template.md)。

## 工作流程

### 1. 解析输入

- 有需求：抽出功能模块、角色/权限、主流程、规则/校验、异常、数据约束；再对照界面验证。
- 无需求：进入自主探索；计划中标明「基于界面探索推断，未提供需求文档」。
- 登录账号、环境等不足时做少量假设并写入「假设说明」，不要反复追问（**登录墙除外**）。

### 2. 用 playwright-cli 探索

前置：`playwright-cli --help`；没有则提示安装：

```bash
npm install -g @playwright/cli@latest
playwright-cli install-browser
```

通用约定：

```bash
playwright-cli open <url> --headed # 默认有头；仅用户明确要求时去掉 --headed
playwright-cli snapshot            # 或 --depth=N / 局部 snapshot
playwright-cli find "关键词"
# 点击、填写、提交等真实交互
playwright-cli close
```

- 用 `snapshot` / `find` 盘点控件；点进相关页面、表单、弹窗、列表、空态。
- **遇登录**：停下问测试账号；禁止猜密码、禁止绕过鉴权、拦截或伪造验证码接口。
- **遇验证码**：
  - 纯字符图片验证码：`snapshot` 取得图片与输入框 ref → `playwright-cli screenshot <图片ref> --filename <工作区截图路径>` → 用当前模型读取该图片并识别字符 → `fill` 回输入框并提交。只自动尝试一次。
  - 识别不清、提交后仍提示验证码错误，或不是纯字符图片验证码（滑块、点选、短信、邮箱、reCAPTCHA 等）：不自动识别。保持有头浏览器打开，请用户手动完成后回复「继续」。
- 记录：URL/标题、可见模块、关键控件与文案、校验提示。
- 复杂页用 `--depth` 或局部 snapshot，避免整树撑爆上下文。

**有需求时**：按需求模块定向探索，记录「需求 vs 界面」对照（见第 3 步：已对齐 / 不一致 / 未实操），**不得擅自替用户选定验收基准**。

**无需求时（自主探索）**：

- 从给定 URL 出发，先盘信息架构：导航、菜单、Tab、侧栏、页内入口。
- 覆盖**一级可达页面**（同站、同域为主）；每页探主交互：表单校验、列表 CRUD、弹窗、空态/错误态（能触发则触发）。
- 深度默认 **2 层**（入口页 + 点进去的一级页面）；站点很大时优先主导航与入口页主流程，不整站爬虫。
- 外链、登出、破坏性操作（删全量数据、支付真单）跳过或只记测试点不实操。
- 根据真实 UI **推断模块名与功能**，作为测试点来源。

探索目的是对齐真实 UI，**不是**录制自动化代码。不要用浏览器 MCP 作为主路径；仅当 CLI 完全不可用时说明，仍优先修 CLI。

### 3. 先出测试点，必须等确认

按 [references/plan-template.md](references/plan-template.md) 写出计划文件，对话中给出摘要：

- 有需求：`{需求简称}-test-plan.md`；含需求摘要 + 探索结论。
- 无需求：`{页面标题或站点简称}-test-plan.md`；用「界面推断功能」+ 已探索页面清单；「需求 vs 界面」写「不适用」。
- **测试点**：`TP_001` 起，覆盖正常 / 异常 / 边界 / UI。
- **本阶段不写用例计划**（不提前给 TC 编号、标题、优先级、设计方法），也不写完整步骤。

**有需求时的「需求 vs 界面」必须拆成三块**（模板见 plan-template）：

1. **已对齐**：需求与界面一致的事实，压缩列举即可。
2. **不一致**：做成对照表——「条目 | 需求怎么写 | 界面实际怎样 | 验收基准 | 对应测试点」。**验收基准须用户选择**（按需求 / 按界面），不得默认替用户拍板。对话中用清晰对照逐条（或分组）询问；用户选定后再写入计划并据此定测试点预期方向。
3. **探索未实操**：不是需求/界面冲突（缺第二账号、未点破坏性删除、联动未实操等）。写清原因 + 是否仍保留测试点 + 执行前置；不要写成缺陷清单。

**硬门禁：**

- 存在「不一致」且用户尚未选定验收基准时：可先出计划草稿与测试点，但**不得**进入「请确认测试点 OK / 导出」的终态；先问清基准并回写计划。
- 测试点未确认不得导出 Excel/XMind，不得生成完整步骤与用例。

终态询问：请判断测试点是否 OK；回复「确认」后直接生成测试用例并导出；或指出增删改测试点。

### 4. 确认后生成用例并导出

将确认后的测试点展开为统一 JSON（每条测试点对应一条或多条完整用例），再调用脚本。本 Skill 目录记为 `SKILL_DIR`。

```json
{
  "title": "需求名或页面标题",
  "assumptions": "可选：假设说明",
  "cases": [
    {
      "case_id": "TC_001",
      "module": "模块名",
      "title": "用例标题",
      "priority": "P0",
      "precondition": "前置条件",
      "steps": "1. ...\n2. ...",
      "expected": "1. ...\n2. ...",
      "method": "场景法+边界值",
      "page": "页面路径或标题",
      "notes": ""
    }
  ]
}
```

**默认 Excel：**

```bash
python3 "$SKILL_DIR/scripts/export_excel.py" <cases.json> <output.xlsx>
```

**用户要 XMind / 脑图时：**

```bash
python3 "$SKILL_DIR/scripts/export_xmind.py" <cases.json> <output.xmind>
```

依赖：`pip3 install -r "$SKILL_DIR/scripts/requirements.txt"`（若缺包）。

文件名默认：`{需求简称或页面标题}-web-testcases.xlsx`（及同名 `.xmind`）。  
导出后告知文件路径；对话中可简要列出模块与用例数量，不必贴全表。

## 质量红线

- 步骤可执行、预期可判定
- 至少覆盖：正常路径、关键异常、关键边界（按模块体量裁剪）
- 禁止「验证功能正常」类空用例
- 每条用例标注 `method`（可组合）
- 优先级：P0 冒烟、P1 核心、P2 次要

## 不做的事

- 不初始化 Playwright 测试工程，不生成 `.spec.ts`
- 不在测试点未确认时直接导出用例
- 仅给 URL 时不要先向用户要需求文档
- 有需求且存在「不一致」时，不擅自替用户选定「按需求」或「按界面」验收基准
