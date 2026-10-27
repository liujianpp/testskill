# WXML 选择器与 Inspect 解读

供 `@miniprogram-script-author` 对照 inspect 编写 Jest spec 时使用。

## miniprogram-automator 选择器规则

与 WXSS 相同，仅支持部分 CSS 选择器（详见[微信官方文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/auto/page.html)）：

| 选择器 | 示例 | 说明 |
|--------|------|------|
| ID | `#login-btn` | 最优先 |
| class | `.index-desc` | 须 inspect 确认唯一性 |
| 属性 | `[data-id="foo"]` | 推荐用于测试专用标记 |
| 组合 | `view.index-desc` | 缩小范围 |

**限制**：`page.$()` / `page.$$()` **不能**选中自定义组件内部节点；须先 `page.$('custom-comp')` 再 `element.$('.inner')`。

## Inspect 文件解读

### WXML 快照（`.wxml`）

由 `element.wxml()` 或 `page.$('page').wxml()` 生成，反映当前渲染树。编写 spec 时：

1. 在 WXML 中定位目标控件的 `id`、`class`、`data-*`。
2. 核对文案是否在 `<text>` 或子节点中（断言用 `element.text()`）。
3. 同名 class 多处出现时，用父级结构或 `$$()` 过滤。

### 元数据（`.meta.json`）

```json
{
  "path": "/pages/login/login",
  "query": {},
  "data": { "username": "" },
  "capturedAt": "2026-06-29T12:00:00.000Z"
}
```

用于确认页面路径、路由参数与 `setData` 影响；写 `reLaunch` / `navigateTo` 时参照 `path`。

## 常用 Element API（编写 spec）

| 操作 | API | inspect 依据 |
|------|-----|--------------|
| 点击 | `await element.tap()` | 元素存在于 WXML |
| 输入 | `await element.input('text')` | `input` / `textarea` |
| 读文案 | `await element.text()` | WXML 内文本节点 |
| 读属性 | `await element.attribute('class')` | WXML 属性 |
| 触发事件 | `await element.trigger('tap', { detail: {} })` | 非 tap 场景 |
| 断言数据 | `await page.data('field')` | `.meta.json` 的 data |

## 选择器优先级（编写 spec）

1. **`id`** / **`data-testid`**（若项目有测试标记）
2. **经 inspect 核对的 class**（唯一或配合父级）
3. **文案** — 通过 `$$()` 遍历匹配 `text()`（脆弱，仅作兜底）
4. **避免** — 纯坐标、未验证的深层 class 链

## 动态列表

```javascript
const rows = await page.$$('.list-item');
for (const row of rows) {
  const text = await row.text();
  if (text.includes('目标行')) {
    await row.tap();
    break;
  }
}
```

左滑等手势：优先 `callMethod` 或页面提供的测试入口；无稳定 API 时在 inspect 中记录坐标并注明设备依赖。

## 登录与会话（编写时须知）

- **业务用例**：`ensureLoggedIn(miniProgram)` —— 已登录则复用会话，未登录才执行登录（suite / 单跑均适用）。
- **测登录本身**：`forceLogin(miniProgram, account, password)` —— 清 storage 后登录。
- **测退出**：先 `ensureLoggedIn`，再点退出；退出后勿再假定有 token。

## 与 Maestro hierarchy 的对照

| Maestro | 小程序 |
|---------|--------|
| `maestro hierarchy` | `element.wxml()` + `page.data()` |
| `accessibilityText` / `resource-id` | WXML `id` / `class` / `text()` |
| `tapOn: "文案"` | `page.$()` + `tap()` 或 `$$()` 过滤 |
