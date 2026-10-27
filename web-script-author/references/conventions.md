# web-script-author 约定（spec 编写与 selector 采集规范）

## spec 文件与命名

- 一条用例一个 `test`；`describe('<模块>', ...)` 按模块组织
- 文件名：`<模块>_<功能>.spec.ts`（kebab/pinyin 均可，仓库内保持一致）
- test 标题：`[CASE:<用例编号>] <用例标题>`——编号沿用 25 列「测试项/测试点」，供 suite.json 与统一报告对齐

## 目录落位

| 场景 | 位置 | import 主干公共层 |
|------|------|------------------|
| 迭代新增 | `web/iterations/<版本号>/`（扁平） | `'../../main/pages/X'`、`'../../main/fixtures/auth'` |
| 主干修正/补充 | `web/main/tests/` | `'../pages/X'`、`'../fixtures/auth'` |

晋级脚本 promote_iteration.py 会自动把 `'../../main/'` 改写为 `'../'`——生成时严格遵守上述相对路径，不要自创层级。

## selector 采集规范

1. **必须真实采集**：`npx playwright codegen <URL>` 或 chrome-devtools 打开真实页面；采集依据记录到 selectors-draft.md（迭代）或 Page Object 注释（主干）
2. **优先级**：getByRole / getByLabel / getByText > data-testid > id > css 类链；禁止依赖会话性 class（哈希后缀）与绝对 xpath
3. **一页一 Page Object**（`web/main/pages/<Page>.ts`）：用例只调方法，不直接写定位器；同一元素多处引用只定义一次
4. **登录态**：一律经 `fixtures/auth.ts`；账号只读 `WEB_USERNAME` / `WEB_PASSWORD`，出现明文即为缺陷
5. **等待**：用 locator 自动等待（toBeVisible / toHaveText），禁止固定 sleep；仅网络型等待用 `page.waitForResponse`

## 断言与用例语义对齐

- 每条 spec 的断言 = 用例「预期结果」列的语义，不增删：用例写"提示密码错误"就断言该提示可见，不额外断言 URL
- 用例步骤写不进 UI 操作的（如"等待短信"）：生成时标注 `// TODO(manual): <原因>` 并在交付说明中列出，不伪造
- 测试数据来自「测试数据准备」列；动态数据（验证码/短信码）不自动化，标注 TODO(manual)

## suite.json 清单格式

```json
{
  "cases": [
    {
      "id": "TC-001",
      "title": "正确账号登录成功",
      "module": "登录",
      "priority": "P0",
      "spec": "main/tests/login_auth.spec.ts",
      "owner": "main | <迭代版本号>"
    }
  ]
}
```

维护规则：按 id 幂等合并（后写覆盖同 id 的 spec/owner 字段）；不删除他人条目；晋级后 owner 改为 "main"。
