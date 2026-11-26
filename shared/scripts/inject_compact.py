#!/usr/bin/env python3
"""SessionStart(source=compact) 钩子：压缩后注入约束提醒与当前时间。

Qoder 的 PostCompact 不提供 additionalContext，压缩后的可注入事件是
SessionStart(source=compact)。这里只在该 source 触发时输出一句约束提醒和
一行时间 + 时区解释；不写状态、不写日志、不阻断压缩。
"""

import json
import sys

from inject_clock import current_time, timestamp, timezone_name


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (ValueError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0
    if payload.get("hook_event_name") != "SessionStart":
        return 0
    if payload.get("source") != "compact":
        return 0

    now = current_time()
    zone = timezone_name(now) or "UTC"
    text = (
        "Never violate global user constraints.\n\n"
        f"Time sampled after context compaction: {timestamp(now)}.\n"
        f"Browser time zone for this request: {zone}. "
        "Interpret otherwise-unqualified dates and times in this zone."
    )
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        }
    }
    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
