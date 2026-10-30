#!/usr/bin/env python3
"""Inject local time, and the always-on rules at session or subagent start."""

import json
import sys
from datetime import datetime
from pathlib import Path

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
RULES_EVENTS = {"SessionStart", "SubagentStart"}
RULES_FILE = Path(__file__).resolve().parent.parent / "rules" / "global-user-constraints.md"
RULES_HEADER = "全局用户约束（必须遵守）："


def local_timestamp() -> str:
    now = datetime.now().astimezone()
    offset = now.strftime("%z")
    if offset:
        offset = f"{offset[:3]}:{offset[3:]}"
    return f"{now:%Y-%m-%d %H:%M:%S} {offset}".rstrip()


def rules_body() -> str:
    try:
        text = RULES_FILE.read_text(encoding="utf-8")
    except OSError:
        return ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return text.strip()


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

    context = f"当前时间：{local_timestamp()}"
    if event in RULES_EVENTS:
        body = rules_body()
        if body:
            context = f"{context}\n\n{RULES_HEADER}\n\n{body}"

    output = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": context,
        }
    }
    json.dump(output, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
