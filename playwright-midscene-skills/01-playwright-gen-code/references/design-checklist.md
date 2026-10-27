# 生成前设计自检清单

生成测试代码前，AI **必须逐项确认**。全部通过后方可进入 Step 3 写码。

## 存量 Playwright

- [ ] 已探测：`playwright.config.*` 或 `package.json` 中 `@playwright/test`
- [ ] 无 Playwright → 才允许全量 `init-playwright.sh`；已有 → **禁止**全量 init
- [ ] 已确定沿用路径：`testDir`、PO 目录、fixture（若有）、auth.setup / helpers（若有）
- [ ] 同 case-name 的 spec 已存在 → 在原文件内按矩阵更新，不新建第二份
- [ ] 同页面已有 PO → 扩展方法/locator，不新建平行类（如 `LoginPage2`）
- [ ] 已有 fixture / helper → 复用或扩展，**禁止**整文件覆盖、禁止另写第二份
- [ ] config **只补缺失**的 `video` / `trace` / `timeout` / Midscene reporter；**禁止**重写 `projects` 与自定义 reporter 整表

## 用例矩阵

- [ ] 已输出用例矩阵（ID / 名称 / 前置 / 步骤 / 预期）
- [ ] 矩阵已写入 `tests/reports/{case-name}-report.md` 顶部
- [ ] 矩阵每行对应 **1 个 `test()`**，无多场景合并
- [ ] 探索报告含 **用例 → 代码映射表**
- [ ] 每步已标注 **driver**（`playwright` \| `midscene`）；midscene 步含 reason + prompt

## 独立性与数据

- [ ] 每条用例可单独运行，不依赖上一条用例结果
- [ ] 写/改/删/刷新验证类用例使用 `Date.now()` 自建数据
- [ ] 搜索类用例优先「先创建目标数据再搜索」，不依赖外部种子数据
- [ ] 纯 UI 验证（列头、按钮可见）无需预置数据
- [ ] 禁止依赖分页敏感或可能被删的共享数据

## 代码结构

- [ ] 使用 `test.describe` + `test.beforeEach` 分组与公共导航
- [ ] 用例内 AAA：`test.step('准备'/'操作'/'验证')`
- [ ] `test()` 是统计单位，`test.step()` 仅作子步骤
- [ ] 命名格式：`{ID}: {动作} + {预期}`
- [ ] 步骤 ≥ 5 或跨页面时已提取 Page Object（优先扩展存量 PO）
- [ ] Midscene 调用未用 `aiAct` 写整段；仅 Instant Actions；未使用 YAML

## Midscene（仅当存在 `driver: midscene` 步）

- [ ] 已安装 `@midscene/web`；已有 Midscene fixture 则复用，否则写入 `{testDir}/fixture.ts`（默认 `tests/fixture.ts`）
- [ ] spec 从 fixture 导入 `test`；`expect` 仍来自 `@playwright/test`
- [ ] `playwright.config.ts`：缺失时补 timeout ≥ 90s、Midscene reporter；仍有 video/trace
- [ ] 已检查 `MIDSCENE_MODEL_API_KEY` / `BASE_URL` / `NAME` / `FAMILY`（缺失则阻塞询问）
- [ ] 已生成 `.env.example`；`midscene_run/`、`.env` 已在 `.gitignore`；未把 API key 写入仓库
- [ ] 稳定 locator 在 PO；Midscene prompt 在 spec step（或 PO 接收 ai* 参数）

## 配置与录制

- [ ] 探索使用 `playwright-cli open {url} --headed`（有头）
- [ ] `playwright.config.ts` 含 `headless: true`（或省略，Playwright 默认无头）
- [ ] `playwright.config.ts` 含 `video: 'on'`（存量缺失才追加）
- [ ] `playwright.config.ts` 含 `trace: 'on'`（存量缺失才追加）
- [ ] 运行测试不加 `--headed`（无头下 trace/video 照常生成）
- [ ] 探索阶段未调用 Midscene Agent

## 运行与修复收尾（02 / 03 skill）

- [ ] `02-playwright-run-report`：先释放报告端口再后台 `npm run show-report`；**矩阵行数** = 矩阵对应 `test()` 通过数（setup 单独说明）
- [ ] 全部通过 → 告知通过数与报告地址，直接完成
- [ ] 有问题 → 对话询问是否修复；确认后由用户调用 `03-playwright-heal`（最多 2 轮）
- [ ] heal 按 driver 分流：Playwright 改 locator（含不可见 overlay 根→dialog）；验证码改 helper prompt/重试；其它 Midscene 改 prompt；模型/env/无视觉能力不走 locator heal

## 目录结构

**默认**（无存量 Playwright 或探测后回退）放在 `tests/` 下：

```
tests/
├── {case-name}.spec.ts
├── auth.setup.ts       # 登录测 + 业务 storageState 时
├── fixture.ts          # 仅混合 Midscene 时
├── helpers/captcha.ts  # 有图形验证码时
├── pages/{PageName}.ts
├── reports/{case-name}-report.md   # 测试计划（00 写，01/02/03 读）
└── explore/                        # snapshot / 截图 / auth.json
```

**已有 Playwright 项目**：跟现有 `testDir` / PO 目录（`pages` | `page-objects` | `pom`）/ fixture / helpers，不要另起一套平行结构。探索报告仍由 00 skill 写入 `tests/reports/`；auth/snapshot 仍在 `tests/explore/`。

## 参考

- 无存量 spec 可模仿时：本 skill 的 [test-template.ts](test-template.ts)
- 混合示例：[../examples/case-chart-hybrid.md](../examples/case-chart-hybrid.md)
- 设计规范：[test-case-design.md](test-case-design.md)
- Midscene：[midscene-hybrid.md](midscene-hybrid.md)
