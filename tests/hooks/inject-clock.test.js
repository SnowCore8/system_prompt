import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, it } from 'node:test';

import { CLOCK_HOOK, cleanup, contextOf, HOOKS_QODER, HOOKS_QWEN, makeSandbox, runHook } from './helpers.js';

/**
 * 建一个插件数据目录，并在测试结束时清理。
 *
 * @param {import('node:test').TestContext} t
 * @returns {string}
 */
function dataDirFor(t) {
  const dir = mkdtempSync(join(tmpdir(), 'hooks-clock-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

/**
 * 列出 clock 状态文件；目录不存在时返回空数组。
 *
 * @param {string} dataDir
 * @returns {string[]}
 */
function stateFiles(dataDir) {
  const dir = join(dataDir, 'clock');
  return existsSync(dir) ? readdirSync(dir) : [];
}

describe('inject-clock.js', () => {
  it('Qoder UserPromptSubmit 按 session 递增 turn', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const dataDir = dataDirFor(t);
    const env = box.env({ QODER_PLUGIN_DATA: dataDir });
    const payload = { hook_event_name: 'UserPromptSubmit', session_id: 'session-1' };

    const first = await runHook(CLOCK_HOOK, payload, { env });
    assert.equal(first.code, 0);
    const firstContext = contextOf(first.stdout);
    assert.match(firstContext, /Time sampled while preparing turn 1:/);
    assert.match(firstContext, /Browser time zone for this request:/);
    assert.match(firstContext, /Elapsed since the preceding model-visible message: unavailable\./);
    assert.equal(stateFiles(dataDir).length, 1);

    const second = await runHook(CLOCK_HOOK, payload, { env });
    assert.equal(second.code, 0);
    const secondContext = contextOf(second.stdout);
    assert.match(secondContext, /Time sampled while preparing turn 2:/);
    assert.match(secondContext, /Elapsed since the preceding model-visible message: \d+s\./);

    const [name] = stateFiles(dataDir);
    const state = JSON.parse(readFileSync(join(dataDir, 'clock', name), 'utf-8'));
    assert.equal(state.turn, 2);
    assert.equal(typeof state.last, 'number');
  });

  it('Qoder SessionStart 初始化 turn 1，随后提示进入 turn 2', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const dataDir = dataDirFor(t);
    const env = box.env({ QODER_PLUGIN_DATA: dataDir });

    const start = await runHook(CLOCK_HOOK, { hook_event_name: 'SessionStart', session_id: 'session-start' }, { env });
    assert.match(contextOf(start.stdout), /Time sampled while preparing turn 1:/);

    const prompt = await runHook(
      CLOCK_HOOK,
      { hook_event_name: 'UserPromptSubmit', session_id: 'session-start' },
      { env },
    );
    assert.match(contextOf(prompt.stdout), /Time sampled while preparing turn 2:/);
  });

  it('Qwen 无数据目录时两次都 turn 1 且不写盘', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const dataDir = dataDirFor(t);
    // Qwen 只设置 CLAUDE_* 等变量；脚本不应据此写状态
    const env = box.env({ CLAUDE_PLUGIN_DATA: dataDir });
    const payload = { hook_event_name: 'UserPromptSubmit', session_id: 'qwen-session' };

    const first = await runHook(CLOCK_HOOK, payload, { env });
    const second = await runHook(CLOCK_HOOK, payload, { env });

    for (const result of [first, second]) {
      assert.equal(result.code, 0);
      const context = contextOf(result.stdout);
      assert.match(context, /Time sampled while preparing turn 1:/);
      assert.match(context, /Elapsed since the preceding model-visible message: unavailable\./);
    }
    assert.equal(existsSync(join(dataDir, 'clock')), false);
  });

  it('工具事件只输出一行时间且不写状态', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const dataDir = dataDirFor(t);
    const env = box.env({ QODER_PLUGIN_DATA: dataDir });

    for (const event of ['PreToolUse', 'PostToolUse', 'PostToolUseFailure']) {
      const { code, stdout } = await runHook(
        CLOCK_HOOK,
        { hook_event_name: event, tool_name: 'read', session_id: 'tool-session' },
        { env },
      );
      assert.equal(code, 0);
      const context = contextOf(stdout);
      assert.equal(context.split('\n').length, 1);
      assert.match(context, new RegExp(`^Time sampled at ${event} \\(read\\): .+\\.$`));
      assert.equal(context.includes('Browser time zone'), false);
    }
    assert.equal(existsSync(join(dataDir, 'clock')), false);
  });

  it('SessionEnd 清理状态并退出 0', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const dataDir = dataDirFor(t);
    const env = box.env({ QODER_PLUGIN_DATA: dataDir });
    const session = 'cleanup-session';

    await runHook(CLOCK_HOOK, { hook_event_name: 'UserPromptSubmit', session_id: session }, { env });
    assert.equal(stateFiles(dataDir).length, 1);

    const { code, stdout } = await runHook(CLOCK_HOOK, { hook_event_name: 'SessionEnd', session_id: session }, { env });
    assert.equal(code, 0);
    assert.equal(stdout, '');
    assert.equal(stateFiles(dataDir).length, 0);
  });

  it('非法 payload 静默退出 0', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(CLOCK_HOOK, 'not-json', { env: box.env(), raw: true });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('不支持的事件静默退出 0', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(CLOCK_HOOK, { hook_event_name: 'UnknownEvent' }, { env: box.env() });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });
});

describe('hooks.json 配置', () => {
  it('Qoder hooks.json 引用 inject-clock.js 且不用 Python 实现', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    const json = JSON.stringify(hooks);
    assert.match(json, /inject-clock\.js/);
    assert.doesNotMatch(json, /inject_clock\.py/);
  });

  it('Qwen hooks.json 引用 inject-clock.js 且不用 Python 实现', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QWEN, 'utf-8'));
    const json = JSON.stringify(hooks);
    assert.match(json, /inject-clock\.js/);
    assert.doesNotMatch(json, /inject_clock\.py/);
  });

  it('Qoder hooks.json 全部使用 node 命令', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    for (const groups of Object.values(hooks.hooks)) {
      for (const group of groups) {
        for (const hook of group.hooks) {
          assert.equal(hook.command, 'node');
        }
      }
    }
  });

  it('Qwen hooks.json 全部使用 node 命令', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QWEN, 'utf-8'));
    for (const groups of Object.values(hooks)) {
      for (const group of groups) {
        for (const hook of group.hooks) {
          assert.match(hook.command, /^node\s/);
        }
      }
    }
  });
});
