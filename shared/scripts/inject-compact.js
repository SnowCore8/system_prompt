#!/usr/bin/env node
/**
 * SessionStart(source=compact) 钩子：压缩后注入约束提醒与当前时间。
 *
 * Qoder 1.1.90 的同步 PostCompact 输出不进入对话，压缩后的注入点是
 * SessionStart(source=compact)。这里只在该 source 触发时输出一句约束提醒和
 * 两行时间说明；不写状态、不写日志、不阻断压缩。
 */

import { emitContext, isMain, runHook } from './lib/hook.js';
import { currentTime, formatCompactText } from './lib/time.js';

/**
 * 处理一次压缩后注入 hook 调用。
 *
 * @param {Record<string, unknown>} payload
 */
async function handle(payload) {
  if (payload.hook_event_name !== 'SessionStart') {
    return;
  }
  if (payload.source !== 'compact') {
    return;
  }
  emitContext('SessionStart', formatCompactText(currentTime()));
}

if (isMain(import.meta.url)) {
  await runHook(handle);
}
