import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

import {
  COMPACT_HOOK,
  HOOKS_QODER,
  cleanup,
  contextOf,
  makeSandbox,
  runHook,
} from './helpers.js';

const TIMESTAMP = String.raw`\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2}\[.+\]`;

describe('inject-compact.js', () => {
  it('SessionStart source=compact 输出提醒与时间', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(
      COMPACT_HOOK,
      { hook_event_name: 'SessionStart', source: 'compact' },
      { env: box.env() },
    );
    assert.equal(code, 0);

    const lines = contextOf(stdout).split('\n');
    assert.equal(lines.length, 4);
    assert.equal(lines[0], 'Never violate global user constraints.');
    assert.equal(lines[1], '');
    assert.match(lines[2], new RegExp(`^Time sampled after context compaction: ${TIMESTAMP}\\.$`));
    assert.match(lines[3], /^Browser time zone for this request: .+\. Interpret otherwise-unqualified dates and times in this zone\.$/);
  });

  it('SessionStart source!=compact 静默退出', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(
      COMPACT_HOOK,
      { hook_event_name: 'SessionStart', source: 'startup' },
      { env: box.env() },
    );
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('非 SessionStart 事件静默退出', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(
      COMPACT_HOOK,
      { hook_event_name: 'UserPromptSubmit', source: 'compact' },
      { env: box.env() },
    );
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('非法 payload 静默退出 0', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(COMPACT_HOOK, 'not-json', { env: box.env(), raw: true });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });
});

describe('Qoder hooks.json compact 配置', () => {
  it('包含 compact matcher 且调用 inject-compact.js', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    const compactGroup = hooks.hooks.SessionStart.find((group) => group.matcher === 'compact');
    assert.ok(compactGroup, '应存在 compact matcher 组');
    assert.equal(compactGroup.hooks[0].command, 'node');
    assert.match(compactGroup.hooks[0].args[0], /inject-compact\.js$/);
  });
});
