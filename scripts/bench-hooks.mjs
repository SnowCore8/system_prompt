#!/usr/bin/env node
/**
 * hook 冷启动延迟基准：以临时 HOME 运行约束注入脚本，统计 p50/p95 并执行预算。
 */
import { spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO = join(dirname(fileURLToPath(import.meta.url)), '..');
const SCRIPT = join(REPO, 'shared', 'scripts', 'inject-constraints.js');
const BUDGET_MS = 500;
const ITERATIONS = 20;
const PAYLOAD = JSON.stringify({ hook_event_name: 'SessionStart', source: 'start' });

const home = mkdtempSync(join(tmpdir(), 'hook-bench-'));
const env = { ...process.env, HOME: home, USERPROFILE: home, QODER_PLUGIN_ROOT: REPO };
for (const name of ['QODER_PLUGIN_DATA', 'QODERCN_CONFIG_DIR', 'QODER_CONFIG_DIR', 'QODER_PROJECT_DIR'])
  delete env[name];

try {
  const durations = [];
  for (let round = 0; round < ITERATIONS; round += 1) {
    const start = performance.now();
    const result = spawnSync(process.execPath, [SCRIPT], { input: PAYLOAD, env, cwd: home, encoding: 'utf8' });
    const elapsed = performance.now() - start;
    if (result.status !== 0) {
      console.error(result.stderr || `hook 退出码 ${result.status}`);
      process.exit(1);
    }
    if (!String(result.stdout).includes('hookSpecificOutput')) {
      console.error('hook 输出缺少 hookSpecificOutput');
      process.exit(1);
    }
    durations.push(elapsed);
  }
  durations.sort((a, b) => a - b);
  const pick = (ratio) => durations[Math.min(durations.length - 1, Math.floor(ratio * durations.length))];
  const p50 = pick(0.5);
  const p95 = pick(0.95);
  console.log(`hook 冷启动 ${ITERATIONS} 次：p50=${p50.toFixed(1)}ms p95=${p95.toFixed(1)}ms 预算=${BUDGET_MS}ms`);
  if (p95 > BUDGET_MS) {
    console.error(`超过预算：p95 ${p95.toFixed(1)}ms > ${BUDGET_MS}ms`);
    process.exit(1);
  }
} finally {
  rmSync(home, { recursive: true, force: true });
}
