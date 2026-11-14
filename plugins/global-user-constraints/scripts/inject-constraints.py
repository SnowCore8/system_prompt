#!/usr/bin/env python3
"""SessionStart 钩子：把用户全局约束全文注入会话上下文。

约束正文来自插件包内的 rules/global-user-constraints.md。若用户级或项目级
已经加载同内容的规则或 AGENTS.md，则跳过注入，避免同一份约束重复进入上下文。
任何异常都静默退出 0，不阻断会话启动。
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

HOOK_EVENT = "SessionStart"
RULES_FILENAME = "global-user-constraints.md"
MAX_BYTES = 512 * 1024


def local_timestamp() -> str:
    now = datetime.now().astimezone()
    offset = now.strftime("%z")
    if offset:
        offset = f"{offset[:3]}:{offset[3:]}"
    return f"{now:%Y-%m-%d %H:%M:%S} {offset}".rstrip()


def config_roots() -> list[Path]:
    roots: list[Path] = []
    for name in ("QODERCN_CONFIG_DIR", "QODER_CONFIG_DIR"):
        value = os.environ.get(name)
        if value:
            roots.append(Path(value))
    home = Path(os.environ.get("HOME") or Path.home())
    roots.extend([home / ".qoder-cn", home / ".qoder"])
    return roots


def project_dirs(cwd: str) -> list[Path]:
    try:
        start = Path(cwd).resolve()
    except OSError:
        return []
    dirs = []
    for path in [start, *start.parents]:
        dirs.append(path)
        if (path / ".git").exists():
            break
    return dirs


def candidate_files(payload: dict) -> list[Path]:
    candidates = []
    for root in config_roots():
        candidates.append(root / "rules" / RULES_FILENAME)
        candidates.append(root / "AGENTS.md")
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        for directory in project_dirs(cwd):
            candidates.append(directory / ".qoder" / "rules" / RULES_FILENAME)
            candidates.append(directory / "AGENTS.md")
            candidates.append(directory / "AGENTS.local.md")
    return candidates


def has_same_content(path: Path, digest: str) -> bool:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest() == digest
    except OSError:
        return False


def emit(additional_context: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": HOOK_EVENT,
            "additionalContext": additional_context,
        }
    }
    sys.stdout.buffer.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()


def main() -> int:
    try:
        raw = sys.stdin.buffer.read()
        payload = json.loads(raw.decode("utf-8", "replace"))
    except (ValueError, OSError):
        return 0
    if not isinstance(payload, dict) or payload.get("hook_event_name") != HOOK_EVENT:
        return 0

    plugin_root = os.environ.get("QODER_PLUGIN_ROOT")
    if not plugin_root:
        return 0
    rules_path = Path(plugin_root) / "rules" / RULES_FILENAME
    try:
        data = rules_path.read_bytes()
    except OSError:
        return 0

    digest = hashlib.sha256(data).hexdigest()
    if any(has_same_content(path, digest) for path in candidate_files(payload)):
        return 0

    if len(data) > MAX_BYTES:
        emit(
            "用户全局约束正文过大，未直接注入；请读取 "
            f"{rules_path} 并在本会话遵守。"
        )
        return 0

    text = data.decode("utf-8", "replace").strip()
    emit(
        f"用户全局约束（由插件在会话启动时注入，{local_timestamp()}）：\n\n"
        f"{text}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
