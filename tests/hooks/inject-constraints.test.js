import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO = join(__dirname, '..', '..');
const HOOK = join(REPO, 'shared', 'scripts', 'inject-constraints.js');
const RULES = join(REPO, 'rules', 'global-user-constraints.md');
const HOOKS_QODER = join(REPO, 'plugins', 'qoder', 'hooks', 'hooks.json');
const HOOKS_QWEN = join(REPO, 'plugins', 'qwen', 'hooks', 'qwen-hooks.json');
const MANIFEST_QWEN = join(REPO, 'plugins', 'qwen', 'qwen-extension.json');

function makeSandbox() {
  const dir = mkdtempSync(join(tmpdir(), 'constraints-test-'));
  const config = join(dir, 'config');
  mkdirSync(config, { recursive: true });
  return {
    dir,
    env(extra = {}) {
      return {
        ...process.env,
        HOME: dir,
        QODERCN_CONFIG_DIR: config,
        QODER_CONFIG_DIR: config,
        QWEN_HOME: config,
        QWEN_CONFIG_DIR: config,
        ...extra,
      };
    },
    cleanup() {
      rmSync(dir, { recursive: true, force: true });
    },
  };
}

function runHook(payload, { env = process.env, args = [] } = {}) {
  return new Promise((resolve) => {
    const child = spawn('node', [HOOK, ...args], {
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    child.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
    child.on('close', (code) => resolve({ code, stdout: stdout.trim(), stderr }));
    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
  });
}

describe('inject-constraints.js', () => {
  it('SessionStart 必须注入约束全文', async () => {
    const box = makeSandbox();
    try {
      const { code, stdout } = await runHook(
        { hook_event_name: 'SessionStart', cwd: box.dir },
        { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
      );
      assert.equal(code, 0);
      const output = JSON.parse(stdout);
      assert.equal(output.hookSpecificOutput.hookEventName, 'SessionStart');
      const context = output.hookSpecificOutput.additionalContext;
      assert.equal(context.startsWith('全局用户约束（由插件于会话启动时注入，必须遵守）：'), true);
      assert.ok(context.length > 10000, '约束正文不应为空或被截断');
    } finally {
      box.cleanup();
    }
  });

  it('显式根参数优先于环境变量', async () => {
    const box = makeSandbox();
    try {
      const env = box.env();
      delete env.QODER_PLUGIN_ROOT;
      delete env.CLAUDE_PLUGIN_ROOT;
      const { code, stdout } = await runHook(
        { hook_event_name: 'SessionStart', cwd: box.dir },
        { env, args: [REPO] },
      );
      assert.equal(code, 0);
      const context = JSON.parse(stdout).hookSpecificOutput.additionalContext;
      assert.ok(context.length > 10000);
    } finally {
      box.cleanup();
    }
  });

  it('source=resume 跳过注入', async () => {
    const box = makeSandbox();
    try {
      const { code, stdout } = await runHook(
        { hook_event_name: 'SessionStart', source: 'resume', cwd: box.dir },
        { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
      );
      assert.equal(code, 0);
      assert.equal(stdout, '');
    } finally {
      box.cleanup();
    }
  });

  it('项目 AGENTS.md 已有同内容时跳过', async () => {
    const box = makeSandbox();
    try {
      copyFileSync(RULES, join(box.dir, 'AGENTS.md'));
      const { code, stdout } = await runHook(
        { hook_event_name: 'SessionStart', cwd: box.dir },
        { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
      );
      assert.equal(code, 0);
      assert.equal(stdout, '');
    } finally {
      box.cleanup();
    }
  });

  it('项目 .qoder/rules 已有同内容时跳过', async () => {
    const box = makeSandbox();
    try {
      const rulesDir = join(box.dir, '.qoder', 'rules');
      mkdirSync(rulesDir, { recursive: true });
      copyFileSync(RULES, join(rulesDir, 'global-user-constraints.md'));
      const { code, stdout } = await runHook(
        { hook_event_name: 'SessionStart', cwd: box.dir },
        { env: box.env({ QODER_PLUGIN_ROOT: REPO }) },
      );
      assert.equal(code, 0);
      assert.equal(stdout, '');
    } finally {
      box.cleanup();
    }
  });

  it('规则缺失时输出安装提示', async () => {
    const box = makeSandbox();
    try {
      const plugin = join(box.dir, 'plugin');
      mkdirSync(plugin, { recursive: true });
      const { code, stdout } = await runHook(
        { hook_event_name: 'SessionStart', cwd: box.dir },
        { env: box.env({ QODER_PLUGIN_ROOT: plugin }) },
      );
      assert.equal(code, 0);
      const context = JSON.parse(stdout).hookSpecificOutput.additionalContext;
      assert.ok(context.includes('全局用户约束未注入'));
    } finally {
      box.cleanup();
    }
  });

  it('正文超过 40 KiB 时输出上限提示', async () => {
    const box = makeSandbox();
    try {
      const plugin = join(box.dir, 'plugin');
      mkdirSync(join(plugin, 'rules'), { recursive: true });
      writeFileSync(join(plugin, 'rules', 'global-user-constraints.md'), 'x'.repeat(40961));
      const { code, stdout } = await runHook(
        { hook_event_name: 'SessionStart', cwd: box.dir },
        { env: box.env({ QODER_PLUGIN_ROOT: plugin }) },
      );
      assert.equal(code, 0);
      const context = JSON.parse(stdout).hookSpecificOutput.additionalContext;
      assert.ok(context.includes('超过 40 KiB 硬上限'));
    } finally {
      box.cleanup();
    }
  });

  it('UserPromptSubmit 输出固定提醒', async () => {
    const box = makeSandbox();
    try {
      const { code, stdout } = await runHook(
        { hook_event_name: 'UserPromptSubmit' },
        { env: box.env() },
      );
      assert.equal(code, 0);
      const output = JSON.parse(stdout);
      assert.equal(output.hookSpecificOutput.additionalContext, 'Never violate global user constraints.');
    } finally {
      box.cleanup();
    }
  });

  it('非法 payload 静默退出 0', async () => {
    const box = makeSandbox();
    try {
      const { code, stdout } = await runHook('not-json', { env: box.env() });
      assert.equal(code, 0);
      assert.equal(stdout, '');
    } finally {
      box.cleanup();
    }
  });

  it('不支持的事件静默退出 0', async () => {
    const box = makeSandbox();
    try {
      const { code, stdout } = await runHook(
        { hook_event_name: 'UnknownEvent' },
        { env: box.env() },
      );
      assert.equal(code, 0);
      assert.equal(stdout, '');
    } finally {
      box.cleanup();
    }
  });
});

describe('约束注入配置', () => {
  it('Qoder 在 SessionStart 调用 inject-constraints.js', () => {
    const hooks = JSON.parse(readFileSync(HOOKS_QODER, 'utf-8'));
    const injected = hooks.hooks.SessionStart.some((group) => (
      group.hooks.some((hook) => (hook.args || []).some((arg) => arg.endsWith('inject-constraints.js')))
    ));
    assert.equal(injected, true);
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
