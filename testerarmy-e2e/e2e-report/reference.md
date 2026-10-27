# e2e 报告模板

配合 `<skills-root>/SKILL.md`。从 `<output>/report.json` 填空；缺字段写「无」或省略该行，不编造。默认同时写出 `.md` 与 `.html`（同名 basename）。

## Markdown 模板

```markdown
# E2E 测试报告

- 日期：<YYYY-MM-DD>
- 应用目录：<path>
- 产物目录：<output，默认 .e2e>
- 命令摘要：<e2e run … / e2e explore …，若可知>

## 概览

| 项 | 值 |
|----|-----|
| 通过 | <n> |
| 失败 | <n> |
| 跳过 | <n> |
| 耗时 | <duration> |
| 退出含义 | <通过 / 有失败 / 配置或环境错误> |

## 用例一览

（列出本次 selected 的每一条：setup / test / 跳过均要。无则写「无」。）

| # | 状态 | 类型 | 标题 | 文件 | 耗时 | 步骤数 |
|---|------|------|------|------|------|--------|
| 1 | 通过/失败/跳过 | setup/test | <titlePath> | `<file>` | <duration> | <n> |

## 用例详情

（每条用例一块；步骤来自 attempt.steps。）

### 1. <titlePath>

- 状态：… · 类型：… · 耗时：…
- 文件：`<file>`

| # | 状态 | API | 说明 | 耗时 |
|---|------|-----|------|------|
| 1 | passed | `app.open` | `/projects` | 0.8s |

## 失败用例

（无失败则写「无」。每条失败一块；与上方详情互补，侧重错误码与证据。）

### <describe › test 标题>

- 错误码：`<code>`
- 摘要：<一两句>
- 复现要点：
  1. …
- 证据：（只列实际存在的文件；相对应用目录）
  - trace：`<output>/results/.../trace.md`
  - video：`<output>/results/.../attempt-1/video/video.webm`（若有）
  - 截图：`<output>/results/.../attempt-1/screenshots/….png`（若有）
  - screen：`<output>/results/.../attempt-1/screen-at-failure.txt`（若有）

## 探索发现（e2e explore）

（无 `run.explore` 则整节写「本次非 explore 或无记录」。）

- 目标：<goal>
- 结束原因：<ended>
- 评估：<summary>

| 级别 | 类型 | 标题 | 路径 | 证据 |
|------|------|------|------|------|
| <severity 或 critical/high/…> | issue/warning | <title> | <path> | <artifact 路径> |

对每条 issue 可附：

- 期望：<expected>
- 实际：<actual>
- 复现：<reproduction 列表>

说明：explore finding 未经独立 repro 测试验证前，标为「待确认」。

## 风险与建议

1. <最优先修复或核对项>
2. <草稿定位器核对 / 补断言 / 补账号 等>
3. <可选：转入回归套件或去掉 draft 标记的条件>
```

## HTML 骨架（自包含）

写入 `reports/e2e-report-<日期>.html`。占位符与 Markdown 同源数据。证据用相对路径（如 `../.e2e/results/<…>/….png` / `….webm`）；无对应文件则去掉该项与 `<figure>` / `<video>`。

失败证据在 HTML 中须**可点击**：`trace.md`、`video.webm`、截图、`screen-at-failure.txt` 用 `<a href>`；有录像时额外内嵌 `<video controls>`（勿 base64）。这不是 Playwright Trace Viewer——点 trace 打开逐步文字，video 页内播放画面。

