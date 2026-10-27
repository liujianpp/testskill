# 小程序自动化仓库约定（script-author + run + shared 共用）

`miniprogram-script-author`、`miniprogram-run` 均须遵守本文件。路径均相对于 **小程序自动化项目仓库根**（含 `miniprogram/`、`reports/` 的目录）。

## Skill 包布局

三件套目录同级，父路径记为 **`<skills-root>`**（安装位置由项目自定，文档不写死具体父目录）：

| 目录 | 说明 |
|------|------|
| `miniprogram-script-author/` | 探索与编写 Jest spec |
| `miniprogram-run/` | 执行脚本 `run-with-reports.sh`、`miniprogram-run.config`（含 Session 报告） |
| `miniprogram-shared/` | 本文件、`selectors.md`、`templates/`、`scaffold.sh`、`miniprogram.local.config.example` |

**交付给用户时只发上述三目录**；勿附带 `miniprogram.local.config`（本机路径）、业务 `tests/*.spec.js`、`inspect/`、`reports/`。

首次在用户自动化仓库使用前，执行脚手架：

```bash
bash <skills-root>/miniprogram-shared/scaffold.sh .
```

将拷贝：`scripts/`、`miniprogram/tests/helpers/`、`jest.config.js`、`jest.setup.js`、空 `suite.json` 等。详见 [README.md](README.md)、[templates/package.deps.md](templates/package.deps.md)。

在 **小程序自动化项目仓库根** 执行（示例）：

```bash
<skills-root>/miniprogram-run/run-with-reports.sh suite
```

配置：仓库根或 `<skills-root>/miniprogram-shared/` 下的 `miniprogram.local.config`（从 example 复制，**勿提交 Git**）。

`run-with-reports.sh` 从脚本所在目录向上查找 `miniprogram/suite.json` 以定位仓库根，与 `<skills-root>` 嵌套深度无关。

## RunId 与目录

同一次**探索批次**共用 **`RunId`**（推荐 `yyyyMMdd-HHmmss`，或用户指定 slug），仅用于 inspect / probes：

| 目录 | 内容 |
|------|------|
| `miniprogram/tests/<模块>/` | 正式用例（按业务模块，**不用** `run-*`） |
| `miniprogram/tests/helpers/` | 共用 helper（如 `auth.js`） |
| `miniprogram/inspect/run-<RunId>/` | WXML 快照与 `.meta.json` |
| `miniprogram/probes/run-<RunId>/` | 导航探针（仅到达目标页，不含业务断言） |

**模块目录**（租客端示例，可按项目增删）：`auth`（登录/退出）、`home`（首页/房间）、`maintenance`（工单）、`profile`（我的）。可复用其它 `inspect/run-*` 历史快照。

`suite.json` 内 `cases[].file` 相对于 **`miniprogram/`**，例如 `tests/auth/auth.spec.js`（同模块多条用例共用同一文件）。

## projectPath 与 cliPath

- **`projectPath`**（小程序工程路径）必填；由用户提供或授权从项目配置引用。
- **`cliPath`**（微信开发者工具 CLI 路径）必填，除非使用 `wsEndpoint` 连接已打开的开发者工具。
- **禁止臆造** 路径；**禁止**在交付文件中使用占位符冒充真实配置。

macOS 常见 CLI 路径示例（须用户确认）：

```
/Applications/wechatwebdevtools.app/Contents/MacOS/cli
```

配置写入 `<skills-root>/miniprogram-shared/miniprogram.local.config`（从 `miniprogram.local.config.example` 复制）。

## Spec 文件命名

- **正式用例**：**一模块一文件** `miniprogram/tests/<模块>/<模块>.spec.js`
  - 示例：`tests/auth/auth.spec.js`、`tests/maintenance/maintenance.spec.js`
  - 同模块多条用例写在同一文件内，每条一个顶层 `describe('<用例ID> <标题>', …)`（`describe` 名须以用例 ID 开头）
  - 新增用例：模块文件已存在则追加 `describe`；禁止再新建 `01_TC-*.spec.js`
