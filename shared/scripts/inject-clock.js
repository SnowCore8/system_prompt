#!/usr/bin/env node
/**
 * 注入当前本地时间；用户提示用完整 DSH 三行块，工具事件用一行时间。
 *
 * Qoder 通过 QODER_PLUGIN_DATA 按 session 记录 turn 与上次注入时间，
 * Qwen 不提供插件数据目录，因此不写盘，turn 固定为 1、elapsed 为 unavailable。
 * 工具事件只发一行时间、不读写状态；SessionEnd 清理状态。任何异常静默退出 0。
 */

import { emitContext, isMain, runHook } from './lib/hook.js';
import { createClockState } from './lib/state.js';
import { currentTime, formatToolTime, formatUserTime } from './lib/time.js';

const HOOK_EVENTS = new Set([
  'SessionStart', 'UserPromptSubmit', 'SessionEnd',
  'PreToolUse', 'PostToolUse', 'PostToolUseFailure',
]);
const TOOL_EVENTS = new Set(['PreToolUse', 'PostToolUse', 'PostToolUseFailure']);

/**
 * 创建当前 payload 对应的时钟状态。
 * 没有 QODER_PLUGIN_DATA 或 session_id 时返回 null，即无状态模式。
 *
 * @param {Record<string, unknown>} payload
 */
function stateFor(payload) {
  return createClockState({
    dataDir: process.env.QODER_PLUGIN_DATA,
    sessionId: payload.session_id,
    namespace: 'clock',
  });
}

/**
 * 处理一次时间注入 hook 调用。
 *
 * @param {Record<string, unknown>} payload
 */
async function handle(payload) {
  const event = payload.hook_event_name;
  if (!HOOK_EVENTS.has(event)) {
    return;
  }

  const state = stateFor(payload);
  if (event === 'SessionEnd') {
    state?.clear();
    return;
  }

  const now = currentTime();

  if (TOOL_EVENTS.has(event)) {
    emitContext(event, formatToolTime({ event, tool: payload.tool_name, now }));
    return;
  }

  const previous = state?.load() ?? null;
  const turn = event === 'SessionStart' || previous === null ? 1 : previous.turn + 1;
  const last = turn === 1 ? null : previous.last;
  state?.save(turn, now.getTime());
  emitContext(event, formatUserTime({ now, turn, last }));
}

if (isMain(import.meta.url)) {
  await runHook(handle);
}