视觉约定：浅色底、系统字体、CSS 变量着色；通过绿 / 失败红 / 跳过灰；**避免**紫渐变、过量阴影与圆角药丸风。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>E2E 测试报告 — <YYYY-MM-DD></title>
  <style>
    :root {
      --bg: #f6f5f1;
      --surface: #ffffff;
      --text: #1a1a1a;
      --muted: #5c5c5c;
      --border: #e2e0d8;
      --pass: #1b7f4e;
      --pass-bg: #e8f5ee;
      --fail: #b42318;
      --fail-bg: #fcebea;
      --skip: #6b6b6b;
      --skip-bg: #efefef;
      --accent: #0f3d3e;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", "PingFang SC", "Hiragino Sans GB",
        "Noto Sans SC", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }
    .wrap { max-width: 920px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
    header { margin-bottom: 1.75rem; }
    header h1 { margin: 0 0 0.35rem; font-size: 1.75rem; letter-spacing: -0.02em; }
    header .meta { color: var(--muted); font-size: 0.95rem; }
    header .meta div { margin: 0.15rem 0; }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.75rem;
      margin: 1.25rem 0 1.75rem;
    }
    @media (max-width: 640px) {
      .stats { grid-template-columns: repeat(2, 1fr); }
    }
    .stat {
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 1rem 1.1rem;
    }
    .stat .label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .stat .value { font-size: 1.75rem; font-weight: 600; margin-top: 0.25rem; }
    .stat.pass .value { color: var(--pass); }
    .stat.fail .value { color: var(--fail); }
    .stat.skip .value { color: var(--skip); }
    h2 {
      margin: 2rem 0 0.75rem;
      font-size: 1.15rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.4rem;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 4px solid var(--fail);
      padding: 1rem 1.15rem;
      margin: 0.75rem 0;
    }
    .card h3 { margin: 0 0 0.5rem; font-size: 1.05rem; }
    .badge {
      display: inline-block;
      font-size: 0.75rem;
      font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
      padding: 0.15rem 0.45rem;
      background: var(--fail-bg);
      color: var(--fail);
      border: 1px solid #f0c4c0;
    }
    .card p, .card ol { margin: 0.4rem 0; color: var(--text); }
    .card .muted { color: var(--muted); font-size: 0.9rem; }
    .evidence a { color: var(--accent); }
    figure { margin: 0.75rem 0 0; }
    figure img, figure video {
      max-width: 100%;
      height: auto;
      border: 1px solid var(--border);
      background: #111;
      display: block;
    }
    figure video { width: 100%; }
    figure figcaption { font-size: 0.8rem; color: var(--muted); margin-top: 0.35rem; }
    table {
      width: 100%;
      border-collapse: collapse;
      background: var(--surface);
      font-size: 0.9rem;
    }
    th, td {
      border: 1px solid var(--border);
      padding: 0.5rem 0.65rem;
      text-align: left;
      vertical-align: top;
    }
    th { background: #efece4; font-weight: 600; }
    .ok { color: var(--pass); }
    .empty { color: var(--muted); font-style: italic; }
    ul.risks { padding-left: 1.2rem; }
    footer { margin-top: 2.5rem; font-size: 0.8rem; color: var(--muted); }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>E2E 测试报告</h1>
      <div class="meta">
        <div>日期：<YYYY-MM-DD></div>
        <div>应用目录：<path></div>
        <div>产物目录：<output></div>
        <div>命令：<e2e run … / e2e explore …></div>
        <div>退出含义：<通过 / 有失败 / …></div>
      </div>
    </header>

    <section class="stats" aria-label="概览">
      <div class="stat pass"><div class="label">通过</div><div class="value"><n></div></div>
      <div class="stat fail"><div class="label">失败</div><div class="value"><n></div></div>
      <div class="stat skip"><div class="label">跳过</div><div class="value"><n></div></div>
      <div class="stat"><div class="label">耗时</div><div class="value" style="font-size:1.25rem"><duration></div></div>
    </section>

    <h2>用例一览</h2>
    <!-- 表格：# / 状态 / 类型 / 标题(链到详情锚点) / 文件 / 耗时 / 步骤数 -->
    <table class="cases">…</table>

    <h2>用例详情</h2>
    <!-- 每条 article.case-card：状态、文件、details 内步骤表（API / 说明 / 状态 / 耗时） -->
    <article class="case-card pass" id="case-1">…</article>

    <h2>失败用例</h2>
    <!-- 无失败时： -->
    <p class="empty">无</p>
    <!-- 有失败时，每条一块： -->
    <article class="card">
      <h3><describe › test 标题></h3>
      <p><span class="badge"><code></span></p>
      <p><一两句摘要></p>
      <p class="muted">复现要点</p>
      <ol>
        <li>…</li>
      </ol>
      <p class="evidence muted">
        证据：
        <a href="../.e2e/results/.../trace.md">trace</a>
        · <a href="../.e2e/results/.../attempt-1/video/video.webm">video</a>
        · <a href="../.e2e/results/.../attempt-1/screenshots/….png">截图</a>
        · <a href="../.e2e/results/.../attempt-1/screen-at-failure.txt">screen</a>
        <!-- 仅保留实际存在的链接 -->
      </p>
      <figure>
        <video controls preload="metadata" src="../.e2e/results/.../attempt-1/video/video.webm"></video>
        <figcaption>失败录像（若有）</figcaption>
      </figure>
      <figure>
        <img src="../.e2e/results/.../….png" alt="失败截图" />
        <figcaption>失败截图（若有）</figcaption>
      </figure>
    </article>

    <h2>探索发现</h2>
    <!-- 无 explore： -->
    <p class="empty">本次非 explore 或无记录</p>
    <!-- 有 explore：写 goal / ended / summary，再跟表 -->
    <table>
      <thead>
        <tr><th>级别</th><th>类型</th><th>标题</th><th>路径</th><th>证据</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>…</td><td>issue/warning</td><td>…</td><td>…</td>
          <td><a href="../.e2e/...">…</a></td>
        </tr>
      </tbody>
    </table>

    <h2>风险与建议</h2>
    <ul class="risks">
      <li>…</li>
    </ul>

    <footer>由 e2e-report 根据 report.json 生成 · 请用浏览器打开本文件</footer>
  </div>
</body>
</html>
```

## 填表提示

- 普通 `e2e run`：以 `report.json` 中测试结果列表统计通过/失败/跳过；**必须**写出「用例一览」+「用例详情」（含每条 `attempt.steps` 的 api/label/status/durationMs）。失败块来自 failed 结果 + 对应 `trace.md` 首段失败信息。
- 命令生成：优先 `npm run report:e2e` / `scripts/e2e-report.mjs`（与本模板同形）；skill 手写时对齐同一结构。
- 证据路径：优先 `attempt.artifacts[].path`；再扫 `results/<test>/` 下的 `trace.md`、`attempt-*/video/*.webm`、`attempt-*/screenshots/*`、`attempt-*/screen-at-failure.txt`。没有就省略，不写「无」占位链接。
- `e2e explore`：概览可用 steps/findings 计数；「失败用例」可写「见探索发现」或把阻塞步骤列在失败节。
- severity：critical 5、high 4、medium 3、low 2、trivial 1（与 explore guide 一致）。
- 不要把密码、完整环境变量或未脱敏截图说明写进报告正文。
- HTML 与 MD 内容对齐；HTML 内对用户可见文本做必要 HTML 转义（`<`、`>`、`&`）。
