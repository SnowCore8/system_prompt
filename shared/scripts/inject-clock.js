#!/usr/bin/env node
/**
 * 注入当前本地时间；用户提示用完整 DSH 三行块，工具事件用一行时间。
 *
 * Qoder 与 Qwen Code 都没有内建时间感知；用户提示采用 DSH time-context 的三行格式：
 * 轮次/步骤、带数值偏移与 IANA 时区的 ISO 时间戳、请求时区解释规则、距上一可见消息的耗时。
 * Qoder hook 没有逐步 step 与 elapsed 字段：用插件数据目录按 session 记录 turn 与上次
 * 注入时间，没有可用状态时输出 turn 1、elapsed unavailable。Pre/PostToolUse 只发一行
 * 时间，避免每步注入完整三行。任何异常静默退出 0。
 */

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, unlinkSync, existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const HOOK_EVENTS = new Set([
  'SessionStart', 'UserPromptSubmit', 'SessionEnd',
  'PreToolUse', 'PostToolUse', 'PostToolUseFailure',
]);
const TOOL_EVENTS = new Set(['PreToolUse', 'PostToolUse', 'PostToolUseFailure']);

export function currentTime() {
  return new Date();
}

export function timezoneName(now) {
  const tz = (process.env.TZ || '').trim().replace(/^:/, '');
  if (tz) {
    try {
      const testDate = new Date();
      const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: tz,
        timeZoneName: 'longOffset',
      });
      // 验证时区是否有效：如果无效会抛异常
      formatter.format(testDate);
      return tz;
    } catch {
      // 无效时区，继续尝试其他方式
    }
  }

  // 尝试从 Intl API 获取
  try {
    const resolved = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (resolved) return resolved;
  } catch {
    // 忽略
  }

  // 尝试读取系统时区文件
  try {
    const etcTimezone = readFileSync('/etc/timezone', 'utf-8').trim();
    if (etcTimezone) return etcTimezone;
  } catch {
    // 忽略
  }

  try {
    const realpath = readFileSync('/etc/localtime', 'utf-8');
    // 尝试从路径中提取 zoneinfo 之后的部分
    // 这个方法在 Node.js 中不太可靠，作为最后手段
  } catch {
    // 忽略
  }

  // 最后使用 UTC 偏移量
  const offset = -now.getTimezoneOffset();
  if (offset === 0) return 'UTC';
  const sign = offset >= 0 ? '+' : '-';
  const absHours = Math.floor(Math.abs(offset) / 60);
  return `UTC${sign}${absHours}`;
}

export function formatDuration(elapsedMs) {
  const totalSeconds = Math.max(0, Math.floor(elapsedMs / 1000));
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  parts.push(`${seconds}s`);

  return parts.join(' ');
}

export function formatTimestamp(now) {
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const secs = String(now.getSeconds()).padStart(2, '0');
  const ms = String(now.getMilliseconds()).padStart(3, '0');

  const offsetMinutes = -now.getTimezoneOffset();
  const sign = offsetMinutes >= 0 ? '+' : '-';
  const absOffset = Math.abs(offsetMinutes);
  const offH = String(Math.floor(absOffset / 60)).padStart(2, '0');
  const offM = String(absOffset % 60).padStart(2, '0');
  const offset = `${sign}${offH}:${offM}`;

  const zone = timezoneName(now) || 'UTC';
  return `${year}-${month}-${day}T${hours}:${minutes}:${secs}.${ms}${offset}[${zone}]`;
}

function statePath(payload) {
  const dataDir = process.env.QODER_PLUGIN_DATA || process.env.CLAUDE_PLUGIN_DATA;
  const sessionId = payload.session_id;
  if (!dataDir || typeof sessionId !== 'string' || !sessionId) {
    return null;
  }
  const digest = createHash('sha256').update(sessionId, 'utf-8').digest('hex').slice(0, 32);
  return join(dataDir, 'clock', `${digest}.json`);
}

function loadState(path) {
  if (!path) return null;
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
}

function saveState(path, turn, last) {
  if (!path) return;
  try {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, JSON.stringify({ turn, last }), 'utf-8');
  } catch {
    // 忽略
  }
}

function cleanupState(path) {
  if (!path) return;
  try {
    unlinkSync(path);
  } catch {
    // 忽略
  }
}

function describe(now, event, previous) {
  const zone = timezoneName(now) || 'UTC';
  const stamp = formatTimestamp(now);

  let turn;
  let last;

  if (event === 'SessionStart' || previous === null) {
    turn = 1;
    last = null;
  } else {
    turn = previous.turn + 1;
    last = previous.last;
  }

  const elapsed = last === null
    ? 'unavailable'
    : formatDuration(now.getTime() - last);

  const text = [
    `Time sampled while preparing turn ${turn}: ${stamp}`,
    `Browser time zone for this request: ${zone}. Interpret otherwise-unqualified dates and times in this zone.`,
    `Elapsed since the preceding model-visible message: ${elapsed}.`,
  ].join('\n');

  return { text, turn };
}

async function readStdin() {
  return new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => chunks.push(chunk));
    process.stdin.on('end', () => resolve(chunks.join('')));
    process.stdin.on('error', reject);
  });
}

function emitOutput(event, additionalContext) {
  const output = {
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext,
    },
  };
  process.stdout.write(JSON.stringify(output) + '\n');
}

export async function main() {
  try {
    const raw = await readStdin();
    const payload = JSON.parse(raw);
    if (typeof payload !== 'object' || payload === null) return 0;

    const event = payload.hook_event_name;
    if (!HOOK_EVENTS.has(event)) return 0;

    if (event === 'SessionEnd') {
      cleanupState(statePath(payload));
      return 0;
    }

    const now = currentTime();

    if (TOOL_EVENTS.has(event)) {
      const tool = payload.tool_name;
      const suffix = typeof tool === 'string' && tool ? ` (${tool})` : '';
      emitOutput(event, `Time sampled at ${event}${suffix}: ${formatTimestamp(now)}.`);
      return 0;
    }

    const sp = statePath(payload);
    const previous = loadState(sp);
    const { text, turn } = describe(now, event, previous);
    saveState(sp, turn, now.getTime());

    emitOutput(event, text);
    return 0;
  } catch {
    return 0;
  }
}

// 仅当直接执行时运行
const isMain = process.argv[1] && (
  process.argv[1].endsWith('inject-clock.js') ||
  process.argv[1] === fileURLToPath(import.meta.url)
);
if (isMain) {
  main().then(code => process.exit(code));
}
