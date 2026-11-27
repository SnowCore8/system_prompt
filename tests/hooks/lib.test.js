import assert from 'node:assert/strict';
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { describe, it } from 'node:test';

import {
  configRoots,
  fileMatches,
  findRulesFile,
  projectDirs,
  resolvePluginRoot,
  sha256,
} from '../../shared/scripts/lib/paths.js';
import {
  CONFIG_ENVS,
  dedupeCandidates,
  HOME_CONFIG_DIRS,
  PLUGIN_ROOT_ENVS,
  RULES_DIRS,
  RULES_FILENAME,
  SKIP_SOURCES,
} from '../../shared/scripts/lib/qoder.js';
import { createClockState } from '../../shared/scripts/lib/state.js';
import {
  formatCompactText,
  formatDuration,
  formatTimestamp,
  formatToolTime,
  formatUserTime,
  timezoneName,
} from '../../shared/scripts/lib/time.js';

/**
 * 建一个测试用临时目录，并在测试结束时清理。
 *
 * @param {import('node:test').TestContext} t
 * @returns {string}
 */
function tempDir(t) {
  const dir = mkdtempSync(join(tmpdir(), 'hooks-lib-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

/**
 * 临时修改环境变量，返回恢复函数。
 *
 * @param {Record<string, string | undefined>} values
 * @returns {() => void}
 */
function withEnv(values) {
  const saved = new Map();
  for (const [name, value] of Object.entries(values)) {
    saved.set(name, process.env[name]);
    if (value === undefined) {
      delete process.env[name];
    } else {
      process.env[name] = value;
    }
  }
  return () => {
    for (const [name, value] of saved) {
      if (value === undefined) {
        delete process.env[name];
      } else {
        process.env[name] = value;
      }
    }
  };
}

describe('paths.sha256 / fileMatches', () => {
  it('摘要稳定，文件命中按内容比较', (t) => {
    const dir = tempDir(t);
    const file = join(dir, 'rules.md');
    writeFileSync(file, '约束正文', 'utf-8');

    assert.equal(sha256('约束正文'), sha256(Buffer.from('约束正文', 'utf-8')));
    assert.equal(fileMatches(file, sha256('约束正文')), true);
    assert.equal(fileMatches(file, sha256('别的正文')), false);
    assert.equal(fileMatches(join(dir, 'missing.md'), sha256('约束正文')), false);
  });
});

describe('paths.projectDirs', () => {
  it('在含 .git 的目录停止，不再向上', (t) => {
    const root = tempDir(t);
    mkdirSync(join(root, '.git'));
    const nested = join(root, 'a', 'b');
    mkdirSync(nested, { recursive: true });

    assert.deepEqual(projectDirs(nested), [nested, join(root, 'a'), root]);
  });

  it('没有 .git 时一直收集到根，或提前遇到 .git', (t) => {
    const root = tempDir(t);
    const dirs = projectDirs(root);

    assert.equal(dirs[0], root);
    for (let index = 0; index < dirs.length - 1; index += 1) {
      assert.equal(dirs[index + 1], dirname(dirs[index]));
    }
    const last = dirs.at(-1);
    assert.ok(dirname(last) === last || existsSync(join(last, '.git')), '应终止于文件系统根或含 .git 的目录');
  });
});

describe('paths.resolvePluginRoot', () => {
  it('argv[2] 优先于环境变量', (t) => {
    const root = tempDir(t);
    const restore = withEnv({ HOOKS_TEST_ROOT: '/from-env' });
    t.after(restore);

    const resolved = resolvePluginRoot({
      argv: ['node', 'hook.js', '/from-argv'],
      envNames: ['HOOKS_TEST_ROOT'],
      startDir: root,
      rulesDirs: RULES_DIRS,
      filename: RULES_FILENAME,
    });
    assert.equal(resolved, '/from-argv');
  });

  it('环境变量按顺序取第一个非空值', (t) => {
    const root = tempDir(t);
    const restore = withEnv({ HOOKS_TEST_ROOT: '/from-env', HOOKS_TEST_ROOT_ALT: '/from-alt' });
    t.after(restore);

    const resolved = resolvePluginRoot({
      argv: ['node', 'hook.js'],
      envNames: ['HOOKS_TEST_ROOT_MISSING', 'HOOKS_TEST_ROOT', 'HOOKS_TEST_ROOT_ALT'],
      startDir: root,
      rulesDirs: RULES_DIRS,
      filename: RULES_FILENAME,
    });
    assert.equal(resolved, '/from-env');
  });

  it('从 startDir 向上找到规则文件所在目录', (t) => {
    const root = tempDir(t);
    mkdirSync(join(root, 'rules'), { recursive: true });
    writeFileSync(join(root, 'rules', RULES_FILENAME), '正文', 'utf-8');
    const startDir = join(root, 'shared', 'scripts');
    mkdirSync(startDir, { recursive: true });

    const resolved = resolvePluginRoot({
      argv: ['node', 'hook.js'],
      envNames: [],
      startDir,
      rulesDirs: RULES_DIRS,
      filename: RULES_FILENAME,
    });
    assert.equal(resolved, root);
  });

  it('都未命中时回退到 startDir 的父目录', (t) => {
    const root = tempDir(t);
    const startDir = join(root, 'scripts');
    mkdirSync(startDir, { recursive: true });

    const resolved = resolvePluginRoot({
      argv: ['node', 'hook.js'],
      envNames: [],
      startDir,
      rulesDirs: RULES_DIRS,
      filename: 'definitely-missing-rules.md',
    });
    assert.equal(resolved, root);
  });
});

describe('paths.findRulesFile / configRoots', () => {
  it('只在 rulesDirs 下查找规则文件', (t) => {
    const root = tempDir(t);
    mkdirSync(join(root, 'rules'), { recursive: true });
    const file = join(root, 'rules', RULES_FILENAME);
    writeFileSync(file, '正文', 'utf-8');

    assert.equal(findRulesFile(root, RULES_DIRS, RULES_FILENAME), file);
    assert.equal(findRulesFile(root, ['constraints'], RULES_FILENAME), null);
    assert.equal(findRulesFile(root, ['constraints'], 'other.md'), null);
  });

  it('配置根先环境变量后 home 目录', (t) => {
    const home = tempDir(t);
    const restore = withEnv({
      HOME: home,
      HOOKS_CFG_A: '/cfg-a',
      HOOKS_CFG_EMPTY: '',
    });
    t.after(restore);

    const roots = configRoots(['HOOKS_CFG_A', 'HOOKS_CFG_EMPTY', 'HOOKS_CFG_MISSING'], HOME_CONFIG_DIRS);
    assert.deepEqual(roots, ['/cfg-a', join(home, '.qoder-cn'), join(home, '.qoder')]);
  });
});

describe('time.formatDuration', () => {
  it('按 d/h/m/s 组合且秒始终存在', () => {
    assert.equal(formatDuration(0), '0s');
    assert.equal(formatDuration(1000), '1s');
    assert.equal(formatDuration(65_000), '1m 5s');
    assert.equal(formatDuration(3_661_000), '1h 1m 1s');
    assert.equal(formatDuration(90_061_000), '1d 1h 1m 1s');
    assert.equal(formatDuration(-5000), '0s');
  });
});

describe('time 文本格式', () => {
  const now = new Date(2026, 0, 2, 3, 4, 5, 6);

  it('formatTimestamp 带数值偏移与时区名', () => {
    const stamp = formatTimestamp(now);
    assert.match(stamp, /^2026-01-02T03:04:05\.006[+-]\d{2}:\d{2}\[.+\]$/);
    assert.ok(stamp.endsWith(`[${timezoneName(now) || 'UTC'}]`));
  });

  it('formatUserTime 输出三行并计算 elapsed', () => {
    const text = formatUserTime({ now, turn: 3, last: now.getTime() - 65_000 });
    const lines = text.split('\n');
    assert.equal(lines.length, 3);
    assert.equal(lines[0], `Time sampled while preparing turn 3: ${formatTimestamp(now)}`);
    assert.match(
      lines[1],
      /^Browser time zone for this request: .+\. Interpret otherwise-unqualified dates and times in this zone\.$/,
    );
    assert.equal(lines[2], 'Elapsed since the preceding model-visible message: 1m 5s.');
  });

  it('formatUserTime 无上次时间时输出 unavailable', () => {
    const text = formatUserTime({ now, turn: 1, last: null });
    assert.match(text, /Elapsed since the preceding model-visible message: unavailable\./);
  });

  it('formatToolTime 只输出一行，可选工具名', () => {
    const withTool = formatToolTime({ event: 'PreToolUse', tool: 'read', now });
    const withoutTool = formatToolTime({ event: 'PostToolUse', now });
    assert.equal(withTool, `Time sampled at PreToolUse (read): ${formatTimestamp(now)}.`);
    assert.equal(withoutTool, `Time sampled at PostToolUse: ${formatTimestamp(now)}.`);
    assert.equal(withTool.includes('Browser time zone'), false);
  });

  it('formatCompactText 保留提醒、空行与两行时间', () => {
    const lines = formatCompactText(now).split('\n');
    assert.deepEqual(lines.slice(0, 2), ['Never violate global user constraints.', '']);
    assert.equal(lines[2], `Time sampled after context compaction: ${formatTimestamp(now)}.`);
    assert.match(
      lines[3],
      /^Browser time zone for this request: .+\. Interpret otherwise-unqualified dates and times in this zone\.$/,
    );
  });
});

describe('state.createClockState', () => {
  it('无 dataDir 或 sessionId 时返回 null', (t) => {
    const dir = tempDir(t);
    assert.equal(createClockState({ dataDir: undefined, sessionId: 's1' }), null);
    assert.equal(createClockState({ dataDir: dir, sessionId: '' }), null);
    assert.equal(createClockState({ dataDir: dir, sessionId: 42 }), null);
  });

  it('按 session 计算路径并支持写入、读取与清理', (t) => {
    const dir = tempDir(t);
    const state = createClockState({ dataDir: dir, sessionId: 'session-1' });
    assert.ok(state);
    assert.equal(state.path, join(dir, 'clock', `${sha256('session-1').slice(0, 32)}.json`));
    assert.equal(state.load(), null);

    state.save(2, 1_700_000_000_000);
    assert.deepEqual(state.load(), { turn: 2, last: 1_700_000_000_000 });

    state.clear();
    assert.equal(existsSync(state.path), false);
    assert.equal(state.load(), null);
  });

  it('状态内容非法时按无状态处理', (t) => {
    const dir = tempDir(t);
    const state = createClockState({ dataDir: dir, sessionId: 'session-bad' });
    assert.ok(state);
    mkdirSync(dirname(state.path), { recursive: true });

    writeFileSync(state.path, 'not-json', 'utf-8');
    assert.equal(state.load(), null);

    writeFileSync(state.path, JSON.stringify({ turn: 0, last: 1 }), 'utf-8');
    assert.equal(state.load(), null);

    writeFileSync(state.path, JSON.stringify({ turn: 1, last: 'soon' }), 'utf-8');
    assert.equal(state.load(), null);
  });
});

describe('qoder 常量与去重候选', () => {
  it('插件根、规则目录与跳过来源收敛为 Qoder-only', () => {
    assert.deepEqual(PLUGIN_ROOT_ENVS, ['QODER_PLUGIN_ROOT']);
    assert.deepEqual(CONFIG_ENVS, ['QODERCN_CONFIG_DIR', 'QODER_CONFIG_DIR']);
    assert.deepEqual(RULES_DIRS, ['rules']);
    assert.deepEqual(HOME_CONFIG_DIRS, ['.qoder-cn', '.qoder']);
    assert.equal(SKIP_SOURCES.has('resume'), true);
  });

  it('候选覆盖用户配置根与项目 .qoder/rules、AGENTS，且不含 Qwen/Claude', (t) => {
    const home = tempDir(t);
    const project = join(home, 'project');
    mkdirSync(join(project, '.git'), { recursive: true });
    mkdirSync(join(project, '.qwen', 'rules'), { recursive: true });
    const restore = withEnv({
      HOME: home,
      QODER_CONFIG_DIR: join(home, 'cfg'),
      QODERCN_CONFIG_DIR: undefined,
    });
    t.after(restore);

    const files = dedupeCandidates({ cwd: project });

    assert.ok(files.includes(join(project, '.qoder', 'rules', RULES_FILENAME)));
    assert.ok(files.includes(join(project, 'AGENTS.md')));
    assert.ok(files.includes(join(project, 'AGENTS.local.md')));
    assert.ok(files.includes(join(home, 'cfg', 'rules', RULES_FILENAME)));
    assert.ok(files.includes(join(home, 'cfg', 'AGENTS.md')));
    assert.ok(files.includes(join(home, '.qoder-cn', 'rules', RULES_FILENAME)));
    assert.ok(files.includes(join(home, '.qoder', 'rules', RULES_FILENAME)));

    assert.equal(
      files.some((file) => file.includes('.qwen')),
      false,
    );
    assert.equal(
      files.some((file) => /QWEN\.md$/.test(file)),
      false,
    );
    assert.equal(
      files.some((file) => file.includes('CLAUDE')),
      false,
    );
    assert.equal(new Set(files).size, files.length);
  });

  it('项目目录回退到 QODER_PROJECT_DIR，payload.cwd 优先', (t) => {
    const home = tempDir(t);
    const payloadDir = join(home, 'payload');
    const envDir = join(home, 'envdir');
    mkdirSync(payloadDir, { recursive: true });
    mkdirSync(envDir, { recursive: true });
    const restore = withEnv({
      HOME: home,
      QODER_PROJECT_DIR: envDir,
      QODER_CONFIG_DIR: undefined,
      QODERCN_CONFIG_DIR: undefined,
    });
    t.after(restore);

    const fromPayload = dedupeCandidates({ cwd: payloadDir });
    assert.ok(fromPayload.includes(join(payloadDir, 'AGENTS.md')));
    assert.equal(
      fromPayload.some((file) => file.startsWith(envDir)),
      false,
    );

    const fromEnv = dedupeCandidates({});
    assert.ok(fromEnv.includes(join(envDir, 'AGENTS.md')));
  });
});
