const fs = require('fs');
const path = require('path');
const { tryScreenshot } = require('./screenshot');

const WXML_MAX = 50 * 1024;

function isTraceEnabled() {
  return String(process.env.RECORD_TRACE || '').toLowerCase() === 'true';
}

function slugName(name) {
  return String(name || 'step')
    .replace(/[^\w\u4e00-\u9fff-]+/g, '_')
    .replace(/_+/g, '_')
    .slice(0, 48);
}

async function getRoot(page) {
  for (const sel of ['.login-page', '.home-page', '.list-page', '.profile-page', '.container', 'view']) {
    try {
      const el = await page.$(sel);
      if (el) return el;
    } catch (_) {
      /* continue */
    }
  }
  return null;
}

async function capturePageSnapshot(miniProgram) {
  const page = await miniProgram.currentPage();
  const pagePath = (page && page.path) || '';
  let data = {};
  let wxml = '';
  try {
    data = (await page.data()) || {};
  } catch (_) {
    data = {};
  }
  try {
    const root = await getRoot(page);
    if (root) {
      wxml = (await root.wxml()) || '';
      if (wxml.length > WXML_MAX) {
        wxml = `${wxml.slice(0, WXML_MAX)}\n<!-- truncated -->\n`;
      }
    }
  } catch (_) {
    wxml = '';
  }
  return { page, path: pagePath, data, wxml };
}

