# Browser CLI：playwright-cli 命令参考

本文件为 [<skills-root>/SKILL.md](SKILL.md) 内嵌的浏览器操作参考。操作手册生成默认使用**有头模式**（`--headed`）。

## 安装与检查

```bash
playwright-cli --version
# 全局不可用时
npx playwright-cli open https://example.com --headed
```

首次运行可能下载浏览器（约 5–15 分钟，仅首次）。不可用时提示用户安装 playwright-cli。

## Quick start

```bash
playwright-cli open https://example.com --headed
playwright-cli snapshot
playwright-cli click e15
playwright-cli fill e5 "搜索关键词"
playwright-cli screenshot --filename=path/to/screenshot.png
playwright-cli close
```

## 核心命令

### 导航与页面

```bash
playwright-cli open https://example.com --headed   # 打开并导航（默认有头）
playwright-cli goto https://example.com/page     # 当前会话内跳转
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
playwright-cli close
```

### 交互

```bash
playwright-cli snapshot                            # 读取页面结构与 ref
playwright-cli snapshot --filename=after-click.yaml
playwright-cli click e3
playwright-cli dblclick e7
playwright-cli fill e5 "user@example.com"          # 清空后填写
playwright-cli type "追加文字"                      # 追加输入
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli upload ./document.pdf
```

### 截图

```bash
playwright-cli screenshot
playwright-cli screenshot --filename=page.png
playwright-cli screenshot e5 --filename=element.png
```

### 弹窗

```bash
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
```

### 视口

```bash
playwright-cli resize 1920 1080
```

## open 参数

```bash
# 有头模式（操作手册默认必用）
playwright-cli open https://example.com --headed

# 指定浏览器
playwright-cli open --browser=chrome
playwright-cli open --browser=firefox
playwright-cli open --browser=webkit

# 持久化 Profile（长会话手动登录时可选）
playwright-cli open --persistent
playwright-cli open --profile=/path/to/profile

# 配置文件（可选）
playwright-cli open https://example.com --headed --config=.playwright/cli.config.json
```

## Snapshots

每次命令后 playwright-cli 会输出当前页面 snapshot。也可手动执行：

```bash
playwright-cli snapshot
```

输出示例：

```bash
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)
```

- 从 snapshot YAML 中读取元素 ref（如 `e0`、`e1`），用于 `click`、`fill` 等命令
- 未指定 `--filename` 时，snapshot 自动保存到 `.playwright-cli/page-*.yml`
- 操作后务必重新 `snapshot`，验证页面变化

## 登录态（Storage State）

### 保存与恢复

```bash
playwright-cli state-save auth.json
playwright-cli state-load auth.json
playwright-cli open https://example.com/dashboard --headed
```

### Authentication State Reuse 示例

```bash
# 登录并保存
playwright-cli open https://app.example.com/login --headed
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli state-save auth.json

# 后续会话恢复
playwright-cli state-load auth.json
playwright-cli open https://app.example.com/dashboard --headed
playwright-cli snapshot
```

**安全要求**：

- `auth.json` 含 cookie/token，不得提交 git
- 探索结束后删除临时 `auth.json`

## 高级（按需）

复杂交互可用 `run-code`：

```bash
playwright-cli run-code "async page => {
  await page.waitForSelector('.loaded');
  return await page.title();
}"
```

## 操作手册场景命令速查

| 场景 | 命令 |
|------|------|
| 打开站点 | `playwright-cli open <url> --headed` |
| 页面内跳转 | `playwright-cli goto <url>` |
| 查看结构 | `playwright-cli snapshot` |
| 点击 | `playwright-cli click eN` |
| 填写 | `playwright-cli fill eN "value"` |
| 截图 | `playwright-cli screenshot --filename=path.png` |
| 保存登录态 | `playwright-cli state-save auth.json` |
| 恢复登录态 | `playwright-cli state-load auth.json` |
| 结束 | `playwright-cli close` |
