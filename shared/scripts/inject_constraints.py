#!/usr/bin/env python3
"""Qoder/Qwen 约束注入钩子：在原生 rules 未覆盖时注入全文或固定提醒。

SessionStart 在用户级或项目级已有同内容规则/AGENTS.md 时跳过，仅在未安装时注入全文；
Qoder 的规则正文由 SessionStart 安装到用户级 rules，本脚本只负责每轮固定提醒。
UserPromptSubmit 只发送一句固定提醒。正文超过 40 KiB 硬上限时不注入全文，只提示读取
原文。同时兼容 Qoder 插件与 Qwen Code 扩展：优先用宿主注入的根目录环境变量，否则按
脚本自身位置推导。异常静默退出 0，不阻断会话。
"""

import hashlib
import json
import os
import sys
from pathlib import Path

HOOK_EVENTS = {"SessionStart", "UserPromptSubmit"}
RULES_FILENAME = "global-user-constraints.md"
MAX_BYTES = 40 * 1024
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
    for parent in here.parents:
        if (parent / "rules" / RULES_FILENAME).is_file():
            return parent
    return here.parents[1]


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
    if event == "UserPromptSubmit":
        emit(event, "Never violate global user constraints.")
        return 0
    source = payload.get("source")
    if isinstance(source, str) and source in SKIP_SOURCES:
        return 0

    root = plugin_root(sys.argv)
    rules_path = next(
        (root / directory / RULES_FILENAME for directory in RULES_DIRS
         if (root / directory / RULES_FILENAME).is_file()),
        None,
    )
    if rules_path is None:
        emit(event, "全局用户约束未注入：插件包内未找到 rules/ 或 constraints/ 下的 global-user-constraints.md。"
             "本会话须先读取约束；无法读取的，停止并报告安装缺失。")
        return 0
    try:
        data = rules_path.read_bytes()
    except OSError as error:
        emit(event, f"全局用户约束未注入：读取 {rules_path} 失败（{error.strerror or error}）。"
             "本会话须先读取约束；无法读取的，停止并报告。")
        return 0

    digest = hashlib.sha256(data).hexdigest()
    if any(has_same_content(path, digest) for path in candidate_files(payload)):
        return 0

    if len(data) > MAX_BYTES:
        emit(event, f"全局用户约束正文超过 40 KiB 硬上限，未直接注入；应当读取 {rules_path} 并在本会话遵守。")
        return 0

    text = data.decode("utf-8", "replace").strip()
    emit(event, f"全局用户约束（由插件于会话启动时注入，必须遵守）：\n\n{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
