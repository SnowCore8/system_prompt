/**
 * 文件路径与内容摘要工具：插件根解析、项目目录遍历、规则文件定位。
 *
 * 所有读取失败都按“未命中”处理，调用方无需捕获异常。
 */

import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';

/**
 * 计算数据的 sha256 十六进制摘要。
 *
 * @param {string | Buffer} data
 * @returns {string}
 */
export function sha256(data) {
  return createHash('sha256').update(data).digest('hex');
}

/**
 * 判断文件内容摘要是否与给定摘要一致；文件缺失或不可读时返回 false。
 *
 * @param {string} filePath
 * @param {string} digest
 * @returns {boolean}
 */
export function fileMatches(filePath, digest) {
  try {
    return sha256(readFileSync(filePath)) === digest;
  } catch {
    return false;
  }
}

/**
 * 从 cwd 开始向上收集目录，遇到含 .git 的目录即停止；没有 .git 时一直到根。
 *
 * @param {string} cwd
 * @returns {string[]}
 */
export function projectDirs(cwd) {
  let current;
  try {
    current = resolve(cwd);
  } catch {
    return [];
  }
  const dirs = [];
  while (true) {
    dirs.push(current);
    if (existsSync(join(current, '.git'))) {
      break;
    }
    const parent = dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }
  return dirs;
}

/**
 * 解析插件根：显式参数优先，其次环境变量，再从 startDir 向上寻找规则文件；
 * 都未命中时回退到 startDir 的父目录。
 *
 * @param {{ argv: string[], envNames: string[], startDir: string, rulesDirs: string[], filename: string }} options
 * @returns {string}
 */
export function resolvePluginRoot({ argv, envNames, startDir, rulesDirs, filename }) {
  const explicit = Array.isArray(argv) ? argv[2] : undefined;
  if (explicit) {
    return explicit;
  }
  for (const name of envNames) {
    const value = process.env[name];
    if (value) {
      return value;
    }
  }

  const base = resolve(startDir || process.cwd());
  let current = base;
  while (true) {
    for (const directory of rulesDirs) {
      if (existsSync(join(current, directory, filename))) {
        return current;
      }
    }
    const parent = dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }
  return dirname(base);
}

/**
 * 在 root 下按 rulesDirs 顺序查找规则文件，未找到返回 null。
 *
 * @param {string} root
 * @param {string[]} rulesDirs
 * @param {string} filename
 * @returns {string | null}
 */
export function findRulesFile(root, rulesDirs, filename) {
  for (const directory of rulesDirs) {
    const candidate = join(root, directory, filename);
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

/**
 * 收集配置根：环境变量按顺序优先，其后是 home 下的固定目录。
 *
 * @param {string[]} envNames
 * @param {string[]} homeDirs
 * @returns {string[]}
 */
export function configRoots(envNames, homeDirs) {
  const roots = [];
  for (const name of envNames) {
    const value = process.env[name];
    if (value) {
      roots.push(value);
    }
  }
  for (const directory of homeDirs) {
    roots.push(join(homedir(), directory));
  }
  return roots;
}
