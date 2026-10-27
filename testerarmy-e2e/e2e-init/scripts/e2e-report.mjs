#!/usr/bin/env node
/**
 * Generate Markdown + HTML reports from .e2e/report.json (same shape as e2e-report skill).
 * Usage: node scripts/e2e-report.mjs [--output .e2e]
 */
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';

const root = process.cwd();
const args = process.argv.slice(2);
const outIdx = args.indexOf('--output');
const outputDir = resolve(root, outIdx >= 0 ? args[outIdx + 1] ?? '.e2e' : '.e2e');
const reportPath = join(outputDir, 'report.json');

if (!existsSync(reportPath)) {
  console.error(`No ${relative(root, reportPath)} — run e2e first.`);
  process.exit(1);
}

const doc = JSON.parse(readFileSync(reportPath, 'utf8'));
const run = doc.run ?? doc;
const results = run.results ?? [];
const selected = results.filter((r) => r.selected !== false);
const passed = selected.filter((r) => r.status === 'passed').length;
const failed = selected.filter((r) => r.status === 'failed').length;
const skipped = selected.filter((r) => r.status === 'skipped').length;
const started = run.startedAt ? new Date(run.startedAt) : null;
const finished = run.finishedAt ? new Date(run.finishedAt) : null;
const durationMs =
  started && finished && !Number.isNaN(+started) && !Number.isNaN(+finished)
    ? finished - started
    : null;
const duration =
  durationMs == null
    ? '无'
    : durationMs >= 1000
      ? `${(durationMs / 1000).toFixed(2)}s`
      : `${durationMs}ms`;

const exitMeaning =
  run.exitCode === 0
    ? '通过'
    : run.exitCode === 1
      ? '有失败'
      : run.exitCode === 2
        ? '配置或环境错误'
        : `退出码 ${run.exitCode ?? '无'}`;

const date = (finished ?? started ?? new Date()).toISOString().slice(0, 10);
const hhmm = new Date().toTimeString().slice(0, 5).replace(':', '');

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function listFiles(dir, acc = []) {
  if (!existsSync(dir)) return acc;
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) listFiles(p, acc);
    else acc.push(p);
  }
  return acc;
}

function resultDirName(result) {
  const attempt = (result.attempts ?? []).at(-1);
  const art = attempt?.artifacts?.[0]?.path;
  if (art) return art.split('/')[0];
  const slug = (result.titlePath ?? ['test'])
    .join('-')
    .replace(/[^\w\u4e00-\u9fff-]+/g, '-')
    .slice(0, 40);
  const id = (result.id ?? '').slice(0, 16);
  return `${slug}-${id}`;
}

function collectEvidence(result) {
  const resultsRoot = join(outputDir, 'results');
  const dirs = existsSync(resultsRoot) ? readdirSync(resultsRoot) : [];
  const idShort = (result.id ?? '').slice(0, 16);
  const match =
    dirs.find((d) => d.includes(idShort)) ||
    dirs.find((d) => {
      const title = (result.titlePath ?? [])[0] ?? '';
      return title && d.includes(title.slice(0, 8));
    });

  const attempt = (result.attempts ?? []).at(-1);
  const fromArtifacts = (attempt?.artifacts ?? [])
    .map((a) => a.path)
    .filter(Boolean)
    .map((p) => join(outputDir, 'results', p));

  const base = match ? join(resultsRoot, match) : null;
  const files = base ? listFiles(base) : fromArtifacts.filter((p) => existsSync(p));
  const all = [...new Set([...fromArtifacts.filter((p) => existsSync(p)), ...files])];

  const rel = (abs) => relative(root, abs).replace(/\\/g, '/');
  const trace = all.find((f) => f.endsWith('trace.md'));
  const videos = all.filter((f) => /\.webm$/i.test(f) || /\/video\/video/i.test(f));
  const shots = all.filter((f) => /screenshots\/.+\.(png|jpe?g|webp)$/i.test(f));
  const screen = all.find((f) => f.endsWith('screen-at-failure.txt'));

  return {
    dir: match ? `results/${match}` : resultDirName(result),
    trace: trace ? rel(trace) : null,
    videos: videos.map(rel),
    shots: shots.map(rel),
    screen: screen ? rel(screen) : null,
  };
}

