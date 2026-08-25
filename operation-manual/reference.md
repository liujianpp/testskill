# Reference：浏览器探索、截图与登录规范

本文件为 [<skills-root>/SKILL.md](SKILL.md) 的补充参考，Agent 在执行 Step 2–3 时按需阅读。

playwright-cli 命令详见 [<skills-root>/browser-cli.md](browser-cli.md)。

## 工具说明

本 skill 自包含浏览器操作能力；**默认有头模式**（`--headed`），便于验证码、SSO 及用户协助。

```bash
playwright-cli --version
# 全局不可用时
npx playwright-cli open https://example.com --headed
```

首次运行可能下载浏览器（约 5–15 分钟，仅首次）。不可用时提示用户安装 playwright-cli，不降级到其他 Browser MCP。

## 基本探索循环

```bash
playwright-cli open https://example.com --headed
playwright-cli snapshot                    # 读取 ref（e0, e1, ...）
playwright-cli click e3                    # 按 snapshot 中的 ref 交互
playwright-cli fill e5 "搜索关键词"
playwright-cli screenshot --filename="{产品名}-操作手册/assets/module-01-page.png"
playwright-cli snapshot                    # 操作后重新 snapshot
```

### 交互原则

- **先 snapshot 再操作**：从 snapshot 输出获取 ref，不要凭猜测点击
- **一次一个操作**：click/fill 后重新 snapshot 验证页面变化
- **避免重复失败**：同一 ref 失败两次后，重新 snapshot 或请求用户协助
- **弹窗**：用 `playwright-cli dialog-accept` / `dialog-dismiss` 处理

## 命令速查（操作手册场景）

| 场景 | playwright-cli 命令 |
|------|---------------------|
| 打开站点（默认） | `playwright-cli open <url> --headed` |
| 页面内跳转 | `playwright-cli goto <url>` |
| 查看结构 | `playwright-cli snapshot` |
| 点击菜单/按钮 | `playwright-cli click eN` |
| 填写表单 | `playwright-cli fill eN "value"` |
| 按键 | `playwright-cli press Enter` |
| 截图整页 | `playwright-cli screenshot --filename=path.png` |
| 截图元素 | `playwright-cli screenshot eN --filename=path.png` |
| 保存登录态 | `playwright-cli state-save auth.json` |
| 恢复登录态 | `playwright-cli state-load auth.json` → `open <url> --headed` |
| 结束探索 | `playwright-cli close` |

## 探索记录格式

每探索一个模块，维护临时笔记：

```markdown
## 模块：{名称}
- 入口：{导航路径}
- URL：{页面地址}
- 步骤：
  1. {操作} → 截图：{文件名}
  2. {操作} → 截图：{文件名}
- 预期结果：{描述}
- 备注：{业务规则、限制}
```

## 截图规范

### 存储位置

```
{产品名}-操作手册/
├── {产品名}-操作手册.md
└── assets/
    ├── access-01-homepage.png
    ├── login-01-page.png
    └── order-create-01-list.png
```

### 命名规则

格式：`{模块}-{两位序号}-{英文简述}.png`

| 部分 | 说明 | 示例 |
|------|------|------|
| 模块 | 功能模块英文名或拼音 | `login`、`order-create` |
| 序号 | 两位数字，从 01 起 | `01`、`02` |
| 简述 | 页面状态或操作简述 | `page`、`form`、`success` |

### CLI 截图

```bash
playwright-cli screenshot --filename="{产品名}-操作手册/assets/login-01-page.png"
playwright-cli screenshot --filename="{产品名}-操作手册/assets/apartment-01-list.png"
```

### Markdown 嵌入

```markdown
![登录页面，显示账号和密码输入框](./assets/login-01-page.png)
```

- 使用相对路径（相对于 .md 文件）
- alt 文字描述截图内容

## 登录场景

### 用户提供凭据

```bash
playwright-cli open https://example.com/login --headed
playwright-cli snapshot
# 根据 snapshot 中的 ref 填写（示例 ref，以实际 snapshot 为准）
playwright-cli fill e0 "USERNAME"
playwright-cli fill e1 "PASSWORD"
playwright-cli fill e2 "CAPTCHA"    # 如有验证码，或由用户在浏览器窗口完成
playwright-cli click e4             # 登录按钮
playwright-cli snapshot             # 验证已进入系统
playwright-cli state-save auth.json
playwright-cli screenshot --filename="{产品名}-操作手册/assets/login-02-dashboard.png"
```

登录态复用模式见 [<skills-root>/browser-cli.md](browser-cli.md) 的 Storage State 章节。

**安全要求**：

- 凭据不得写入 Markdown、不得提交 git
- `auth.json` 加入 `.gitignore`，探索结束后删除
- 截图前确认页面无密码明文显示

### 验证码 / SSO（用户协助）

有头模式下浏览器窗口始终可见，用户可直接在窗口中完成验证码或 SSO：

```bash
playwright-cli open https://example.com/login --headed
playwright-cli screenshot --filename="{产品名}-操作手册/assets/login-01-page.png"
# 提示用户：「请在浏览器窗口中完成登录（含验证码），完成后回复『已登录』」
playwright-cli snapshot             # 用户确认后验证
playwright-cli state-save auth.json
playwright-cli screenshot --filename="{产品名}-操作手册/assets/login-02-dashboard.png"
```

### 恢复会话继续探索

```bash
playwright-cli state-load auth.json
playwright-cli open https://example.com/dashboard --headed
playwright-cli snapshot
```

### 异常处理

| 情况 | 处理方式 |
|------|----------|
| 登录失败 | 报告错误，请用户确认凭据或在浏览器窗口重试 |
| 验证码 / 2FA | 提示用户在可见浏览器窗口完成，或请用户提供验证码后 `fill` |
| SSO 跳转 | 用户在浏览器窗口完成 SSO，回复「已登录」后继续 |
| 会话过期 | 重新登录；手册注明需重新登录 |
| playwright-cli 不可用 | 提示安装；参考 [<skills-root>/browser-cli.md](browser-cli.md) |
| 无 GUI 环境 | 临时去掉 `--headed`，改用手动截图占位，标注「截图待补充」 |

## 多模块探索示例

```bash
playwright-cli open http://example.com/login --headed
playwright-cli snapshot
playwright-cli fill e0 "admin"
playwright-cli fill e1 "password"
playwright-cli click e4
playwright-cli state-save auth.json

playwright-cli goto http://example.com/apartment
playwright-cli snapshot
playwright-cli screenshot --filename="{产品名}-操作手册/assets/apartment-01-list.png"
playwright-cli click e20              # 「新增公寓」按钮（ref 以 snapshot 为准）
playwright-cli screenshot --filename="{产品名}-操作手册/assets/apartment-02-form.png"

playwright-cli close
```

复杂交互可用 `playwright-cli run-code "async page => { ... }"`，见 [<skills-root>/browser-cli.md](browser-cli.md)。

## 降级策略

无法自动探索时，不编造内容：

```markdown
> 📷 截图待补充（原因：需登录 / 验证码 / 权限不足）
```

## 与其他 Skill 的协作

| Skill | 用途 |
|-------|------|
| `humanizer-zh` | Step 6 润色说明文字（可选） |
| `outline-to-article` | MD 格式参考 |

## MD 输出规范

- 文档标题用单个 `#`
- 模块用 `##`，步骤用 `####` 或有序列表
- 不跳级；步骤编号在同一模块内连续
- 段落之间空一行
