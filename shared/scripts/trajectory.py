#!/usr/bin/env python3
"""记录 Qoder 全事件操作轨迹，并在支持上下文的事件注入一行时间。

每个事件写入 `${QODER_PLUGIN_DATA}/trajectory/<session>.jsonl`，记录时间戳、事件名、
会话、工作目录、耗时和有限的事件元数据；不记录 prompt、tool_input、tool_response、
错误正文等可能含敏感内容的大字段。支持 additionalContext 的事件额外注入一行时间；
UserPromptSubmit 由 inject_clock.py 提供完整 DSH 三行时间块，本脚本只记日志避免重复。
控制事件的输出保持为空，不拦截、不修改、不自动决定权限。异常静默退出 0。
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

CONTEXT_EVENTS = {
    "SessionStart",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "SubagentStart",
    "PostModelSwitch",
    "Notification",
}
LOG_FIELDS = (
    "session_id",
    "cwd",
    "agent_id",
    "agent_type",
    "tool_name",
    "source",
    "trigger",
    "reason",
    "notification_type",
    "file_path",
    "worktree_path",
    "name",
    "mcp_server_name",
    "from_model",
    "to_model",
    "error_type",
    "task_id",
)


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


def stamp(now: datetime) -> str:
    offset = now.strftime("%z")
    if offset:
        offset = f"{offset[:3]}:{offset[3:]}"
    zone = timezone_name(now) or "UTC"
    return f"{now:%Y-%m-%dT%H:%M:%S}{offset}[{zone}]"


def format_duration(elapsed_ms: Optional[float]) -> str:
    if elapsed_ms is None:
        return "unavailable"
    seconds = max(0, int(elapsed_ms // 1000))
    return f"{seconds}s"


def state_paths(payload: dict) -> tuple[Optional[Path], Optional[Path]]:
    data_dir = os.environ.get("QODER_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    session_id = payload.get("session_id")
    if not data_dir or not isinstance(session_id, str) or not session_id:
        return None, None
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:32]
    root = Path(data_dir) / "trajectory"
    return root / f"{digest}.jsonl", root / f"{digest}.json"


def load_last(path: Optional[Path]) -> Optional[float]:
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("last")
    except (OSError, ValueError, AttributeError):
        return None
    return float(value) if isinstance(value, (int, float)) else None


def save_last(path: Optional[Path], last: float) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"last": last}), encoding="utf-8")
    except OSError:
        pass


def append_log(path: Optional[Path], record: dict) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def emit(event: str, text: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }
    }
    sys.stdout.buffer.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (ValueError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0
    event = payload.get("hook_event_name")
    if not isinstance(event, str) or not event:
        return 0

    now = datetime.now().astimezone()
    log_path, state_path = state_paths(payload)
    last = load_last(state_path)
    elapsed_ms = None if last is None else (now.timestamp() - last) * 1000
    timestamp = stamp(now)

    record = {
        "ts": timestamp,
        "event": event,
        "elapsed_ms": elapsed_ms,
        "elapsed": format_duration(elapsed_ms),
    }
    for key in LOG_FIELDS:
        value = payload.get(key)
        if isinstance(value, (str, int, float, bool)) or value is None:
            record[key] = value
    append_log(log_path, record)

    if event == "SessionEnd":
        try:
            if state_path is not None:
                state_path.unlink()
        except OSError:
            pass
    else:
        save_last(state_path, now.timestamp())

    if event in CONTEXT_EVENTS:
        emit(
            event,
            f"Time sampled at {event}: {timestamp}; "
            f"elapsed since previous trajectory event: {format_duration(elapsed_ms)}.",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
