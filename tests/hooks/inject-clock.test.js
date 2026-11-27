import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdtempSync, rmSync, mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const HOOK = join(__dirname, '..', '..', 'shared', 'scripts', 'inject-clock.js');
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

describe('inject-clock.js', () => {
  it('UserPromptSubmit 输出完整三行时间块', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'UserPromptSubmit',
      session_id: 'test-session',
    });
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    const ctx = output.hookSpecificOutput.additionalContext;
    assert.match(ctx, /Time sampled while preparing turn 1:/);
    assert.match(ctx, /Browser time zone for this request:/);
    assert.match(ctx, /Elapsed since the preceding model-visible message:/);
  });

  it('PreToolUse 输出一行时间', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'PreToolUse',
      tool_name: 'read',
      session_id: 'test-session',
    });
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    const ctx = output.hookSpecificOutput.additionalContext;
    assert.match(ctx, /Time sampled at PreToolUse \(read\):/);
    assert.doesNotMatch(ctx, /Browser time zone/);
  });

  it('PostToolUse 输出一行时间', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'PostToolUse',
      tool_name: 'bash',
      session_id: 'test-session',
    });
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    const ctx = output.hookSpecificOutput.additionalContext;
    assert.match(ctx, /Time sampled at PostToolUse \(bash\):/);
  });

  it('PostToolUseFailure 输出一行时间', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'PostToolUseFailure',
      tool_name: 'edit',
      session_id: 'test-session',
    });
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    const ctx = output.hookSpecificOutput.additionalContext;
    assert.match(ctx, /Time sampled at PostToolUseFailure \(edit\):/);
  });

  it('SessionEnd 清理状态并退出 0', async () => {
    const dataDir = mkdtempSync(join(tmpdir(), 'clock-test-'));
    const { code, stdout } = await runHook({
      hook_event_name: 'SessionEnd',
      session_id: 'cleanup-test',
    }, { QODER_PLUGIN_DATA: dataDir });
    assert.equal(code, 0);
    assert.equal(stdout, '');
    rmSync(dataDir, { recursive: true, force: true });
  });

  it('非法 payload 静默退出 0', async () => {
    const { code, stdout } = await runHook('not-json');
    assert.equal(code, 0);
  });

  it('不支持的事件静默退出 0', async () => {
    const { code, stdout } = await runHook({
      hook_event_name: 'UnknownEvent',
    });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('SessionStart 初始化 turn 1', async () => {
    const dataDir = mkdtempSync(join(tmpdir(), 'clock-test-'));
    const { code, stdout } = await runHook({
      hook_event_name: 'SessionStart',
      session_id: 'session-start-test',
    }, { QODER_PLUGIN_DATA: dataDir });
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    const ctx = output.hookSpecificOutput.additionalContext;
    assert.match(ctx, /Time sampled while preparing turn 1:/);
    rmSync(dataDir, { recursive: true, force: true });
  });

  it('连续 UserPromptSubmit 递增 turn', async () => {
    const dataDir = mkdtempSync(join(tmpdir(), 'clock-test-'));
    const env = { QODER_PLUGIN_DATA: dataDir };
    
    // 第一次
    await runHook({
      hook_event_name: 'SessionStart',
      session_id: 'turn-test',
    }, env);
    
    // 第二次
    const { stdout: stdout2 } = await runHook({
      hook_event_name: 'UserPromptSubmit',
      session_id: 'turn-test',
    }, env);
    const output2 = JSON.parse(stdout2);
    const ctx2 = output2.hookSpecificOutput.additionalContext;
    assert.match(ctx2, /Time sampled while preparing turn 2:/);
    
    rmSync(dataDir, { recursive: true, force: true });
  });
});

describe('hooks.json 配置', () => {
  it('Qoder hooks.json 引用 inject-clock.js', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    const json = JSON.stringify(hooks);
    assert.match(json, /inject-clock\.js/);
    assert.doesNotMatch(json, /inject_clock\.py/);
  });

  it('Qwen hooks.json 引用 inject-clock.js', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QWEN, 'utf-8'));
    const json = JSON.stringify(hooks);
    assert.match(json, /inject-clock\.js/);
    assert.doesNotMatch(json, /inject_clock\.py/);
  });

  it('Qoder hooks.json 使用 node 命令', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    for (const event of Object.values(hooks.hooks)) {
      for (const group of event) {
        for (const hook of group.hooks) {
          assert.equal(hook.command, 'node');
        }
      }
    }
  });

  it('Qwen hooks.json 使用 node 命令', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QWEN, 'utf-8'));
    for (const event of Object.values(hooks)) {
      for (const group of event) {
        for (const hook of group.hooks) {
          assert.match(hook.command, /^node\s/);
        }
      }
    }
  });
});
