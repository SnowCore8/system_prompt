import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const HOOK = join(__dirname, '..', '..', 'shared', 'scripts', 'inject-compact.js');
const HOOKS_QODER = join(__dirname, '..', '..', 'plugins', 'qoder', 'hooks', 'hooks.json');

function runHook(payload, env = {}) {
  return new Promise((resolve) => {
    const child = spawn('node', [HOOK], {
      env: { ...process.env, ...env },
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => { stdout += d.toString(); });
    child.stderr.on('data', (d) => { stderr += d.toString(); });
    child.on('close', (code) => {
      resolve({ code, stdout: stdout.trim(), stderr });
    });
    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
  });
}

describe('inject-compact.js', () => {
  it('SessionStart source=compact 输出约束提醒与时间', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'SessionStart',
      source: 'compact',
    });
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    const ctx = output.hookSpecificOutput.additionalContext;
    assert.match(ctx, /Never violate global user constraints/);
    assert.match(ctx, /Time sampled after context compaction:/);
    assert.match(ctx, /Browser time zone for this request:/);
  });

  it('SessionStart source!=compact 静默退出', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'SessionStart',
      source: 'startup',
    });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('非 SessionStart 事件静默退出', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'UserPromptSubmit',
      source: 'compact',
    });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('非法 payload 静默退出 0', async () => {
    const { code } = await runHook('not-json');
    assert.equal(code, 0);
  });
});

describe('Qoder hooks.json compact 配置', () => {
  it('包含 compact matcher', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    const sessionStart = hooks.hooks.SessionStart;
    const compactGroup = sessionStart.find(g => g.matcher === 'compact');
    assert.ok(compactGroup, '应存在 compact matcher 组');
    assert.equal(compactGroup.hooks[0].command, 'node');
    assert.match(compactGroup.hooks[0].args[0], /inject-compact\.js/);
  });
});
