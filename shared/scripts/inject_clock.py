#!/usr/bin/env python3
"""在会话启动与每次提示提交时注入当前本地时间，并在会话结束时清理状态。

Qoder 与 Qwen Code 都没有内建时间感知；这个钩子采用 DSH time-context 的三行格式：
轮次/步骤、带数值偏移与 IANA 时区的 ISO 时间戳、请求时区解释规则、距上一可见消息的耗时。
Qoder hook 没有 turn/step/elapsed 字段：用插件数据目录按 session 记录 turn 与上次注入时间，
step 固定为 1；没有可用状态时输出 turn 1、step 1、elapsed unavailable。任何异常静默退出 0。
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

HOOK_EVENTS = {"SessionStart", "UserPromptSubmit", "SessionEnd"}


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


def format_duration(elapsed_ms: float) -> str:
    seconds = max(0, int(elapsed_ms // 1000))
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def state_path(payload: dict) -> Optional[Path]:
    data_dir = os.environ.get("QODER_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    session_id = payload.get("session_id")
    if not data_dir or not isinstance(session_id, str) or not session_id:
        return None
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:32]
    return Path(data_dir) / "clock" / f"{digest}.json"


def load_state(path: Optional[Path]) -> Optional[tuple[int, float]]:
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        turn = data.get("turn")
        last = data.get("last")
    except (OSError, ValueError, AttributeError):
        return None
    if not isinstance(turn, int) or turn < 1 or not isinstance(last, (int, float)):
        return None
    return turn, float(last)


def save_state(path: Optional[Path], turn: int, last: float) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"turn": turn, "last": last}), encoding="utf-8")
    except OSError:
        pass


def cleanup_state(path: Optional[Path]) -> None:
    if path is None:
        return
    try:
        path.unlink()
    except OSError:
        pass


def describe(now: datetime, event: str, previous: Optional[tuple[int, float]]) -> tuple[str, int]:
    offset = now.strftime("%z")
    if offset:
        offset = f"{offset[:3]}:{offset[3:]}"
    zone = timezone_name(now) or "UTC"
    stamp = f"{now:%Y-%m-%dT%H:%M:%S}{offset}[{zone}]"
    if event == "SessionStart":
        turn = 1
        last = None
    elif previous is None:
        turn = 1
        last = None
    else:
        turn = previous[0] + 1
        last = previous[1]
    step = 1
    baseline = "model-visible message" if step == 1 else "step context"
    elapsed = "unavailable" if last is None else format_duration((now.timestamp() - last) * 1000)
    text = (
        f"Time sampled while preparing turn {turn}, step {step}: {stamp}\n"
        f"Browser time zone for this request: {zone}. "
        "Interpret otherwise-unqualified dates and times in this zone.\n"
        f"Elapsed since the preceding {baseline}: {elapsed}."
    )
    return text, turn


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
    if event == "SessionEnd":
        cleanup_state(state_path(payload))
        return 0

    now = datetime.now().astimezone()
    path = state_path(payload)
    text, turn = describe(now, event, load_state(path))
    save_state(path, turn, now.timestamp())
    output = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }
    }
    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
