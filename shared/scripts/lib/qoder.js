/**
 * Qoder 专用常量与候选路径。
 *
 * 基线为 Qoder CLI CN 1.1.90：插件根只认 QODER_PLUGIN_ROOT，配置根只认
 * QODERCN_CONFIG_DIR/QODER_CONFIG_DIR 与 ~/.qoder-cn、~/.qoder；项目规则只查
 * .qoder/rules、AGENTS.md 与 AGENTS.local.md。Qwen/Claude 的路径不参与去重。
 */

import { join } from 'node:path';
import { configRoots, findRulesFile, projectDirs, resolvePluginRoot } from './paths.js';

export const RULES_FILENAME = 'global-user-constraints.md';
export const RULES_DIRS = ['rules'];
export const PLUGIN_ROOT_ENVS = ['QODER_PLUGIN_ROOT'];
export const CONFIG_ENVS = ['QODERCN_CONFIG_DIR', 'QODER_CONFIG_DIR'];
export const HOME_CONFIG_DIRS = ['.qoder-cn', '.qoder'];
export const SKIP_SOURCES = new Set(['resume']);

/**
 * 解析 Qoder 插件根。
 *
 * @param {{ argv: string[], startDir: string }} options
 * @returns {string}
 */
export function pluginRoot({ argv, startDir }) {
  return resolvePluginRoot({
    argv,
    envNames: PLUGIN_ROOT_ENVS,
    startDir,
    rulesDirs: RULES_DIRS,
    filename: RULES_FILENAME,
  });
}

/**
 * 定位插件根下的约束正文。
 *
 * @param {string} root
 * @returns {string | null}
 */
export function rulesFile(root) {
  return findRulesFile(root, RULES_DIRS, RULES_FILENAME);
}

/**
 * 生成用于同内容去重的候选文件：用户配置根与项目目录，去重后返回。
 *
 * @param {Record<string, unknown>} payload
 * @returns {string[]}
 */
export function dedupeCandidates(payload) {
  const files = new Set();

  for (const root of configRoots(CONFIG_ENVS, HOME_CONFIG_DIRS)) {
    files.add(join(root, 'rules', RULES_FILENAME));
    files.add(join(root, 'AGENTS.md'));
  }

  const cwd = typeof payload?.cwd === 'string' && payload.cwd ? payload.cwd : process.cwd();
  for (const directory of projectDirs(cwd)) {
    files.add(join(directory, '.qoder', 'rules', RULES_FILENAME));
    files.add(join(directory, 'AGENTS.md'));
    files.add(join(directory, 'AGENTS.local.md'));
  }

  return [...files];
}
