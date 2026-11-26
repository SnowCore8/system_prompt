#!/usr/bin/env python3
"""SessionStart 钩子：把全局用户约束安装到 Qoder 用户级 rules。

Qoder CLI 没有插件安装/卸载生命周期 hook，因此首次 SessionStart 时把包内
rules/global-user-constraints.md 复制到用户 rules 目录；内容不同则直接覆盖。
首次安装或内容更新时同时把全文作为 additionalContext 注入，桥接当前会话；
后续会话由 Qoder 原生 rules 加载。卸载插件不会自动删除该文件，需手动删除。
"""

import json
import os
import sys
from pathlib import Path

RULES_FILENAME = "global-user-constraints.md"
MAX_BYTES = 40 * 1024
RULES_DIRS = ("constraints", "rules")


def plugin_root() -> Path:
    value = os.environ.get("QODER_PLUGIN_ROOT")
    if value:
        return Path(value)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "rules" / RULES_FILENAME).is_file():
            return parent
    return here.parents[1]


def config_root() -> Path:
    for name in ("QODERCN_CONFIG_DIR", "QODER_CONFIG_DIR"):
        value = os.environ.get(name)
        if value:
            return Path(value)
    home = Path(os.environ.get("HOME") or Path.home())
    cn = home / ".qoder-cn"
    en = home / ".qoder"
    if cn.is_dir() and not en.is_dir():
        return cn
    return en


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
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "SessionStart":
        return 0

    root = plugin_root()
    rules_path = next(
        (root / directory / RULES_FILENAME for directory in RULES_DIRS
         if (root / directory / RULES_FILENAME).is_file()),
        None,
    )
    if rules_path is None:
        return 0
    try:
        data = rules_path.read_bytes()
    except OSError:
        return 0
    if len(data) > MAX_BYTES:
        return 0

    target = config_root() / "rules" / RULES_FILENAME
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file() and target.read_bytes() == data:
            return 0
        target.write_bytes(data)
    except OSError as error:
        emit("SessionStart", f"全局用户约束安装失败：写入 {target} 失败（{error.strerror or error}）；本会话仍将注入全文。")
        return 0

    text = data.decode("utf-8", "replace").strip()
    emit(
        "SessionStart",
        f"全局用户约束已安装到 {target}（本会话首次/更新注入，后续由 Qoder 原生 rules 加载）：\n\n{text}",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
