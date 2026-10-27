#!/usr/bin/env python3
"""Block obvious secret commits before git commit runs."""

import json
import os
import re
import shlex
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

# Commands that may precede git without changing which program runs.
WRAPPERS = {
    "command": set(),
    "time": set(),
    "nohup": set(),
    "builtin": set(),
    "sudo": {"-u", "-g", "-C", "-h", "-p", "-r", "-t", "-U", "-T", "-R", "-D"},
    "doas": {"-u", "-C"},
    "env": {"-u", "-C", "-S"},
    "nice": {"-n"},
    "exec": {"-a"},
}

ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
GIT_OPTS_WITH_ARG = {"-C", "-c"}
SHELL_BREAKS = set(";&|()")

# Short options of git commit that consume the rest of their cluster.
COMMIT_OPTS_WITH_VALUE = set("mFCct")
COMMIT_OPTS_WITH_OPTIONAL_VALUE = set("Su")


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


def tokenize(line: str) -> list[str]:
    try:
        lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return line.split()


def split_segments(tokens: list[str]):
    segment: list[str] = []
    for token in tokens:
        if token and all(char in SHELL_BREAKS for char in token):
            if segment:
                yield segment
            segment = []
            continue
        segment.append(token)
    if segment:
        yield segment


def git_index(tokens: list[str]):
    """Return the index of the git program token after env assignments and wrappers."""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if ENV_ASSIGN_RE.match(token):
            index += 1
            continue
        base = os.path.basename(token)
        if base == "git":
            return index
        if base not in WRAPPERS:
            return None
        args_with_value = WRAPPERS[base]
        index += 1
        while index < len(tokens) and tokens[index].startswith("-"):
            option = tokens[index].split("=", 1)[0]
            takes_value = "=" not in tokens[index] and option in args_with_value
            index += 2 if takes_value else 1
    return None


def git_subcommand(args: list[str]):
    index = 0
    while index < len(args):
        token = args[index]
        if token in GIT_OPTS_WITH_ARG:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token, args[index + 1 :]
    return None, []


def is_help_or_dry_run(args: list[str]) -> bool:
    return any(arg in {"--help", "--dry-run", "-h"} for arg in args)


def includes_all(args: list[str]) -> bool:
    for arg in args:
        if arg == "--":
            break
        if arg == "--all":
            return True
        if len(arg) > 1 and arg[0] == "-" and arg[1] != "-":
            for char in arg[1:]:
                if char == "a":
                    return True
                if char in COMMIT_OPTS_WITH_VALUE or char in COMMIT_OPTS_WITH_OPTIONAL_VALUE:
                    break
    return False


def commit_plan(command: str) -> tuple[bool, bool]:
    """Return (runs a real commit, must scan unstaged changes)."""
    runs_commit = False
    scan_unstaged = False
    for line in command.splitlines():
        for segment in split_segments(tokenize(line)):
            index = git_index(segment)
            if index is None:
                continue
            subcommand, args = git_subcommand(segment[index + 1 :])
            if subcommand != "commit" or is_help_or_dry_run(args):
                continue
            runs_commit = True
            if includes_all(args):
                scan_unstaged = True
    return runs_commit, scan_unstaged


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    parts = [tool_input.get("command"), tool_input.get("cmd"), payload.get("command")]
    command = "\n".join(str(part) for part in parts if part)
    runs_commit, scan_unstaged = commit_plan(command)
    if not runs_commit:
        return 0

    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = "."

    text = command
    text += "\n" + git_diff(["diff", "--cached", "--no-color", "--unified=0"], cwd)
    if scan_unstaged:
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
