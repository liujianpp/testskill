# Examples：操作手册生成示例

本文件展示两个完整示例，供 Agent 理解输入、探索过程与输出格式。示例中的 URL、ref（e0/e1）和截图文件名为示意，实际执行时以 `playwright-cli snapshot` 输出为准。所有 `open` 命令默认使用 `--headed`。

---

## 示例 A：公开文档站

### 用户输入

```
网站 URL：https://docs.github.com/zh/get-started
产品名称：GitHub 文档中心
目标读者：刚接触 GitHub 的开发者
功能范围：快速入门 — 搜索文档、阅读文章
补充信息：无
登录方式：不需要
输出路径：GitHub文档-操作手册/
```

### 探索清单

| 模块 | 入口 | 计划步骤 | 计划截图 |
|------|------|----------|----------|
| 访问首页 | 直接打开 URL | 打开首页，识别导航结构 | `access-01-homepage.png` |
| 搜索文档 | 顶部搜索框 | 输入关键词 → 查看结果 | `search-01-input.png`、`search-02-results.png` |
| 阅读文章 | 搜索结果点击 | 进入文章页，浏览目录 | `article-01-page.png` |

### 探索过程（摘要）

```bash
playwright-cli open https://docs.github.com/zh/get-started --headed
playwright-cli snapshot
playwright-cli screenshot --filename=GitHub文档-操作手册/assets/access-01-homepage.png

playwright-cli click e5          # 搜索框（ref 以 snapshot 为准）
playwright-cli type "创建仓库"
playwright-cli press Enter
playwright-cli screenshot --filename=GitHub文档-操作手册/assets/search-01-input.png
playwright-cli screenshot --filename=GitHub文档-操作手册/assets/search-02-results.png

playwright-cli click e12         # 第一篇搜索结果
playwright-cli snapshot
playwright-cli screenshot --filename=GitHub文档-操作手册/assets/article-01-page.png

playwright-cli close
```

### 输出目录

```
GitHub文档-操作手册/
├── GitHub文档-操作手册.md
└── assets/
    ├── access-01-homepage.png
    ├── search-01-input.png
    ├── search-02-results.png
    └── article-01-page.png
```

### 输出节选

```markdown
# GitHub 文档中心 操作手册

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品/系统 | GitHub 文档中心 |
| 版本 | 以实际系统为准 |
| 更新日期 | 2026-06-09 |
| 适用对象 | 刚接触 GitHub 的开发者 |
| 访问地址 | https://docs.github.com/zh/get-started |

## 概述

GitHub 文档中心提供 GitHub 平台的使用说明与快速入门指南。

本手册介绍如何访问文档、搜索所需内容并阅读文章。

## 访问与登录

### 访问系统

1. 打开浏览器，访问 https://docs.github.com/zh/get-started。
2. 页面加载完成后，您将看到 GitHub 文档首页。

![GitHub 文档首页](./assets/access-01-homepage.png)

## 搜索文档

### 功能说明

通过顶部搜索框快速查找与 GitHub 相关的帮助文档。

### 操作步骤

#### 步骤 1：输入搜索关键词

**目的**：查找与目标主题相关的文档。

1. 点击页面顶部的搜索框。
2. 输入关键词，例如「创建仓库」。

![搜索框中输入关键词「创建仓库」](./assets/search-01-input.png)

**预期结果**：搜索框下方出现匹配的文档列表。

![搜索结果列表](./assets/search-02-results.png)

## 阅读文章

### 操作步骤

#### 步骤 1：打开文档页面

**目的**：查看完整的操作说明。

1. 在搜索结果中，点击目标文档标题。

![文档文章页面，左侧显示目录导航](./assets/article-01-page.png)

**预期结果**：进入文档详情页，左侧显示章节目录，右侧显示正文内容。
```

---

## 示例 B：需登录后台系统

### 用户输入

```
网站 URL：https://example-admin.com/login
产品名称：订单管理系统
目标读者：运营人员
功能范围：登录、创建订单、导出报表
补充信息：订单金额不能超过 10 万元；导出仅支持 Excel 格式
登录方式：我手动登录
输出路径：订单管理系统-操作手册/
```

### 探索清单

| 模块 | 入口 | 计划步骤 | 计划截图 |
|------|------|----------|----------|
| 登录 | /login | 打开登录页 → 用户手动登录 → 验证 | `login-01-page.png`、`login-02-dashboard.png` |
| 创建订单 | 侧边栏「订单管理」 | 新建 → 填表 → 提交 | `order-create-01-list.png`、`order-create-02-form.png`、`order-create-03-success.png` |
| 导出报表 | 侧边栏「报表中心」 | 选月份 → 导出 | `report-01-page.png`、`report-02-export.png` |

