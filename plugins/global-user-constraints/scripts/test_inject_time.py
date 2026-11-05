#!/usr/bin/env python3
"""Table-driven tests for inject-time.py."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).with_name("inject-time.py")
HOOKS_JSON = Path(__file__).parents[1] / "hooks" / "hooks.json"
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
    def run_hook(self, payload) -> subprocess.CompletedProcess:
        raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        return subprocess.run(
            [sys.executable, "-B", str(HOOK)],
            input=raw,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_registered_events_match_supported_events(self):
        config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(set(config["hooks"]), SUPPORTED_EVENTS)

    def test_supported_events_inject_time(self):
        for event in sorted(SUPPORTED_EVENTS):
            with self.subTest(event=event):
                proc = self.run_hook({"hook_event_name": event})
                self.assertEqual(proc.returncode, 0)
                self.assertEqual(proc.stderr, "")
                output = json.loads(proc.stdout)["hookSpecificOutput"]
                self.assertEqual(output["hookEventName"], event)
                self.assertRegex(output["additionalContext"], TIME_PATTERN)

    def test_unsupported_event_is_silent(self):
        for event in ("Stop", "PermissionRequest", "PostCompact"):
            with self.subTest(event=event):
                proc = self.run_hook({"hook_event_name": event})
                self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_invalid_payload_is_silent(self):
        for payload in ("", "not json", "[]", '"text"', "{}"):
            with self.subTest(payload=payload):
                proc = self.run_hook(payload)
                self.assertEqual((proc.returncode, proc.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