function failSummary(result) {
  const attempt = (result.attempts ?? []).at(-1);
  const err = attempt?.error;
  const code = err?.code ?? 'FAILED';
  let summary = (err?.message ?? '').split('\n')[0] || '无摘要';
  if (summary.length > 220) summary = `${summary.slice(0, 217)}…`;
  return { code, summary, message: err?.message ?? '' };
}

function formatMs(ms) {
  if (ms == null || Number.isNaN(ms)) return '—';
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
  return `${Math.round(ms)}ms`;
}

function statusLabel(status) {
  const map = {
    passed: '通过',
    failed: '失败',
    skipped: '跳过',
    timedOut: '超时',
    interrupted: '中断',
    flaky: '不稳定',
  };
  return map[status] ?? status ?? '—';
}

function caseMeta(result) {
  const attempt = (result.attempts ?? []).at(-1);
  const title = (result.titlePath ?? [result.file ?? 'test']).join(' › ');
  const steps = attempt?.steps ?? [];
  return {
    title,
    file: result.file ?? '—',
    kind: result.kind ?? 'test',
    status: result.status ?? '—',
    durationMs: attempt?.durationMs,
    steps,
    skipReason: result.skip?.reason,
  };
}

const failures = selected.filter((r) => r.status === 'failed');
const explore = run.explore;
const filesRun = [...new Set(selected.map((r) => r.file).filter(Boolean))];
const cmdHint = filesRun.length
  ? `e2e run ${filesRun.join(' ')}`
  : 'e2e run';

const reportsDir = join(root, 'reports');
mkdirSync(reportsDir, { recursive: true });

let basename = `e2e-report-${date}`;
if (existsSync(join(reportsDir, `${basename}.md`)) || existsSync(join(reportsDir, `${basename}.html`))) {
  basename = `e2e-report-${date}-${hhmm}`;
}

const mdPath = join(reportsDir, `${basename}.md`);
const htmlPath = join(reportsDir, `${basename}.html`);
const outRel = relative(root, outputDir).replace(/\\/g, '/') || '.e2e';

function evidenceMd(ev) {
  const lines = [];
  if (ev.trace) lines.push(`  - trace：\`${ev.trace}\``);
  for (const v of ev.videos) lines.push(`  - video：\`${v}\``);
  for (const s of ev.shots) lines.push(`  - 截图：\`${s}\``);
  if (ev.screen) lines.push(`  - screen：\`${ev.screen}\``);
  return lines.length ? lines.join('\n') : '  - （无产物文件）';
}

function hrefFromReports(relPath) {
  return `../${relPath}`;
}

function stepsMd(steps) {
  if (!steps.length) return '_无步骤记录_\n';
  const rows = steps
    .map((s, i) => {
      const label = (s.label ?? s.api ?? '').replace(/\|/g, '\\|');
      return `| ${i + 1} | ${s.status ?? '—'} | \`${s.api ?? '—'}\` | ${label} | ${formatMs(s.durationMs)} |`;
    })
    .join('\n');
  return `| # | 状态 | API | 说明 | 耗时 |
|---|------|-----|------|------|
${rows}
`;
}

const casesMdTable = selected.length
  ? `| # | 状态 | 类型 | 标题 | 文件 | 耗时 | 步骤数 |
|---|------|------|------|------|------|--------|
${selected
  .map((r, i) => {
    const m = caseMeta(r);
    return `| ${i + 1} | ${statusLabel(m.status)} | ${m.kind} | ${m.title.replace(/\|/g, '\\|')} | \`${m.file}\` | ${formatMs(m.durationMs)} | ${m.steps.length} |`;
  })
  .join('\n')}
`
  : '_无用例_\n';

const casesMdDetail = selected
  .map((r, i) => {
    const m = caseMeta(r);
    const skip = m.skipReason ? `\n- 跳过原因：${m.skipReason}` : '';
    return `### ${i + 1}. ${m.title}

