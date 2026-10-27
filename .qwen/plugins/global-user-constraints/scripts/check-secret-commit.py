#!/usr/bin/env python3
"""Block obvious secret commits before git commit runs."""

import json
import re
import subprocess
import sys

SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Stripe secret key", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("password assignment", re.compile(r"\b(?:password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}", re.IGNORECASE)),
    ("secret assignment", re.compile(r"\b(?:api[_-]?key|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}", re.IGNORECASE)),
]


def git_diff(args: list[str], cwd: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return proc.stdout if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError, ValueError):
        return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    parts = [tool_input.get("command"), tool_input.get("cmd"), payload.get("command")]
    command = "\n".join(str(part) for part in parts if part)
    if not re.search(r"\bgit\b[\s\S]{0,120}\bcommit\b", command):
        return 0

    cwd = payload.get("cwd") or "."
    text = command
    text += "\n" + git_diff(["diff", "--cached", "--no-color", "--unified=0"], cwd)
    if re.search(r"\s-(?:a|am|all)\b", command):
        text += "\n" + git_diff(["diff", "--no-color", "--unified=0"], cwd)

    hits = [name for name, pattern in SECRET_PATTERNS if pattern.search(text)]
    if not hits:
        return 0

    reason = [
        "该提交可能包含 secret，已阻止执行：",
        *[f"- 疑似 {name}" for name in hits],
        "请移除 secret、改用环境变量或 secret 管理器，并重新提交。公开 key 与 publishable key 不在此拦截范围。",
    ]
    print("\n".join(reason), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