### 探索过程（摘要）

**用户手动登录（验证码 / SSO）**：

```bash
playwright-cli open https://example-admin.com/login --headed
playwright-cli screenshot --filename=订单管理系统-操作手册/assets/login-01-page.png
# 提示用户在浏览器窗口完成登录（含验证码），回复「已登录」后：
playwright-cli snapshot
playwright-cli state-save auth.json
playwright-cli screenshot --filename=订单管理系统-操作手册/assets/login-02-dashboard.png
```

**凭据登录（用户提供账号密码）**：

```bash
playwright-cli open https://example-admin.com/login --headed
playwright-cli snapshot
playwright-cli fill e0 "USER"
playwright-cli fill e1 "PASS"
playwright-cli fill e2 "CAPTCHA"    # 或由用户在可见浏览器窗口完成验证码
playwright-cli click e4
playwright-cli state-save auth.json
playwright-cli goto https://example-admin.com/dashboard
playwright-cli screenshot --filename=订单管理系统-操作手册/assets/login-02-dashboard.png
```

**继续探索各模块**：

```bash
playwright-cli state-load auth.json
playwright-cli open https://example-admin.com/orders --headed
playwright-cli snapshot
playwright-cli screenshot --filename=订单管理系统-操作手册/assets/order-create-01-list.png
playwright-cli click e20                    # 「新建订单」
playwright-cli screenshot --filename=订单管理系统-操作手册/assets/order-create-02-form.png
# ... 提交后截图 success，进入报表中心截图 ...
playwright-cli close
```

### 登录协助对话示例

```
Agent：已用 --headed 打开登录页并截图。请在浏览器窗口中完成登录（含验证码），
       完成后回复「已登录」。
User：已登录
Agent：[playwright-cli snapshot 验证] 检测到已进入工作台，state-save 后继续探索…
```

### 输出目录

```
订单管理系统-操作手册/
├── 订单管理系统-操作手册.md
└── assets/
    ├── login-01-page.png
    ├── login-02-dashboard.png
    ├── order-create-01-list.png
    ├── order-create-02-form.png
    ├── order-create-03-success.png
    ├── report-01-page.png
    └── report-02-export.png
```

### 输出节选

```markdown
# 订单管理系统 操作手册

## 访问与登录

### 登录

**目的**：进入订单管理后台。

1. 打开 https://example-admin.com/login。
2. 输入您的账号和密码，点击「登录」。

![登录页面](./assets/login-01-page.png)

**预期结果**：进入订单管理工作台。

![登录后的工作台，左侧显示订单管理、报表中心等菜单](./assets/login-02-dashboard.png)

## 创建订单

### 功能说明

运营人员可在系统中手动录入新订单。

### 操作步骤

#### 步骤 1：进入新建订单页面

**目的**：打开订单创建表单。

1. 在左侧菜单点击「订单管理」。
2. 点击右上角「新建订单」按钮。

![订单列表页，「新建订单」按钮位于右上角](./assets/order-create-01-list.png)

#### 步骤 2：填写订单信息

**目的**：录入客户与商品信息。

1. 填写客户名称、商品、数量、金额等必填项。
2. 点击「提交」。

![新建订单表单](./assets/order-create-02-form.png)

**预期结果**：页面提示「订单创建成功」。

![创建成功提示](./assets/order-create-03-success.png)

### 注意事项

- 单笔订单金额不能超过 10 万元。
- 如需修改已提交订单，请联系管理员。

## 导出报表

### 操作步骤

#### 步骤 1：导出月度报表

**目的**：下载 Excel 格式的月度统计报表。

1. 在左侧菜单点击「报表中心」。
2. 选择目标月份。
3. 点击「导出 Excel」。

![报表中心页面](./assets/report-01-page.png)

![选择月份并点击导出](./assets/report-02-export.png)

**预期结果**：浏览器自动下载 Excel 文件。

### 注意事项

- 导出格式仅支持 Excel（.xlsx）。
```

---

## 示例对比

| 维度 | 示例 A（公开站） | 示例 B（需登录） |
|------|------------------|------------------|
| 工具 | playwright-cli（有头） | playwright-cli（有头）+ state-save |
| 登录 | 跳过登录章节 | 有头窗口手动登录 或 fill + click |
| 截图 | `screenshot --filename=` | 表单用空白/示例数据 |
| 敏感信息 | 无 | 不出现真实账号；`auth.json` 不提交 git |
| 探索中断 | 少见 | 验证码/权限不足时需用户协助 |