- 状态：${statusLabel(m.status)} · 类型：\`${m.kind}\` · 耗时：${formatMs(m.durationMs)}
- 文件：\`${m.file}\`${skip}

${stepsMd(m.steps)}`;
  })
  .join('\n');

let failMd = '无\n';
if (failures.length) {
  failMd = failures
    .map((r) => {
      const { code, summary } = failSummary(r);
      const ev = collectEvidence(r);
      const title = (r.titlePath ?? [r.file ?? 'test']).join(' › ');
      return `### ${title}

- 错误码：\`${code}\`
- 摘要：${summary}
- 复现要点：
  1. 打开 \`${r.file ?? ''}\` 对应用例
  2. 对照 trace / 录像核对失败步骤
- 证据：
${evidenceMd(ev)}
`;
    })
    .join('\n');
}

let exploreMd = '本次非 explore 或无记录。\n';
if (explore) {
  exploreMd = `- 目标：${explore.goal ?? '无'}
- 结束原因：${explore.ended ?? '无'}
- 评估：${explore.summary ?? '无'}

| 级别 | 类型 | 标题 | 路径 | 证据 |
|------|------|------|------|------|
`;
  const findings = explore.findings ?? [];
  if (!findings.length) {
    exploreMd += '| — | — | 无 findings | — | — |\n';
  } else {
    for (const f of findings) {
      exploreMd += `| ${f.severity ?? f.level ?? '—'} | ${f.kind ?? f.type ?? '—'} | ${f.title ?? '—'} | ${f.path ?? '—'} | ${f.evidence ?? '—'} |\n`;
    }
  }
}

const risks =
  failed > 0
    ? [
        '优先用 e2e-fix 对照失败用例的 trace / 录像定位。',
        '确认断言与定位器是否稳定（hidden、combobox 等）。',
        '修完后用 e2e-run / npm run test:e2e 重跑。',
      ]
    : [
        '本轮无失败；retain-on-failure 下通常无 trace/video，属预期。',
        '稳定通过的草稿用例可去掉 draft 标记纳入回归。',
        '需要排障时保持 E2E_VIDEO / E2E_TRACE=retain-on-failure。',
      ];

const md = `# E2E 测试报告

- 日期：${date}
- 应用目录：${root}
- 产物目录：${outRel}
- 命令摘要：\`${cmdHint}\`

## 概览

| 项 | 值 |
|----|-----|
| 通过 | ${passed} |
| 失败 | ${failed} |
| 跳过 | ${skipped} |
| 耗时 | ${duration} |
| 退出含义 | ${exitMeaning} |

## 用例一览

${casesMdTable}
## 用例详情

${casesMdDetail || '_无用例_\n'}
## 失败用例

${failMd}
## 探索发现（e2e explore）

${exploreMd}
## 风险与建议

${risks.map((x, i) => `${i + 1}. ${x}`).join('\n')}
`;

function statusClass(status) {
  if (status === 'passed') return 'pass';
  if (status === 'failed' || status === 'timedOut') return 'fail';
  if (status === 'skipped') return 'skip';
  return '';
}

function failHtmlBlocks() {
  if (!failures.length) return '<p class="empty">无</p>';
  return failures
    .map((r) => {
      const { code, summary } = failSummary(r);
      const ev = collectEvidence(r);
      const title = escapeHtml((r.titlePath ?? [r.file ?? 'test']).join(' › '));
      const links = [];
      if (ev.trace) links.push(`<a href="${hrefFromReports(ev.trace)}">trace</a>`);
      for (const v of ev.videos) links.push(`<a href="${hrefFromReports(v)}">video</a>`);
      for (const s of ev.shots) links.push(`<a href="${hrefFromReports(s)}">截图</a>`);
      if (ev.screen) links.push(`<a href="${hrefFromReports(ev.screen)}">screen</a>`);
      const evidence =
        links.length > 0
          ? `证据： ${links.join(' · ')}`
          : '证据：无产物文件';
      const videoFigs = ev.videos
        .map(
          (v) => `<figure>
        <video controls preload="metadata" src="${hrefFromReports(v)}"></video>
        <figcaption>失败录像</figcaption>
      </figure>`,
        )
        .join('\n');
      const shotFigs = ev.shots
        .map(
          (s) => `<figure>
        <img src="${hrefFromReports(s)}" alt="失败截图" />
        <figcaption>失败截图</figcaption>
      </figure>`,
        )
        .join('\n');
      return `<article class="card">
      <h3>${title}</h3>
      <p><span class="badge">${escapeHtml(code)}</span></p>
      <p>${escapeHtml(summary)}</p>
      <p class="muted">复现要点</p>
      <ol>
        <li>打开 <code>${escapeHtml(r.file ?? '')}</code></li>
        <li>对照 trace / 录像核对失败步骤</li>
      </ol>
      <p class="evidence muted">${evidence}</p>
      ${videoFigs}
      ${shotFigs}
    </article>`;
    })
    .join('\n');
}

