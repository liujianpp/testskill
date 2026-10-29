# 05 · 技能详解：browser-use + browser-use-case-runner（Web UI 用例执行）

> **一句话**：把测试用例交给 AI，它打开一个**看得见的浏览器**，像人一样逐条点、填、验证，最后出带截图的执行报告（PASS / FAIL / BLOCKED）。

[← 返回总导读](README.md) | 套件自带文档：[browser-use-case-runner/使用说明.md](../../browser-use-case-runner/使用说明.md)、[browser-use/使用说明.md](../../browser-use/使用说明.md)

---

## 1. 两个技能的分工

| 技能 | 角色 | 给谁用 |
|------|------|--------|
| `browser-use-case-runner` | **用例执行器**：定义输入形态、执行节奏、当轮配置、留痕与报告 | 给你（测试人员）用 |
| `browser-use` | **浏览器 CLI 命令手册**：state/input/click/screenshot 等命令的行为契约 | 给 AI 查的（你一般不直接用） |

> 依赖关系：case-runner 只引用 browser-use 文档化过的命令，**不得臆造**未文档化子命令（如 `browser-use ocr` 不存在）。

## 2. browser-use-case-runner 详解

### 2.1 输入：用例三选一（可组合）

| 方式 | 说明 |
|------|------|
| 表格 `.xlsx` | 首行表头；推荐列：用例编号/用例名称/功能模块/优先级/前置条件/测试步骤/测试数据/预期结果（脚本按表头名匹配） |
| Markdown `.md` | 每条用例一个 `## <编号> <名称>` 二级标题 + 粗体标签子弹（模块/优先级/前置/步骤/数据/预期） |
| 手动输入 | 对话里直接给字段，不用落盘 |

导出统一中间格式 JSONL（字段键：`id, name, module, priority, preconditions, steps, data, expected, source`）：

```bash
# 在被测项目仓库根目录执行
python3 .claude/skills/browser-use-case-runner/scripts/test_cases_export.py xlsx test-data/登录-测试用例.xlsx -o reports/cases.jsonl
```

### 2.2 当轮 run-config（强制，先于一切浏览器操作）

每轮必须生成 `reports/run-config-<UTC>.json` 作为**当轮唯一真源**：

```bash
python3 .claude/skills/browser-use-case-runner/scripts/generate_run_config.py \
  --jsonl reports/cases-<标签>.jsonl \
  --source "xlsx:<相对路径或来源描述>" \
  --defaults .claude/skills/browser-use-case-runner/runner-config.json
```

| 关键字段 | 说明 |
|----------|------|
| `sessionStrategy` | `single-session`（同一浏览器连续执行）或 `fresh-per-case`（每条前关掉重开） |
| `inferredSuiteKind` | 脚本自动推断登录类套件 → 默认 fresh-per-case；其他 → 默认 single-session |
| `videoRecording.enabled` | **默认 false（只做关键步骤截图留痕）**；true 仅当你显式要整屏录屏 |
| `userOverrides` | 记录你对策略/录屏的确认 |

流程：导出 JSONL → 生成 run-config → **短问短答**确认（缺 URL 只问 URL；录屏默认不问）→ 整轮只读此文件。**未生成 run-config 不得开始执行。**

> ⚠️ 已知不一致：仓库的 runner-config.json 模板当前 `"enabled": true`，与文档默认 `false` 不符——建议把模板改回 `false`，或每轮生成后核对。

### 2.3 执行节奏（默认规则，小白必知）

1. **连续执行**：终端逐条输出 `[id] START` → `STEP n` → `STATE 摘要` → `[id] RESULT: PASS|FAIL|BLOCKED`；PASS 且无需人工 → 自动下一条；
2. **遇阻即停**：断言失败 / CLI 错误 / 需要验证码、短信、扫码、U 盾等人工操作 → 立即停下汇报，不擅自重试；
3. **验证码三级兜底**：截图落盘 → 视觉识别（**必须报告置信度**）→ 停下等你回复；不得伪造通过、不得绕过风控；
4. **可选覆盖**（仅你显式声明）：「逐条停顿」（每条含 PASS 后即停）、「失败也继续」。

