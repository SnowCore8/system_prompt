/**
 * 时间格式化：DSH 三行时间块、工具事件一行时间、压缩后提醒。
 *
 * 时区依次取 TZ（经 Intl 校验）、Intl 系统时区、/etc/timezone，最后用 UTC 整点偏移兜底。
 */

import { readFileSync } from 'node:fs';

/** @returns {Date} */
export function currentTime() {
  return new Date();
}

/**
 * 解析当前请求应使用的时区名。
 *
 * @param {Date} now
 * @returns {string}
 */
export function timezoneName(now) {
  const tz = (process.env.TZ || '').trim().replace(/^:/, '');
  if (tz) {
    try {
      const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: tz,
        timeZoneName: 'longOffset',
      });
      // 无效时区会在此抛异常
      formatter.format(now);
      return tz;
    } catch {
      // 无效时区，继续尝试其他方式
    }
  }

  try {
    const resolved = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (resolved) {
      return resolved;
    }
  } catch {
    // 忽略
  }

  try {
    const etcTimezone = readFileSync('/etc/timezone', 'utf-8').trim();
    if (etcTimezone) {
      return etcTimezone;
    }
  } catch {
    // 忽略
  }

  const offset = -now.getTimezoneOffset();
  if (offset === 0) {
    return 'UTC';
  }
  const sign = offset >= 0 ? '+' : '-';
  const absHours = Math.floor(Math.abs(offset) / 60);
  return `UTC${sign}${absHours}`;
}

/**
 * 把毫秒耗时格式化为 `1d 2h 3m 4s` 形式。
 *
 * @param {number} elapsedMs
 * @returns {string}
 */
export function formatDuration(elapsedMs) {
  const totalSeconds = Math.max(0, Math.floor(elapsedMs / 1000));
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const parts = [];
  if (days > 0) {
    parts.push(`${days}d`);
  }
  if (hours > 0) {
    parts.push(`${hours}h`);
  }
  if (minutes > 0) {
    parts.push(`${minutes}m`);
  }
  parts.push(`${seconds}s`);
  return parts.join(' ');
}

/**
 * 生成带数值偏移与 IANA 时区的 ISO 风格时间戳。
 *
 * @param {Date} now
 * @returns {string}
 */
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

/**
 * 用户提示的三行时间块。
 *
 * @param {{ now: Date, turn: number, last: number | null }} options
 * @returns {string}
 */
export function formatUserTime({ now, turn, last }) {
  const zone = timezoneName(now) || 'UTC';
  const stamp = formatTimestamp(now);
  const elapsed = typeof last === 'number' ? formatDuration(now.getTime() - last) : 'unavailable';

  return [
    `Time sampled while preparing turn ${turn}: ${stamp}`,
    `Browser time zone for this request: ${zone}. Interpret otherwise-unqualified dates and times in this zone.`,
    `Elapsed since the preceding model-visible message: ${elapsed}.`,
  ].join('\n');
}

/**
 * 工具事件的一行时间。
 *
 * @param {{ event: string, tool?: unknown, now: Date }} options
 * @returns {string}
 */
export function formatToolTime({ event, tool, now }) {
  const suffix = typeof tool === 'string' && tool ? ` (${tool})` : '';
  return `Time sampled at ${event}${suffix}: ${formatTimestamp(now)}.`;
}

/**
 * 压缩后的提醒与时间。
 *
 * @param {Date} now
 * @returns {string}
 */
export function formatCompactText(now) {
  const zone = timezoneName(now) || 'UTC';
  const stamp = formatTimestamp(now);

  return [
    'Never violate the se-governance charter.',
    '',
    `Time sampled after context compaction: ${stamp}.`,
    `Browser time zone for this request: ${zone}. Interpret otherwise-unqualified dates and times in this zone.`,
  ].join('\n');
}
