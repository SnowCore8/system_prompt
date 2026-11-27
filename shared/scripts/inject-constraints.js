#!/usr/bin/env node
/**
 * Qoder 约束注入钩子：SessionStart 注入约束全文，UserPromptSubmit 发送固定提醒。
 *
 * 根目录优先取显式参数（argv[2]），其次 QODER_PLUGIN_ROOT，最后从脚本位置向上查找。
 * `source=resume` 或用户/项目规则文件已有同内容时跳过；正文缺失、读取失败或
 * 超过 64 KiB 时只输出提示，不注入全文。异常静默退出 0，不阻断会话。
 */

import { readFileSync } from 'node:fs';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import { emitContext, isMain, runHook } from './lib/hook.js';
import { fileMatches, sha256 } from './lib/paths.js';
import { dedupeCandidates, pluginRoot, RULES_FILENAME, rulesFile, SKIP_SOURCES } from './lib/qoder.js';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const MAX_BYTES = 64 * 1024;
const REMINDER = 'Never violate the se-governance charter.';
const TITLE = 'se-governance 治理章程（由插件于会话启动时注入，必须遵守）：';

/**
 * 处理一次约束注入 hook 调用。
 *
 * @param {Record<string, unknown>} payload
 */
async function handle(payload) {
  const event = payload.hook_event_name;
  if (event === 'UserPromptSubmit') {
    emitContext('UserPromptSubmit', REMINDER);
    return;
  }
  if (event !== 'SessionStart') {
    return;
  }
  if (typeof payload.source === 'string' && SKIP_SOURCES.has(payload.source)) {
    return;
  }

  const root = pluginRoot({ argv: process.argv, startDir: SCRIPT_DIR });
  const path = rulesFile(root);
  if (!path) {
    emitContext(
      'SessionStart',
      `se-governance 章程未注入：插件包内未找到 rules/ 下的 ${RULES_FILENAME}。本会话须先读取章程；无法读取的，停止并报告安装缺失。`,
    );
    return;
  }

  let data;
  try {
    data = readFileSync(path);
  } catch (error) {
    const reason = error.code || error.message || '未知错误';
    emitContext(
      'SessionStart',
      `se-governance 章程未注入：读取 ${path} 失败（${reason}）。本会话须先读取章程；无法读取的，停止并报告。`,
    );
    return;
  }

  const digest = sha256(data);
  if (dedupeCandidates(payload).some((file) => fileMatches(file, digest))) {
    return;
  }
  if (data.length > MAX_BYTES) {
    emitContext('SessionStart', `se-governance 章程超过 64 KiB 硬上限，未直接注入；应当读取 ${path} 并在本会话遵守。`);
    return;
  }

  emitContext('SessionStart', `${TITLE}\n\n${data.toString('utf-8').trim()}`);
}

if (isMain(import.meta.url)) {
  await runHook(handle);
}
