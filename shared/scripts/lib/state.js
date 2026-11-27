/**
 * 时间 hook 的会话状态：按 session 记录 turn 与上次注入时间。
 *
 * 状态文件位于宿主提供的插件数据目录；没有数据目录或 session_id 时返回 null，
 * 调用方据此退化为无状态模式（turn 1、elapsed unavailable）。读写失败一律吞掉。
 */

import { mkdirSync, readFileSync, unlinkSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { sha256 } from './paths.js';

/**
 * 创建会话状态句柄。
 *
 * @param {{ dataDir?: string, sessionId?: unknown, namespace?: string }} options
 * @returns {{ path: string, load: () => ({ turn: number, last: number } | null), save: (turn: number, last: number) => void, clear: () => void } | null}
 */
export function createClockState({ dataDir, sessionId, namespace = 'clock' }) {
  if (!dataDir || typeof sessionId !== 'string' || !sessionId) {
    return null;
  }

  const digest = sha256(sessionId).slice(0, 32);
  const path = join(dataDir, namespace, `${digest}.json`);

  return {
    path,

    load() {
      try {
        const data = JSON.parse(readFileSync(path, 'utf-8'));
        const turn = data.turn;
        const last = data.last;
        if (typeof turn !== 'number' || turn < 1 || typeof last !== 'number') {
          return null;
        }
        return { turn, last };
      } catch {
        return null;
      }
    },

    save(turn, last) {
      try {
        mkdirSync(dirname(path), { recursive: true });
        writeFileSync(path, JSON.stringify({ turn, last }), 'utf-8');
      } catch {
        // 忽略：无法写状态时退化为无状态
      }
    },

    clear() {
      try {
        unlinkSync(path);
      } catch {
        // 忽略：状态本来就不存在
      }
    },
  };
}
