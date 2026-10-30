#!/usr/bin/env python3
"""Table-driven tests for the compiled inject-time hook binary (POSIX build)."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = REPO_ROOT / ".qoder" / "plugins" / "global-user-constraints"
HOOK = PLUGIN_DIR / "scripts" / "bin" / "inject-time"
HOOKS_JSON = PLUGIN_DIR / "hooks" / "hooks.json"
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
TIME_PATTERN = re.compile(r"^当前时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:\d{2}$")


class InjectTimeHookTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not HOOK.is_file():
            raise unittest.SkipTest(f"未找到 {HOOK}，先运行 scripts/build-hooks.sh")

    def run_hook(self, payload) -> subprocess.CompletedProcess:
        raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        return subprocess.run(
            [str(HOOK)],
            input=raw.encode("utf-8"),
            capture_output=True,
            check=False,
        )

    def test_registered_events_match_supported_events(self):
        config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(set(config["hooks"]), SUPPORTED_EVENTS)

    def test_registered_command_points_to_binary(self):
        config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        for event, groups in config["hooks"].items():
            for group in groups:
                for handler in group["hooks"]:
                    with self.subTest(event=event):
                        self.assertEqual(handler["type"], "command")
                        self.assertTrue(
                            handler["command"].endswith("/scripts/bin/inject-time"),
                            handler["command"],
                        )

    def test_supported_events_inject_time(self):
        for event in sorted(SUPPORTED_EVENTS):
            with self.subTest(event=event):
                proc = self.run_hook({"hook_event_name": event})
                self.assertEqual(proc.returncode, 0)
                self.assertEqual(proc.stderr, b"")
                output = json.loads(proc.stdout)["hookSpecificOutput"]
                self.assertEqual(output["hookEventName"], event)
                self.assertRegex(output["additionalContext"], TIME_PATTERN)

    def test_unsupported_event_is_silent(self):
        for event in ("Stop", "PermissionRequest", "PostCompact"):
            with self.subTest(event=event):
                proc = self.run_hook({"hook_event_name": event})
                self.assertEqual(proc.returncode, 0)
                self.assertEqual(proc.stdout, b"")

    def test_invalid_payload_is_silent(self):
        for payload in ("", "not json", "[]", '"text"', "{}"):
            with self.subTest(payload=payload):
                proc = self.run_hook(payload)
                self.assertEqual(proc.returncode, 0)
                self.assertEqual(proc.stdout, b"")

    def test_nested_key_is_ignored(self):
        payload = {"tool_input": {"prompt": '{"hook_event_name":"SessionStart"}'}}
        proc = self.run_hook(payload)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, b"")

    def test_truncated_object_is_silent(self):
        proc = self.run_hook('{"hook_event_name":"SessionStart"')
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, b"")

    def test_other_fields_are_ignored(self):
        payload = {"tool_name": "Bash", "hook_event_name": "PreToolUse", "session_id": "x"}
        proc = self.run_hook(payload)
        output = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")

    def test_nested_object_as_last_member(self):
        payload = {"hook_event_name": "PreToolUse", "tool_input": {"command": "ls"}}
        proc = self.run_hook(payload)
        output = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")

    def test_trailing_comma_is_silent(self):
        proc = self.run_hook('{"hook_event_name":"SessionStart",}')
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, b"")


if __name__ == "__main__":
    unittest.main()