function casesOverviewHtml() {
  if (!selected.length) return '<p class="empty">无用例</p>';
  const rows = selected
    .map((r, i) => {
      const m = caseMeta(r);
      const anchor = `case-${i + 1}`;
      return `<tr class="${statusClass(m.status)}">
        <td>${i + 1}</td>
        <td><span class="pill ${statusClass(m.status)}">${escapeHtml(statusLabel(m.status))}</span></td>
        <td>${escapeHtml(m.kind)}</td>
        <td><a href="#${anchor}">${escapeHtml(m.title)}</a></td>
        <td><code>${escapeHtml(m.file)}</code></td>
        <td>${escapeHtml(formatMs(m.durationMs))}</td>
        <td>${m.steps.length}</td>
      </tr>`;
    })
    .join('\n');
  return `<table class="cases">
      <thead>
        <tr><th>#</th><th>状态</th><th>类型</th><th>标题</th><th>文件</th><th>耗时</th><th>步骤</th></tr>
      </thead>
      <tbody>
${rows}
      </tbody>
    </table>`;
}

function casesDetailHtml() {
  if (!selected.length) return '<p class="empty">无用例</p>';
  return selected
    .map((r, i) => {
      const m = caseMeta(r);
      const anchor = `case-${i + 1}`;
      const skip = m.skipReason
        ? `<p class="muted">跳过原因：${escapeHtml(m.skipReason)}</p>`
        : '';
      const stepRows = m.steps.length
        ? m.steps
            .map((s, si) => {
              const st = s.status ?? '—';
              return `<tr class="${statusClass(st)}">
              <td>${si + 1}</td>
              <td><span class="pill ${statusClass(st)}">${escapeHtml(statusLabel(st))}</span></td>
              <td><code>${escapeHtml(s.api ?? '—')}</code></td>
              <td>${escapeHtml(s.label ?? '')}</td>
              <td>${escapeHtml(formatMs(s.durationMs))}</td>
            </tr>`;
            })
            .join('\n')
        : '<tr><td colspan="5" class="empty">无步骤记录</td></tr>';
      const border =
        m.status === 'failed' || m.status === 'timedOut'
          ? 'fail'
          : m.status === 'passed'
            ? 'pass'
            : 'skip';
      return `<article class="case-card ${border}" id="${anchor}">
      <h3>${i + 1}. ${escapeHtml(m.title)}</h3>
      <p class="muted">
        <span class="pill ${statusClass(m.status)}">${escapeHtml(statusLabel(m.status))}</span>
        · ${escapeHtml(m.kind)} · ${escapeHtml(formatMs(m.durationMs))}
        · <code>${escapeHtml(m.file)}</code>
      </p>
      ${skip}
      <details open>
        <summary>步骤（${m.steps.length}）</summary>
        <table class="steps">
          <thead>
            <tr><th>#</th><th>状态</th><th>API</th><th>说明</th><th>耗时</th></tr>
          </thead>
          <tbody>
            ${stepRows}
          </tbody>
        </table>
      </details>
    </article>`;
    })
    .join('\n');
}