### 2.4 执行方式与留痕

- AI 每条先 `state` 拿元素索引再交互；**索引跨页会变，禁止硬编码复用旧索引**；
- 断言对照「预期结果」与页面文案/state；无法自动判定（如「与产品文案一致」）→ 如实标 **BLOCKED**；
- **留痕（默认方式）**：关键步骤 + 结论态各至少一张截图 → `reports/screenshots/<用例id>-step<n>.png` 与 `<用例id>-result.png`，报告必须引用；
- **整屏录屏（可选，默认关）**：仅当你显式要求时走 ffmpeg 外部录屏（非 browser-use 内置能力）。

### 2.5 报告产物

```
reports/
├── run-config-<UTC>.json       # 当轮唯一真源
├── cases-<标签>.jsonl           # 导出的用例
├── case-run-<时间>.md           # ★ Markdown 报告（每条一小节：结果+依据+截图路径；末尾汇总）
└── screenshots/                 # 关键步骤 / 结论态 / 验证码截图
```

### 2.6 使用话术

**场景 1：执行一张现成用例表**
> 「用 browser-use-case-runner 执行 test-data/登录模块用例.xlsx，被测地址 https://test.example.com」

**场景 2：失败也继续 + 逐条停顿**
> 「……执行上面的用例，失败也继续，逐条停顿」

**场景 3：手动给一条用例**
> 「手动给你一条用例执行：编号 TC-001，步骤：……，预期：……，地址 https://xxx」

**场景 4：首次接入先冒烟**
> 「先用 1 条用例做冒烟验证，确认 headed 生效、截图落盘、报告路径正常」（建议新环境先这样跑一遍）

## 3. browser-use 命令手册（供了解，AI 自己会用）

核心工作流：`open <url>`（打开）→ `state`（★ 拿元素索引）→ `click <索引>` / `input <索引> "文本"`（交互）→ `state`/`screenshot`（验证）。后台 daemon 常驻，浏览器跨命令存活。

| 类别 | 常用命令 |
|------|----------|
| 浏览器模式 | `open`（默认无头）/ `--headed open`（可见窗口）/ `connect`（接管你已开的 Chrome，保留登录态） |
| 导航 | `back`、`scroll down/up`、`tab list/new/switch/close` |
| 状态 | `state`（元素索引来源）、`screenshot [path]` |
| 交互 | `click <索引>`、`input <索引> "text"`、`keys "Enter"`、`select`、`hover` 等 |
| 等待 | `wait text "文案"`、`wait selector "css"` |
| 会话 | `close`、`close --all`、`sessions`、`doctor`（诊断） |

多会话（`--session NAME`）、云浏览器（`cloud connect`）、隧道（`tunnel`）等进阶用法见 [browser-use/使用说明.md](../../browser-use/使用说明.md)。

## 4. 常见问题

**Q：弹验证码怎么办？**
它会截图 → 尝试识别并告诉你把握多大 → 停下等你回复验证码内容。你回「跳过本条」或「刷新再截」也行。

**Q：执行到一半断了，前面算数吗？**
算。每条结论实时写入 MD 报告，中断前的结果都在。

**Q：它和 web-script-author 有什么区别？**
case-runner 是「AI 现场逐条手动点」（灵活、无需写代码，但每次都要 AI 在场）；web-script-author 是「生成永久 Playwright 脚本」（以后进 CI 自动跑）。见 [07 册](07-技能详解-web-script-author-界面脚本生成.md)。

**Q：和生产环境/风控的关系？**
测试环境建议关闭或固定验证码；生产环境风控**不得绕过**——这是红线。

## 5. 和其他技能的关系

- 上游：testflow 转换器把 25 列 Excel 转成 8 列 `ui_cases.xlsx` 给它执行；
- 底层：browser-use CLI（本册 §3）；
- 报告被 testflow 阶段 4 汇总（五源之一）。

---

*本册基于两技能 2026-10-29 现状整理。*
