#!/usr/bin/env node
/**
 * SessionStart(source=compact) 钩子：压缩后注入约束提醒与当前时间。
 *
 * Qoder 1.1.90 的同步 PostCompact 输出不进入对话，压缩后的注入点是
 * SessionStart(source=compact)。这里只在该 source 触发时输出一句约束提醒和
 * 一行时间 + 时区解释；不写状态、不写日志、不阻断压缩。
 */

import { currentTime, timezoneName, formatTimestamp } from './inject-clock.js';

async function readStdin() {
  return new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => chunks.push(chunk));
    process.stdin.on('end', () => resolve(chunks.join('')));
    process.stdin.on('error', reject);
  });
}

async function main() {
  try {
    const raw = await readStdin();
    const payload = JSON.parse(raw);
    if (typeof payload !== 'object' || payload === null) return 0;
    if (payload.hook_event_name !== 'SessionStart') return 0;
    if (payload.source !== 'compact') return 0;

    const now = currentTime();
    const zone = timezoneName(now) || 'UTC';
    const stamp = formatTimestamp(now);

    const text = [
      'Never violate global user constraints.',
      '',
      `Time sampled after context compaction: ${stamp}.`,
      `Browser time zone for this request: ${zone}. Interpret otherwise-unqualified dates and times in this zone.`,
    ].join('\n');

    const output = {
      hookSpecificOutput: {
        hookEventName: 'SessionStart',
        additionalContext: text,
      },
    };

    process.stdout.write(JSON.stringify(output) + '\n');
    return 0;
  } catch {
    return 0;
  }
}

main().then(code => process.exit(code));