- **共用片段**：`helpers/auth.js` 等，无虚构用例 ID，不占业务顺序号。
- 模块文件首行注释：`// <模块> 模块｜…`；各 describe 内可注明前置。

## 登录会话复用

suite 经 `wsEndpoint` 连接同一模拟器时，storage 可跨 Jest 进程保留：

- **业务用例**（已登录前置）：用 `ensureLoggedIn()` —— 已有 `accessToken` 则跳过登录。
- **必须干净未登录**（测登录本身、或需强制重登）：用 `forceLogin()`（先 `clearStorageSync`）。
- **退出登录类**：`ensureLoggedIn` 后执行退出；勿在 helper 里无条件清 storage。

## 套件顺序

执行顺序**不依赖**文件夹遍历，唯一编排源：

- **`miniprogram/suite.json`** — `cases[]` 按 `order` 排序；批量执行：`@miniprogram-run suite`（**逐条**按 `id` 用 `--testNamePattern` 跑模块文件中对应 describe；默认失败后继续、同一 Session；`STOP_ON_FAIL=true` 时遇失败即停，可 `suite --from` 续跑）

须与 Excel「执行顺序」列对齐。调整顺序只改 `cases[].order`，**无需**重命名 spec 文件。同模块多条的 `file` 均指向同一 `<模块>.spec.js`。

## Inspect 落盘

- 目录：`miniprogram/inspect/run-<RunId>/`
- WXML 文件：`<页面语义>_<YYYYMMDD-HHmm>.wxml`（UTF-8）
- 元数据：同名 `.meta.json`，含 `{ path, query, data, capturedAt }`
- 采集工具：`node scripts/capture-wxml.js` 或 Skill 1 内联 automator 调用

## 报告产物

由 `@miniprogram-run`（`run-with-reports.sh`）在执行时生成：

```
reports/
  miniprogram-executions.md              # 跨 Session 累积台账（脚本追加）
  miniprogram-report-<sessionId>.md      # 批量 Markdown 报告
  miniprogram-report-<sessionId>.html    # 批量 HTML 报告（含 Trace 链接）
  artifacts/<sessionId>/<caseKey>/       # single 或 suite 逐条
    jest-results.json
    console.log
    screenshot.png                       # 可选：RECORD_SCREENSHOT=true
    trace/                               # 伪 Trace（RECORD_TRACE=true）
      trace.json
      viewer.html
      NNN_<step>.meta.json / .wxml / .png
```

`reports/artifacts/` 通常在 `.gitignore` 中。

**限制**：miniprogram-automator **不支持** Playwright video / `trace.zip`；用伪 Trace（步骤 meta + WXML + 尽力截图）+ HTML viewer 代替。

**截图**：须调用 `miniProgram.screenshot({ path })`（**不是** `page.screenshot`；Page 无此 API）。仅开发者工具**模拟器**可用；实现见 `helpers/screenshot.js`。

**Trace 跳过截图**：步骤名为 `ensureLoggedIn` / `forceLogin` / `login*`，或当前页 path 含 `login` 时**不截 png**（仍落 meta/wxml），避免登录前后重复图。

## 两步工作流

1. `@miniprogram-script-author` — 探索 + 写 Jest spec + 维护 suite（不跑正式用例回归）
2. `@miniprogram-run` — 执行 spec，写入 executions / artifacts / Session 批量报告

## 选择器铁律

详见 [selectors.md](selectors.md)。摘要：

1. 每个关键页须有 WXML inspect 依据，**禁止**仅凭 Excel/口头步骤写 `page.$()`。
2. 优先 `id` / `data-*` / 经 inspect 核对的 class；动态列表用 `$$()` + 文本过滤。
3. 自定义组件内元素须用 `element.$()`，不能用 `page.$()` 跨组件选择。