function buildViewerHtml(traceData) {
  const steps = traceData.steps || [];
  const rows = steps
    .map((s) => {
      const cls = s.ok ? 'ok' : 'fail';
      const png = s.files && s.files.png ? s.files.png : '';
      const wxml = s.files && s.files.wxml ? s.files.wxml : '';
      const meta = s.files && s.files.meta ? s.files.meta : '';
      const img = png
        ? `<img src="${png}" alt="step ${s.index}" style="max-width:280px;border:1px solid #ddd"/>`
        : '<span class="muted">无截图</span>';
      return `<tr class="${cls}">
  <td>${s.index}</td>
  <td><code>${escapeHtml(s.name)}</code></td>
  <td>${escapeHtml(s.path || '')}</td>
  <td>${s.ok ? 'OK' : 'FAIL'}</td>
  <td>${escapeHtml(s.at || '')}</td>
  <td>${img}<div class="links">
    ${meta ? `<a href="${meta}">meta</a>` : ''}
    ${wxml ? `<a href="${wxml}">wxml</a>` : ''}
  </div></td>
</tr>`;
    })
    .join('\n');

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>Trace ${escapeHtml(traceData.caseKey || '')}</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;margin:24px;background:#f6f8fa;color:#24292f}
h1{font-size:1.25rem}table{border-collapse:collapse;width:100%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08)}
th,td{border-bottom:1px solid #eaecef;padding:10px 12px;text-align:left;font-size:13px;vertical-align:top}
th{background:#f0f3f6}.ok td:nth-child(4){color:#1a7f37;font-weight:600}.fail td:nth-child(4){color:#cf222e;font-weight:600}
.muted{color:#6e7781}.links a{margin-right:8px;color:#0969da;text-decoration:none}
.meta{color:#57606a;margin:8px 0 16px}
</style>
</head>
<body>
<h1>伪 Trace · ${escapeHtml(traceData.caseKey || '')}</h1>
<p class="meta">startedAt=${escapeHtml(traceData.startedAt || '')} · steps=${steps.length}</p>
<table>
<thead><tr><th>#</th><th>步骤</th><th>path</th><th>结果</th><th>时间</th><th>证据</th></tr></thead>
<tbody>
${rows}
</tbody>
</table>
</body>
</html>`;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * @param {object} miniProgram
 * @param {{ caseKey?: string }} [opts]
 */
function createTrace(miniProgram, opts = {}) {
  const enabled = isTraceEnabled();
  const caseKey = opts.caseKey || process.env.CASE_KEY || 'CASE';
  const artifactDir = process.env.ARTIFACT_DIR || '';
  const traceDir = artifactDir ? path.join(artifactDir, 'trace') : '';
  const state = {
    caseKey,
    startedAt: new Date().toISOString(),
    steps: [],
  };
  let index = 0;

  const noop = {
    enabled: false,
    async step(_name, fn) {
      return fn();
    },
    async flush() {
      return null;
    },
  };

  if (!enabled || !traceDir || !miniProgram) {
    return noop;
  }

  fs.mkdirSync(traceDir, { recursive: true });

  /** ensureLoggedIn / forceLogin / 登录页：不截图（减少重复），仍落 meta/wxml */
  function shouldSkipScreenshot(stepName, pagePath) {
    const n = String(stepName || '')
      .toLowerCase()
      .replace(/[-_\s]/g, '');
    if (n.includes('ensureloggedin') || n.includes('forcelogin')) return true;
    if (n === 'login' || n.startsWith('login')) return true;
    const p = String(pagePath || '').toLowerCase();
    if (p.includes('login')) return true;
    return false;
  }

  async function writeStepFiles(prefix, snap, stepName) {
    const metaName = `${prefix}.meta.json`;
    const wxmlName = `${prefix}.wxml`;
    const pngName = `${prefix}.png`;
    const metaPath = path.join(traceDir, metaName);
    const wxmlPath = path.join(traceDir, wxmlName);
    const pngPath = path.join(traceDir, pngName);

    fs.writeFileSync(
      metaPath,
      JSON.stringify(
        {
          path: snap.path,
          data: snap.data,
          capturedAt: new Date().toISOString(),
        },
        null,
        2
      ),
      'utf8'
    );
    if (snap.wxml) {
      fs.writeFileSync(wxmlPath, snap.wxml, 'utf8');
    }

    let pngOk = null;
    if (!shouldSkipScreenshot(stepName, snap.path)) {
      pngOk = await tryScreenshot(miniProgram, pngPath);
    }

    return {
      meta: metaName,
      wxml: snap.wxml ? wxmlName : null,
      png: pngOk ? pngName : null,
    };
  }

  return {
    enabled: true,
    async step(name, fn) {
      index += 1;
      const prefix = `${String(index).padStart(3, '0')}_${slugName(name)}`;
      let ok = true;
      let error = null;
      let result;
      try {
        result = await fn();
      } catch (e) {
        ok = false;
        error = e && (e.message || String(e));
        // 失败也采快照
        try {
          const snap = await capturePageSnapshot(miniProgram);
          const files = await writeStepFiles(prefix, snap, name);
          state.steps.push({
            index,
            name,
            at: new Date().toISOString(),
            path: snap.path,
            ok: false,
            error,
            files,
          });
          persistTraceJson();
        } catch (_) {
          state.steps.push({
            index,
            name,
            at: new Date().toISOString(),
            path: '',
            ok: false,
            error,
            files: {},
          });
          persistTraceJson();
        }
        throw e;
      }

      try {
        const snap = await capturePageSnapshot(miniProgram);
        const files = await writeStepFiles(prefix, snap, name);
        state.steps.push({
          index,
          name,
          at: new Date().toISOString(),
          path: snap.path,
          ok,
          error: null,
          files,
        });
        persistTraceJson();
      } catch (_) {
        state.steps.push({
          index,
          name,
          at: new Date().toISOString(),
          path: '',
          ok,
          error: null,
          files: {},
        });
        persistTraceJson();
      }
      return result;
    },
    async flush() {
      persistTraceJson();
      const viewerPath = path.join(traceDir, 'viewer.html');
      fs.writeFileSync(viewerPath, buildViewerHtml(state), 'utf8');
      return viewerPath;
    },
  };

  function persistTraceJson() {
    fs.writeFileSync(path.join(traceDir, 'trace.json'), JSON.stringify(state, null, 2), 'utf8');
  }
}

module.exports = { createTrace, isTraceEnabled };
