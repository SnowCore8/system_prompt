#!/usr/bin/env python3
"""Inject the current local time into supported Qoder hook events."""

import json
import sys
from datetime import datetime

SUPPORTED_EVENTS = {
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "SubagentStart",
    "Notification",
    "CwdChanged",
    "FileChanged",
}


def local_timestamp() -> str:
    now = datetime.now().astimezone()
    offset = now.strftime("%z")
    if offset:
        offset = f"{offset[:3]}:{offset[3:]}"
    return f"{now:%Y-%m-%d %H:%M:%S} {offset}".rstrip()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    event = payload.get("hook_event_name")
    if event not in SUPPORTED_EVENTS:
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": f"当前时间：{local_timestamp()}",
        }
    }
    json.dump(output, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
