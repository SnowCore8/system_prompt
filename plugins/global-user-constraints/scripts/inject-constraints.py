#!/usr/bin/env python3
"""SessionStart 钩子：把用户全局约束全文注入会话上下文。

约束正文来自插件包内的 rules/global-user-constraints.md。若用户级或项目级
已经加载同内容的规则或 AGENTS.md，则跳过注入，避免同一份约束重复进入上下文。
同时兼容 Qoder 插件与 Qwen Code 扩展：优先用宿主注入的根目录环境变量，
否则按脚本自身位置推导。任何异常都静默退出 0，不阻断会话启动。
"""

import hashlib
import json
import os
import sys
from pathlib import Path

HOOK_EVENTS = {"SessionStart"}
RULES_FILENAME = "global-user-constraints.md"
MAX_BYTES = 512 * 1024


def plugin_root() -> Path:
    for name in ("QODER_PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT"):
        value = os.environ.get(name)
        if value:
            return Path(value)
    return Path(__file__).resolve().parents[1]


def config_roots() -> list[Path]:
    roots: list[Path] = []
    for name in ("QODERCN_CONFIG_DIR", "QODER_CONFIG_DIR", "QWEN_HOME", "QWEN_CONFIG_DIR"):
        value = os.environ.get(name)
        if value:
            roots.append(Path(value))
    home = Path(os.environ.get("HOME") or Path.home())
    roots.extend([home / ".qoder-cn", home / ".qoder", home / ".qwen"])
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
        candidates.append(root / "QWEN.md")
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    for directory in project_dirs(cwd):
        candidates.append(directory / ".qoder" / "rules" / RULES_FILENAME)
        candidates.append(directory / ".qwen" / "rules" / RULES_FILENAME)
        candidates.append(directory / "AGENTS.md")
        candidates.append(directory / "AGENTS.local.md")
        candidates.append(directory / "QWEN.md")
        candidates.append(directory / "QWEN.local.md")
    return candidates


def has_same_content(path: Path, digest: str) -> bool:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest() == digest
    except OSError:
        return False


def emit(event: str, additional_context: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": additional_context,
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
    if event not in HOOK_EVENTS:
        return 0

    rules_path = plugin_root() / "rules" / RULES_FILENAME
    try:
        data = rules_path.read_bytes()
    except OSError:
        return 0

    digest = hashlib.sha256(data).hexdigest()
    if any(has_same_content(path, digest) for path in candidate_files(payload)):
        return 0

    if len(data) > MAX_BYTES:
        emit(event, f"用户全局约束正文过大，未直接注入；请读取 {rules_path} 并在本会话遵守。")
        return 0

    text = data.decode("utf-8", "replace").strip()
    emit(event, f"用户全局约束（由插件在会话启动时注入，必须遵守）：\n\n{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
