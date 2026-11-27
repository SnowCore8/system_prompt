/**
 * hook 测试公共工具：临时沙箱、子进程执行与输出解析。
 */

import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));

export const REPO = join(HERE, '..', '..');
export const SCRIPTS = join(REPO, 'shared', 'scripts');
export const CONSTRAINTS_HOOK = join(SCRIPTS, 'inject-constraints.js');
export const COMPACT_HOOK = join(SCRIPTS, 'inject-compact.js');
export const CLOCK_HOOK = join(SCRIPTS, 'inject-clock.js');
export const RULES = join(REPO, 'rules', 'global-user-constraints.md');
export const HOOKS_QODER = join(REPO, 'plugins', 'qoder', 'hooks', 'hooks.json');
export const HOOKS_QWEN = join(REPO, 'plugins', 'qwen', 'hooks', 'qwen-hooks.json');
export const MANIFEST_QWEN = join(REPO, 'plugins', 'qwen', 'qwen-extension.json');

// 子进程环境里必须隔离的宿主变量，避免测试机上的 Qoder/Qwen 配置影响断言
const ISOLATED_ENVS = [
  'QODER_PLUGIN_ROOT',
  'QODER_PLUGIN_DATA',
  'CLAUDE_PLUGIN_ROOT',
  'CLAUDE_PLUGIN_DATA',
  'QODERCN_CONFIG_DIR',
  'QODER_CONFIG_DIR',
  'TZ',
];

/**
 * 创建隔离的临时沙箱：HOME、Qoder 配置根都指向临时目录。
 *
 * @returns {{ dir: string, config: string, env: (extra?: Record<string, string>) => Record<string, string | undefined> }}
 */
export function makeSandbox() {
  const dir = mkdtempSync(join(tmpdir(), 'hooks-test-'));
  const config = join(dir, 'config');
  mkdirSync(config, { recursive: true });

  const baseEnv = { ...process.env, HOME: dir };
  for (const name of ISOLATED_ENVS) {
    delete baseEnv[name];
  }
  baseEnv.QODERCN_CONFIG_DIR = config;
  baseEnv.QODER_CONFIG_DIR = config;

  return {
    dir,
    config,
    env(extra = {}) {
      return { ...baseEnv, ...extra };
    },
  };
}

/**
 * 删除沙箱目录。
 *
 * @param {{ dir: string }} box
 */
export function cleanup(box) {
  rmSync(box.dir, { recursive: true, force: true });
}

/**
 * 以子进程执行 hook 脚本并收集输出。
 *
 * @param {string} script
 * @param {unknown} payload
 * @param {{ env?: Record<string, string | undefined>, args?: string[], raw?: boolean }} [options]
 * @returns {Promise<{ code: number | null, stdout: string, stderr: string }>}
 */
export function runHook(script, payload, { env = process.env, args = [], raw = false } = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [script, ...args], {
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk) => {
      stdout += chunk;
    });
    child.stderr.on('data', (chunk) => {
      stderr += chunk;
    });
    child.on('close', (code) => {
      resolve({ code, stdout, stderr });
    });

    child.stdin.end(raw ? String(payload) : JSON.stringify(payload));
  });
}

/**
 * 解析 hook 输出中的 additionalContext。
 *
 * @param {string} stdout
 * @returns {string}
 */
export function contextOf(stdout) {
  return JSON.parse(stdout).hookSpecificOutput.additionalContext;
}
