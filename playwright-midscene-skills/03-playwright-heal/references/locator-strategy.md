# 元素定位策略

## 优先级顺序（强制）

探索与生成代码时，**必须**按以下顺序选择 locator：

| 优先级 | 策略 | Playwright API | 适用场景 |
|--------|------|----------------|----------|
| 1 | `data-testid` | `page.getByTestId('login-btn')` | 元素有 test id 属性 |
| 2 | role + 可访问名称 | `page.getByRole('button', { name: '登录' })` | 按钮、链接、输入框等有语义 role |
| 3 | `id` | `page.locator('#username')` | id 唯一且稳定 |
| 4 | CSS 类 + 标签 | `page.locator('button.submit-btn')` | 无 testId/role/id 时的结构化选择 |
| 5 | XPath | `page.locator('xpath=...')` | 仅当目标仍是稳定 DOM 且前 4 级不可用 |
| 降级 | Midscene Instant Actions | `aiTap` / `aiInput` / `aiAssert` 等 | 动态 UI：canvas、不稳定 DOM、Shadow/iframe、snapshot 失败 |

## 降级规则

1. 在 `playwright-cli snapshot` 输出中依次检查：`data-testid` → role/name → id → tag+class
2. 属性不可见时用 `playwright-cli eval "el => el.getAttribute('data-testid')" eN` 或 `playwright-cli generate-locator eN --raw`
3. 生成代码时必须映射到对应 Playwright API，不得跳过高优先级；优先采用 CLI 自动输出的代码再校验
4. **优先 Midscene、少用 XPath**：若仅能得到 hash class（如 `.css-1a2b3c`）或深层脆弱 XPath，或目标在 canvas / closed Shadow / 跨域 iframe / snapshot 无 ref，标记 `driver: midscene`，不要用 XPath 硬扛
5. 确需 XPath（稳定 DOM、临时过渡）时必须在代码注释中说明原因
6. 元素缺少 testId 时，在探索报告中标注 `建议添加 data-testid="..."`

## Midscene 降级判定（满足任一）

- Canvas / WebGL / 图表：操作目标不在 a11y tree
- Closed Shadow DOM / 跨域 iframe：snapshot 看不到内部
- snapshot 无可用 `eN`，或 `generate-locator` 只有 hash class / 深层 XPath
- 无 testid、无语义 role、id 不稳定

**不切 Midscene**：表单、按钮、表格、链接——testid 或 role+name 可用即写 Playwright。

完整 Instant Actions、fixture、env 见 [midscene-hybrid.md](midscene-hybrid.md)。

## 各优先级示例

### 1. data-testid

```typescript
await page.getByTestId('username-input').fill('admin');
await page.getByTestId('submit-btn').click();
await expect(page.getByTestId('welcome-message')).toBeVisible();
```

### 2. role + 可访问名称

```typescript
await page.getByRole('textbox', { name: '用户名' }).fill('admin');
await page.getByRole('button', { name: '登录' }).click();
await expect(page.getByRole('heading', { name: '欢迎' })).toBeVisible();
```

常用 role：`button`, `link`, `textbox`, `checkbox`, `radio`, `combobox`, `heading`, `tab`, `menuitem`

### 3. id

```typescript
await page.locator('#username').fill('admin');
await page.locator('#login-form').locator('#submit').click();
```

仅当 id 在页面中唯一时使用，避免 `#content`、`#main` 等通用 id。

### 4. CSS 类 + 标签

```typescript
await page.locator('input.form-control[name="username"]').fill('admin');
await page.locator('button.btn-primary[type="submit"]').click();
```

避免：
- 纯 hash 类名：`.css-1a2b3c`（改用 Midscene）
- 深层嵌套：`div > div > div > span.text`
- 动态生成的 class

### 5. XPath（尽量避免）

```typescript
// XPath: 表格第 2 行操作按钮，无 testId/role/id 可用，且仍是稳定 DOM
await page.locator('xpath=//table[@data-testid="user-list"]//tr[2]//button[text()="编辑"]').click();
```

### 降级：Midscene

```typescript
// driver: midscene — canvas: target not in a11y tree
await aiTap('图表右上角的放大按钮');
await aiAssert('图表已全屏且显示明细坐标轴');
```

## 可见容器 vs 不可见根节点（通用）

部分 UI 库把 `data-testid` 挂在 overlay/modal **根包装节点**上（可能 `aria-hidden` 或 Playwright 判为 hidden），真正可交互的是内部 `role="dialog"` / 表单。

- 若 locator 命中根包装且 `toBeVisible` / 点击失败，而子树存在 dialog 或表单：改用 `getByRole('dialog', { name })`（**name 来自 explore a11y / 报告**），并在 dialog 作用域内找字段与按钮
- testid 可留在根上作辅助查询，但 **可见性断言与交互不以不可见根为准**
- 探索报告须记录：dialog 可访问名、建议作用域 locator；可注明「某 UI 库 modal-root 常 hidden」作提示，非硬编码依赖

```typescript
// name 以 explore report 为准，勿写死业务标题
const dialog = page.getByRole('dialog', { name: dialogNameFromReport });
await expect(dialog).toBeVisible();
await dialog.getByRole('textbox', { name: fieldLabelFromReport }).fill(value);
```

## 断言模板

```typescript
// 可见性
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();

// 文本
await expect(locator).toHaveText('欢迎');
await expect(locator).toContainText('成功');

// 属性
await expect(locator).toHaveAttribute('href', '/dashboard');
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();

// 输入值
await expect(locator).toHaveValue('admin');

// URL
await expect(page).toHaveURL(/dashboard/);
await expect(page).toHaveTitle('首页');

// Midscene 视觉/语义断言（动态步）
await aiAssert('搜索结果列表至少有一行');
```

## 探索报告 locator 记录格式

```markdown
### Step 3: 点击登录按钮

- **driver**: playwright
- **选用**: 优先级 1 — `getByTestId('login-btn')`
- **备选**: 优先级 2 — `getByRole('button', { name: '登录' })`
- **建议**: 密码框缺少 testId，建议添加 `data-testid="password-input"`
```

```markdown
### Step 4: 点击图表放大

- **driver**: midscene
- **reason**: canvas: target not in a11y tree
- **prompt**: 图表右上角的放大按钮
```
