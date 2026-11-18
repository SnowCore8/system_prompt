#!/usr/bin/env python3
"""SessionStart 钩子：把用户全局约束与随包人格注入会话上下文。

正文来自插件包内的 rules/（Qwen 包为 constraints/）：global-user-constraints.md
与 persona.md。若用户级或项目级已经加载同内容的规则或 AGENTS.md，则跳过对应
文件，避免重复进入上下文。同时兼容 Qoder 插件与 Qwen Code 扩展：优先用宿主
注入的根目录环境变量，否则按脚本自身位置推导。解析与文件读取异常静默退出 0，
不阻断会话启动。
"""

import hashlib
import json
import os
import sys
from pathlib import Path

HOOK_EVENTS = {"SessionStart"}
RULES_FILENAME = "global-user-constraints.md"
PERSONA_FILENAME = "persona.md"
MAX_BYTES = 512 * 1024
# Qwen 会把扩展的 rules/ 当作条件规则扫描，无 paths 的常驻规则会被丢弃并告警；
# 所以 Qwen 包把正文放在 constraints/，Qoder 包继续用 rules/。
RULES_DIRS = ("constraints", "rules")
# 恢复会话时历史里已经有注入的正文，再注入一份只会膨胀上下文。
# clear/compact 会重建上下文，仍需要重新注入；startup 与 new 同理。
SKIP_SOURCES = {"resume"}


def plugin_root(argv: list[str]) -> Path:
    if len(argv) > 1 and argv[1]:
        return Path(argv[1])
    for name in ("QODER_PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT"):
        value = os.environ.get(name)
        if value:
            return Path(value)
    here = Path(__file__).resolve()
    names = (RULES_FILENAME, PERSONA_FILENAME)
    for parent in here.parents:
        if any((parent / directory / name).is_file()
               for directory in RULES_DIRS for name in names):
            return parent
    return here.parents[1]


def find_rule(root: Path, filename: str):
    for directory in RULES_DIRS:
        path = root / directory / filename
        if path.is_file():
            return path
    return None


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
    source = payload.get("source")
    if isinstance(source, str) and source in SKIP_SOURCES:
        return 0

    root = plugin_root(sys.argv)
    parts = []
    for filename, label, header in (
        (PERSONA_FILENAME, "表达人格", "表达人格（由插件随包注入，遵守全局约束）："),
        (RULES_FILENAME, "用户全局约束", "用户全局约束（由插件在会话启动时注入，必须遵守）："),
    ):
        path = find_rule(root, filename)
        if path is None:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        digest = hashlib.sha256(data).hexdigest()
        if any(has_same_content(candidate, digest) for candidate in candidate_files(payload)):
            continue
        if len(data) > MAX_BYTES:
            parts.append(f"{label}正文过大，未直接注入；请读取 {path} 并在本会话遵守。")
            continue
        text = data.decode("utf-8", "replace").strip()
        parts.append(f"{header}\n\n{text}")

    if parts:
        emit(event, "\n\n".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
