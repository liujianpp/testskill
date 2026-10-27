#!/usr/bin/env node
/**
 * Thin wrapper: load .env, then forward to `e2e`.
 * When E2E_HEADED is 1/true/yes, append --headed unless already present.
 * After `run` / `explore`, generate reports/e2e-report-*.md|.html via e2e-report.mjs.
 *
 * Canonical template: <skills-root>/scripts/e2e.mjs (e2e-init skill).
 * Copied into the app as scripts/e2e.mjs for npm run test:e2e / explore.
 */
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

if (existsSync('.env')) {
  process.loadEnvFile('.env');
}

const headed = /^(1|true|yes)$/i.test(String(process.env.E2E_HEADED ?? '').trim());
const args = process.argv.slice(2);
if (headed && !args.includes('--headed')) {
  args.push('--headed');
}

const result = spawnSync('npx', ['e2e', ...args], {
  stdio: 'inherit',
  shell: process.platform === 'win32',
  env: process.env,
});

const cmd = args[0];
if (cmd === 'run' || cmd === 'explore') {
  const here = dirname(fileURLToPath(import.meta.url));
  const reportScript = join(here, 'e2e-report.mjs');
  if (existsSync(reportScript) && existsSync('.e2e/report.json')) {
    const outIdx = args.indexOf('--output');
    const reportArgs = outIdx >= 0 && args[outIdx + 1] ? ['--output', args[outIdx + 1]] : [];
    spawnSync(process.execPath, [reportScript, ...reportArgs], {
      stdio: 'inherit',
      env: process.env,
    });
  }
}

process.exit(result.status ?? 1);
