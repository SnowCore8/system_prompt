#!/usr/bin/env python3
"""在会话启动与每次提示提交时注入当前本地时间。

Qoder 与 Qwen Code 都没有内建时间感知；这个钩子把「当前时间 + UTC 偏移 +
时区名 + 星期」作为一行 additionalContext 注入，让模型在处理日期、排期、
日志与跨天任务时有可依据的时间。任何异常都静默退出 0。
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

HOOK_EVENTS = {"SessionStart", "UserPromptSubmit"}
WEEKDAYS = "一二三四五六日"


def timezone_name(now: datetime) -> str:
    tz = os.environ.get("TZ", "").strip().lstrip(":")
    if tz:
        return tz
    try:
        name = Path("/etc/timezone").read_text(encoding="utf-8").strip()
    except OSError:
        name = ""
    if name:
        return name
    try:
        resolved = Path("/etc/localtime").resolve()
        parts = resolved.parts
        if "zoneinfo" in parts:
            return "/".join(parts[parts.index("zoneinfo") + 1 :])
    except OSError:
        pass
    return now.tzname() or ""


def describe(now: datetime) -> str:
    offset = now.strftime("%z")
    if offset:
        offset = f"{offset[:3]}:{offset[3:]}"
    zone = timezone_name(now)
    zone_part = f"{zone}，" if zone else ""
    return (
        f"当前时间：{now:%Y-%m-%d %H:%M:%S} {offset}（{zone_part}星期{WEEKDAYS[now.weekday()]}）。"
        "涉及日期或时间事项的，应当以此为准；长会话应当以最近一次注入为准。"
    )


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (ValueError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0
    event = payload.get("hook_event_name")
    if event not in HOOK_EVENTS:
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": describe(datetime.now().astimezone()),
        }
    }
    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
