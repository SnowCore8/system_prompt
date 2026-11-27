import assert from 'node:assert/strict';
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, it } from 'node:test';

import {
  CONSTRAINTS_HOOK,
  cleanup,
  contextOf,
  HOOKS_QODER,
  HOOKS_QWEN,
  MANIFEST_QWEN,
  makeSandbox,
  REPO,
  RULES,
  runHook,
} from './helpers.js';

const RULE_BASENAME = 'global-user-constraints.md';

/**
 * 在插件根写入约束正文。
 *
 * @param {string} plugin
 * @param {string} content
 */
function writeRule(plugin, content) {
  mkdirSync(join(plugin, 'rules'), { recursive: true });
  writeFileSync(join(plugin, 'rules', RULE_BASENAME), content, 'utf-8');
}

describe('inject-constraints.js', () => {
  it('SessionStart 注入约束全文且前缀不变', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout, stderr } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
    );
    assert.equal(code, 0, stderr);

    const context = contextOf(stdout);
    assert.equal(context.startsWith('全局用户约束（由插件于会话启动时注入，必须遵守）：'), true);
    assert.ok(context.length > 10000, '约束正文不应为空或被截断');
    assert.equal(context.endsWith(readFileSync(RULES, 'utf-8').trim()), true);
  });

  it('显式根参数优先于环境变量', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const plugin = join(box.dir, 'empty-plugin');
    mkdirSync(plugin, { recursive: true });

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: plugin }), args: [REPO] },
    );
    assert.equal(code, 0);
    assert.ok(contextOf(stdout).length > 10000);
  });

  it('source=resume 跳过注入', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', source: 'resume', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
    );
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('项目 AGENTS.md 已有同内容时跳过', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    mkdirSync(join(box.dir, '.git'));
    copyFileSync(RULES, join(box.dir, 'AGENTS.md'));

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
    );
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('项目 AGENTS.local.md 已有同内容时跳过', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    mkdirSync(join(box.dir, '.git'));
    copyFileSync(RULES, join(box.dir, 'AGENTS.local.md'));

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
    );
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('项目 .qoder/rules 已有同内容时跳过', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    mkdirSync(join(box.dir, '.git'));
    mkdirSync(join(box.dir, '.qoder', 'rules'), { recursive: true });
    copyFileSync(RULES, join(box.dir, '.qoder', 'rules', RULE_BASENAME));

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
    );
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('项目 .qwen/rules 有同内容时不参与去重', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    mkdirSync(join(box.dir, '.git'));
    mkdirSync(join(box.dir, '.qwen', 'rules'), { recursive: true });
    copyFileSync(RULES, join(box.dir, '.qwen', 'rules', RULE_BASENAME));

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
    );
    assert.equal(code, 0);
    assert.ok(contextOf(stdout).length > 10000);
  });

  it('规则缺失时输出安装提示', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const plugin = join(box.dir, 'plugin');
    mkdirSync(plugin, { recursive: true });

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: plugin }) },
    );
    assert.equal(code, 0);
    const context = contextOf(stdout);
    assert.equal(context.includes('全局用户约束未注入'), true);
    assert.equal(context.includes(RULE_BASENAME), true);
  });

  it('规则读取失败时输出读取提示', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const plugin = join(box.dir, 'plugin');
    mkdirSync(join(plugin, 'rules', RULE_BASENAME), { recursive: true });

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: plugin }) },
    );
    assert.equal(code, 0);
    const context = contextOf(stdout);
    assert.equal(context.includes('全局用户约束未注入'), true);
    assert.equal(context.includes('读取'), true);
    assert.equal(context.includes('失败'), true);
  });

  it('正文超过 64 KiB 时输出上限提示', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));
    const plugin = join(box.dir, 'plugin');
    writeRule(plugin, 'x'.repeat(64 * 1024 + 1));

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'SessionStart', cwd: box.dir },
      { env: box.env({ QODER_PLUGIN_ROOT: plugin }) },
    );
    assert.equal(code, 0);
    const context = contextOf(stdout);
    assert.equal(context.includes('超过 64 KiB 硬上限'), true);
  });

  it('UserPromptSubmit 输出固定提醒', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(
      CONSTRAINTS_HOOK,
      { hook_event_name: 'UserPromptSubmit' },
      { env: box.env() },
    );
    assert.equal(code, 0);
    const output = JSON.parse(stdout);
    assert.equal(output.hookSpecificOutput.hookEventName, 'UserPromptSubmit');
    assert.equal(output.hookSpecificOutput.additionalContext, 'Never violate global user constraints.');
  });

  it('非法 payload 静默退出 0', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(CONSTRAINTS_HOOK, 'not-json', { env: box.env(), raw: true });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });

  it('不支持的事件静默退出 0', async (t) => {
    const box = makeSandbox();
    t.after(() => cleanup(box));

    const { code, stdout } = await runHook(CONSTRAINTS_HOOK, { hook_event_name: 'UnknownEvent' }, { env: box.env() });
    assert.equal(code, 0);
    assert.equal(stdout, '');
  });
});

describe('约束注入配置', () => {
  it('Qoder 在 SessionStart 与 UserPromptSubmit 调用 inject-constraints.js', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    for (const event of ['SessionStart', 'UserPromptSubmit']) {
      const referenced = hooks.hooks[event].some((group) =>
        group.hooks.some((hook) => (hook.args || []).some((arg) => arg.endsWith('inject-constraints.js'))),
      );
      assert.equal(referenced, true, `${event} 应调用 inject-constraints.js`);
    }
  });

  it('Qwen 不再通过 hook 注入约束', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QWEN, 'utf-8'));
    assert.equal(JSON.stringify(hooks).includes('inject-constraints.js'), false);
    assert.equal(JSON.stringify(hooks).includes('inject-clock.js'), true);
  });

  it('Qwen 清单用 contextFileName 加载约束', () => {
    const manifest = JSON.parse(readFileSync(MANIFEST_QWEN, 'utf-8'));
    assert.deepEqual(manifest.contextFileName, ['constraints/global-user-constraints.md']);
  });
});
