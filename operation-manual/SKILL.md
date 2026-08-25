---
name: operation-manual
description: >-
  根据用户提供的网站 URL 与相关信息，通过浏览器探索页面、自动截图，
  生成带截图的 Markdown 操作手册。适用于操作手册、用户手册、使用指南、
  系统说明书。Use when the user asks for 操作手册、用户手册、使用指南、
  website manual, or wants documentation from a website URL.
allowed-tools: Bash(playwright-cli:*)
---

# 网站操作手册生成

根据用户提供的网站 URL 与补充信息，浏览网站、自动截图，输出带截图引用的 Markdown 操作手册。

## Skill 目录结构

本 skill 封装在 `<skills-root>/` 目录下（即 `operation-manual/` 文件夹）：

```
operation-manual/
├── SKILL.md                      # 主流程（本文件）
├── browser-cli.md                # playwright-cli 命令参考（内嵌）
├── reference.md                  # 浏览器探索与截图规范
├── examples.md                   # 完整示例
└── templates/
    └── manual-template.md        # 操作手册输出模板
```

## 触发场景

- 用户提供网站 URL，要求编写操作手册 / 用户手册 / 使用指南
- 用户要求基于某个系统或产品网站生成说明文档
- 用户提到「截图 + 步骤说明」形式的系统文档

## 工作流

```
Task Progress:
- [ ] Step 1: 收集输入
- [ ] Step 2: 规划探索范围
- [ ] Step 3: 网站探索与截图
- [ ] Step 4: 生成大纲
- [ ] Step 5: 撰写手册
- [ ] Step 6: 润色与输出
```

### Step 1：收集输入

缺失必填项时主动询问。收集完成后复述确认。

| 字段 | 必填 | 说明 |
|------|------|------|
| 网站 URL | 是 | 起始入口 |
| 产品/系统名称 | 是 | 手册标题 |
| 目标读者 | 否 | 默认「普通业务用户」 |
| 功能范围 | 否 | 要覆盖的模块；未指定则按站点导航自动识别 |
| 补充信息 | 否 | 业务背景、术语、特殊注意事项 |
| 登录方式 | 条件 | 需登录时：账号密码 / 用户手动登录 / SSO 说明 |
| 输出路径 | 否 | 默认 `{产品名}-操作手册/` 目录 |

### Step 2：规划探索

1. `playwright-cli open <url> --headed` 打开首页（**默认有头模式**）
2. `playwright-cli snapshot` 识别导航、菜单、主要功能入口（从 ref 如 e0/e1 读取）
3. 结合用户「功能范围」列出待覆盖模块清单
4. 为每个模块规划：入口 → 操作步骤 → 预期结果 → 需截图的节点

详细浏览器操作规范见 [<skills-root>/reference.md](reference.md)。playwright-cli 命令见 [<skills-root>/browser-cli.md](browser-cli.md)。

### Step 3：网站探索与截图

**工具**：使用 **playwright-cli**（命令参考内嵌于本 skill，无需额外 attach 其他 skill）。

```bash
playwright-cli --version          # 检查可用性
# 若全局命令不可用：npx playwright-cli open https://example.com --headed
```

首次运行可能触发浏览器下载（约 5–15 分钟，仅首次）。

**默认有头模式**：所有 `open` 必须带 `--headed`，便于验证码、SSO 及用户协助登录。

**基本顺序**：`open --headed` → `snapshot` → `click`/`fill` → `screenshot`

| 操作 | playwright-cli 命令 |
|------|---------------------|
| 打开站点 | `playwright-cli open <url> --headed` |
| 读页面结构 | `playwright-cli snapshot` |
| 填表/点击 | `playwright-cli fill eN "..."` / `playwright-cli click eN` |
| 截图 | `playwright-cli screenshot --filename={产品名}-操作手册/assets/xxx.png` |
| 保存登录态 | `playwright-cli state-save auth.json` |
| 恢复登录态 | `playwright-cli state-load auth.json` → `open <url> --headed` |
| 结束 | `playwright-cli close` |

**CLI 示例**：

```bash
playwright-cli open http://example.com --headed
playwright-cli snapshot
playwright-cli screenshot --filename="{产品名}-操作手册/assets/access-01-homepage.png"

# 登录
playwright-cli open http://example.com/login --headed
playwright-cli snapshot
playwright-cli fill e0 "USER"
playwright-cli fill e1 "PASS"
playwright-cli click e4
playwright-cli state-save auth.json
playwright-cli goto http://example.com/dashboard
playwright-cli screenshot --filename="{产品名}-操作手册/assets/login-02-dashboard.png"
```

**截图约定**（摘要，详见 reference.md）：

- 保存到输出目录 `assets/` 子目录
- 命名：`{模块}-{步骤序号}-{简述}.png`
- Markdown 引用：`![说明文字](./assets/xxx.png)`
- 截图后立即记录：步骤编号、页面 URL、操作说明
- `auth.json` / `*.auth-state.json` 不得提交 git

**公开页面**：直接探索。

**需登录页面**：

| 场景 | 流程 |
|------|------|
| 用户提供凭据 | `--headed` 打开 → snapshot → fill 账号密码 → 验证码由用户在可见浏览器完成或口头提供后 fill → click 登录 → state-save |
| 验证码 / SSO | 提示用户在已打开的浏览器窗口完成，用户回复「已登录」后 snapshot 验证 → state-save |
| 探索结束 | `playwright-cli close`，删除临时 `auth.json` |

凭据不得写入手册或提交 git。登录失败时停止自动化并请求用户协助。

### Step 4：生成大纲

基于探索结果，按 [<skills-root>/templates/manual-template.md](templates/manual-template.md) 生成大纲：

- 只含标题与一行要点，不写正文
- 向用户展示并等待确认；用户说「直接生成」时可跳过

### Step 5：撰写手册

- 以模板为骨架，填充分步操作说明
- 每步格式：**目的 → 操作 → 截图 → 预期结果**
- 用语：第二人称「您」、祈使句、一步一截图
- 整合用户补充信息（业务规则、注意事项）
- 不包含凭据、内部 API、源码等敏感信息
- 未探索到的功能标注「待补充」，不编造

### Step 6：润色与输出

1. 对说明文字应用 `humanizer-zh` 去 AI 味规则（保留步骤编号与截图引用）
2. 写入输出目录：

```
{产品名}-操作手册/
├── {产品名}-操作手册.md
└── assets/
    └── *.png
```

3. 向用户报告：文件路径、覆盖模块数、截图数量、待补充部分
4. 探索结束后执行 `playwright-cli close`，删除临时 `auth.json`

## 输出约定

- **交付物**：一个 Markdown 文件 + `assets/` 截图目录
- **默认路径**：`{产品名}-操作手册/{产品名}-操作手册.md`
- **语言**：默认中文

## 质量检查清单

完成前逐项确认：

- [ ] 每个功能模块有清晰入口说明
- [ ] 关键步骤均配有截图且路径正确
- [ ] 步骤可独立执行，不依赖隐含知识
- [ ] 无账号密码等敏感信息
- [ ] 术语与用户提供的补充信息一致
- [ ] 未探索到的功能标注「待补充」而非编造

## 附加资源

- 操作手册模板：[<skills-root>/templates/manual-template.md](templates/manual-template.md)
- 浏览器探索与截图规范：[<skills-root>/reference.md](reference.md)
- playwright-cli 命令参考：[<skills-root>/browser-cli.md](browser-cli.md)
- 完整示例：[<skills-root>/examples.md](examples.md)