const exploreHtml = explore
  ? `<p>目标：${escapeHtml(explore.goal ?? '无')}</p>
    <p>结束原因：${escapeHtml(String(explore.ended ?? '无'))}</p>
    <p>评估：${escapeHtml(explore.summary ?? '无')}</p>`
  : '<p class="empty">本次非 explore 或无记录</p>';

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>E2E 测试报告 — ${escapeHtml(date)}</title>
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
    .wrap { max-width: 960px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
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
    table.cases, table.steps {
      width: 100%;
      border-collapse: collapse;
      background: var(--surface);
      font-size: 0.88rem;
      margin: 0.5rem 0 1rem;
    }
    table.cases th, table.cases td,
    table.steps th, table.steps td {
      border: 1px solid var(--border);
      padding: 0.45rem 0.55rem;
      text-align: left;
      vertical-align: top;
    }
    table.cases th, table.steps th { background: #efece4; font-weight: 600; }
    .pill {
      display: inline-block;
      font-size: 0.75rem;
      padding: 0.1rem 0.4rem;
      border: 1px solid var(--border);
      font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    }
    .pill.pass { background: var(--pass-bg); color: var(--pass); border-color: #b7dfc8; }
    .pill.fail { background: var(--fail-bg); color: var(--fail); border-color: #f0c4c0; }
    .pill.skip { background: var(--skip-bg); color: var(--skip); }
    .case-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 4px solid var(--border);
      padding: 1rem 1.15rem;
      margin: 0.75rem 0;
    }
    .case-card.pass { border-left-color: var(--pass); }
    .case-card.fail { border-left-color: var(--fail); }
    .case-card.skip { border-left-color: var(--skip); }
    .case-card h3 { margin: 0 0 0.4rem; font-size: 1.05rem; }
    .case-card details { margin-top: 0.5rem; }
    .case-card summary { cursor: pointer; color: var(--muted); font-size: 0.9rem; }
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
    .card p, .card ol, .case-card p { margin: 0.4rem 0; color: var(--text); }
    .muted { color: var(--muted); font-size: 0.9rem; }
    .evidence a, table.cases a { color: var(--accent); }
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
    .empty { color: var(--muted); font-style: italic; }
    ul.risks { padding-left: 1.2rem; }
    footer { margin-top: 2.5rem; font-size: 0.8rem; color: var(--muted); }
    code { font-size: 0.85em; }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>E2E 测试报告</h1>
      <div class="meta">
        <div>日期：${escapeHtml(date)}</div>
        <div>应用目录：${escapeHtml(root)}</div>
        <div>产物目录：${escapeHtml(outRel)}</div>
        <div>命令：${escapeHtml(cmdHint)}</div>
        <div>退出含义：${escapeHtml(exitMeaning)}</div>
      </div>
    </header>

    <section class="stats" aria-label="概览">
      <div class="stat pass"><div class="label">通过</div><div class="value">${passed}</div></div>
      <div class="stat fail"><div class="label">失败</div><div class="value">${failed}</div></div>
      <div class="stat skip"><div class="label">跳过</div><div class="value">${skipped}</div></div>
      <div class="stat"><div class="label">耗时</div><div class="value" style="font-size:1.25rem">${escapeHtml(duration)}</div></div>
    </section>

    <h2>用例一览</h2>
    ${casesOverviewHtml()}

    <h2>用例详情</h2>
    ${casesDetailHtml()}

    <h2>失败用例</h2>
    ${failHtmlBlocks()}

    <h2>探索发现</h2>
    ${exploreHtml}

    <h2>风险与建议</h2>
    <ul class="risks">
      ${risks.map((x) => `<li>${escapeHtml(x)}</li>`).join('\n      ')}
    </ul>

    <footer>由 scripts/e2e-report.mjs 根据 report.json 生成 · 请用浏览器打开本文件</footer>
  </div>
</body>
</html>
`;

writeFileSync(mdPath, md, 'utf8');
writeFileSync(htmlPath, html, 'utf8');
console.log(`Wrote ${relative(root, htmlPath)}`);
console.log(`Wrote ${relative(root, mdPath)}`);
