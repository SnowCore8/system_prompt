import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdtempSync, rmSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { createHash } from 'node:crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const HOOK = join(__dirname, '..', '..', 'shared', 'scripts', 'inject-constraints.js');
const RULES_FILE = join(__dirname, '..', '..', 'rules', 'global-user-constraints.md');
const HOOKS_QODER = join(__dirname, '..', '..', 'plugins', 'qoder', 'hooks', 'hooks.json');
const HOOKS_QWEN = join(__dirname, '..', '..', 'plugins', 'qwen', 'hooks', 'qwen-hooks.json');

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

describe('inject-constraints.js', () => {
  it('UserPromptSubmit 输出固定提醒', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'UserPromptSubmit',
    });
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    assert.equal(output.hookSpecificOutput.additionalContext, 'Never violate global user constraints.');
  });

  it('SessionStart 注入约束全文', async () => {
    const pluginRoot = join(__dirname, '..', '..');
    const { code, stdout } = await runHook({
      hook_event_name: 'SessionStart',
      cwd: pluginRoot,
    }, { QODER_PLUGIN_ROOT: pluginRoot });
    assert.equal(code, 0);
    if (stdout) {
      const output = JSON.parse(stdout);
      const ctx = output.hookSpecificOutput.additionalContext;
      assert.match(ctx, /全局用户约束/);
    }
  });

  it('SessionStart source=resume 跳过注入', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'SessionStart',
      source: 'resume',
      cwd: process.cwd(),
    });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('非法 payload 静默退出 0', async () => {
    const { code } = await runHook('not-json');
    assert.equal(code, 0);
  });

  it('不支持的事件静默退出 0', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'UnknownEvent',
    });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });
});

describe('hooks.json 约束注入配置', () => {
  it('Qoder hooks.json 引用 inject-constraints.js', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    const json = JSON.stringify(hooks);
    assert.match(json, /inject-constraints\.js/);
    assert.doesNotMatch(json, /inject_constraints\.py/);
  });

  it('Qwen hooks.json 引用 inject-constraints.js', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QWEN, 'utf-8'));
    const json = JSON.stringify(hooks);
    assert.match(json, /inject-constraints\.js/);
    assert.doesNotMatch(json, /inject_constraints\.py/);
  });
});
