#!/usr/bin/env node
/**
 * Capture WXML snapshot from WeChat mini program simulator.
 * Usage:
 *   node scripts/capture-wxml.js --projectPath ... --cliPath ... --page /pages/index/index --out miniprogram/inspect/run-xxx/首页.wxml
 *   node scripts/capture-wxml.js --wsEndpoint ws://... --out miniprogram/inspect/run-xxx/首页.wxml
 */

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    if (!key.startsWith('--')) continue;
    const name = key.slice(2);
    const next = argv[i + 1];
    if (next && !next.startsWith('--')) {
      args[name] = next;
      i += 1;
    } else {
      args[name] = true;
    }
  }
  return args;
}

function findRepoRoot(startDir) {
  let dir = startDir;
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, 'miniprogram', 'suite.json'))) {
      return dir;
    }
    dir = path.dirname(dir);
  }
  return path.join(startDir, '..');
}

function loadLocalConfig() {
  const root = findRepoRoot(path.join(__dirname, '..'));
  const candidates = [
    path.join(root, 'miniprogram.local.config'),
    path.join(root, '.cursor/skills/miniprogram-shared/miniprogram.local.config'),
    path.join(root, 'miniprogram-shared/miniprogram.local.config'),
  ];
  for (const file of candidates) {
    if (!fs.existsSync(file)) continue;
    const config = {};
    for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eq = trimmed.indexOf('=');
      if (eq === -1) continue;
      const k = trimmed.slice(0, eq).trim();
      let v = trimmed.slice(eq + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      config[k] = v;
    }
    return config;
  }
  return {};
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function timestamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return (
    `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-` +
    `${pad(d.getHours())}${pad(d.getMinutes())}`
  );
}

async function main() {
  const args = parseArgs(process.argv);
  const local = loadLocalConfig();

  const projectPath = args.projectPath || local.projectPath;
  const cliPath = args.cliPath || local.cliPath;
  const wsEndpoint = args.wsEndpoint || local.wsEndpoint;
  const pagePath = args.page || '';
  const waitMs = Number(args.wait || 500);
  let outFile = args.out;

  if (!outFile) {
    console.error('Error: --out is required (path to .wxml file)');
    process.exit(1);
  }

  if (!path.isAbsolute(outFile)) {
    outFile = path.join(__dirname, '..', outFile);
  }

  if (!wsEndpoint && !projectPath) {
    console.error('Error: projectPath or wsEndpoint is required');
    process.exit(1);
  }

  if (!wsEndpoint && !cliPath) {
    console.error('Error: cliPath is required when not using wsEndpoint');
    process.exit(1);
  }

  const automator = require('miniprogram-automator');
  let miniProgram;

  try {
    if (wsEndpoint) {
      miniProgram = await automator.connect({ wsEndpoint });
    } else {
      miniProgram = await automator.launch({ cliPath, projectPath });
    }

    let page;
    if (pagePath) {
      page = await miniProgram.reLaunch(pagePath);
    } else {
      page = await miniProgram.currentPage();
    }

    if (waitMs > 0) {
      await page.waitFor(waitMs);
    }

    const root = await page.$('page');
    if (!root) {
      throw new Error('Cannot find page root element');
    }

    const wxml = await root.wxml();
    const pageData = await page.data();
    const meta = {
      path: page.path,
      query: page.query || {},
      data: pageData,
      capturedAt: new Date().toISOString(),
    };

    ensureDir(outFile);
    fs.writeFileSync(outFile, wxml, 'utf8');

    const metaFile = outFile.replace(/\.wxml$/i, '') + '.meta.json';
    if (metaFile === outFile) {
      fs.writeFileSync(`${outFile}.meta.json`, JSON.stringify(meta, null, 2), 'utf8');
    } else {
      fs.writeFileSync(metaFile, JSON.stringify(meta, null, 2), 'utf8');
    }

    console.log(`WXML saved: ${outFile}`);
    console.log(`Meta saved: ${metaFile}`);
    console.log(`Page path: ${meta.path}`);
  } finally {
    if (miniProgram) {
      await miniProgram.close();
    }
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
