/**
 * hook 运行时：读取 stdin、解析 payload、输出 hookSpecificOutput。
 *
 * 三个注入脚本共用同一套输入输出契约；所有失败都静默处理，退出码保持 0，
 * 不阻断宿主会话。这里不使用 process.exit，避免截断尚未刷出的 stdout。
 */

import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * 读取 stdin 上的 JSON payload。
 * 读取、解析失败或结果不是普通对象时返回 null。
 *
 * @returns {Promise<Record<string, unknown> | null>}
 */
export async function readPayload() {
  try {
    const chunks = [];
    for await (const chunk of process.stdin) {
      chunks.push(typeof chunk === 'string' ? Buffer.from(chunk) : chunk);
    }
    const payload = JSON.parse(Buffer.concat(chunks).toString('utf-8'));
    if (typeof payload !== 'object' || payload === null || Array.isArray(payload)) {
      return null;
    }
    return payload;
  } catch {
    return null;
  }
}

/**
 * 按宿主契约输出 additionalContext。
 * JSON 会转义换行，解析后的字符串仍保留原始换行。
 *
 * @param {string} event
 * @param {string} text
 */
export function emitContext(event, text) {
  const output = {
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext: text,
    },
  };
  process.stdout.write(JSON.stringify(output) + '\n');
}

/**
 * 读取 payload 并执行 handler。
 * 任何异常都静默吞掉；退出码固定为 0，由 Node 在 stdout 刷出后自然退出。
 *
 * @param {(payload: Record<string, unknown>) => void | Promise<void>} handler
 * @returns {Promise<void>}
 */
export async function runHook(handler) {
  try {
    const payload = await readPayload();
    if (payload === null) {
      return;
    }
    await handler(payload);
  } catch {
    // 静默：hook 失败不应阻断会话
  } finally {
    process.exitCode = 0;
  }
}

/**
 * 判断当前模块是否被直接执行（而非被测试或脚本导入）。
 *
 * @param {string} metaUrl
 * @returns {boolean}
 */
export function isMain(metaUrl) {
  const entry = process.argv[1];
  if (!entry) {
    return false;
  }
  try {
    return resolve(entry) === fileURLToPath(metaUrl);
  } catch {
    return false;
  }
}
