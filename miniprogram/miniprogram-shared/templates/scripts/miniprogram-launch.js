const fs = require('fs');
const path = require('path');

/**
 * 定位自动化仓库根（含 miniprogram/suite.json），兼容 skill 安装深度。
 */
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

async function launchMiniProgram(overrides = {}) {
  const automator = require('miniprogram-automator');
  const local = loadLocalConfig();
  const cliPath = overrides.cliPath || process.env.MINIPROGRAM_CLI_PATH || local.cliPath;
  const projectPath =
    overrides.projectPath || process.env.MINIPROGRAM_PROJECT_PATH || local.projectPath;
  const wsEndpoint =
    overrides.wsEndpoint || process.env.MINIPROGRAM_WS_ENDPOINT || local.wsEndpoint;

  if (wsEndpoint) {
    const mp = await automator.connect({ wsEndpoint });
    // connect 模式下 close() 会拆掉 auto 端口；改为 disconnect 以便 suite 续连
    const disconnect = typeof mp.disconnect === 'function' ? mp.disconnect.bind(mp) : null;
    if (disconnect) {
      mp.close = async () => {
        try {
          await Promise.race([disconnect(), new Promise((r) => setTimeout(r, 3000))]);
        } catch (_) {
          /* ignore */
        }
      };
    }
    return mp;
  }
  if (!projectPath || !cliPath) {
    throw new Error(
      'Missing projectPath or cliPath. Copy miniprogram.local.config.example to miniprogram.local.config'
    );
  }
  return automator.launch({ cliPath, projectPath });
}

module.exports = { loadLocalConfig, launchMiniProgram, findRepoRoot };
