const fs = require('fs');
const path = require('path');

function findRepoRoot(startDir) {
  let dir = startDir;
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, 'miniprogram', 'suite.json'))) {
      return dir;
    }
    dir = path.dirname(dir);
  }
  return startDir;
}

function loadLocalConfig() {
  const root = findRepoRoot(__dirname);
  const candidates = [
    path.join(root, 'miniprogram.local.config'),
    path.join(root, '.cursor/skills/miniprogram-shared/miniprogram.local.config'),
    path.join(root, 'miniprogram-shared/miniprogram.local.config'),
  ];

  for (const file of candidates) {
    if (!fs.existsSync(file)) continue;
    const content = fs.readFileSync(file, 'utf8');
    const config = {};
    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eq = trimmed.indexOf('=');
      if (eq === -1) continue;
      const key = trimmed.slice(0, eq).trim();
      let value = trimmed.slice(eq + 1).trim();
      if (
        (value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))
      ) {
        value = value.slice(1, -1);
      }
      config[key] = value;
    }
    return config;
  }
  return {};
}

const localConfig = loadLocalConfig();

global.__MINIPROGRAM_CONFIG__ = {
  cliPath: process.env.MINIPROGRAM_CLI_PATH || localConfig.cliPath || '',
  projectPath: process.env.MINIPROGRAM_PROJECT_PATH || localConfig.projectPath || '',
  wsEndpoint: process.env.MINIPROGRAM_WS_ENDPOINT || localConfig.wsEndpoint || '',
};

beforeAll(async () => {
  const { projectPath, wsEndpoint } = global.__MINIPROGRAM_CONFIG__;
  if (!projectPath && !wsEndpoint) {
    throw new Error(
      'Missing projectPath or wsEndpoint. Run scaffold.sh and edit miniprogram.local.config.'
    );
  }
});
