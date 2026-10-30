#!/usr/bin/env python3
"""Table-driven tests for inject-context.py."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).with_name("inject-context.py")
HOOKS_JSON = Path(__file__).parents[1] / "hooks" / "hooks.json"
RULES_FILE = Path(__file__).parents[1] / "rules" / "global-user-constraints.md"
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
RULES_EVENTS = {"SessionStart", "SubagentStart"}
TIME_PATTERN = re.compile(r"^当前时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:\d{2}$")


def rules_body() -> str:
    text = RULES_FILE.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return text.strip()


class InjectContextHookTest(unittest.TestCase):
    def run_hook(self, payload) -> subprocess.CompletedProcess:
        raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        return subprocess.run(
            [sys.executable, "-B", str(HOOK)],
            input=raw,
            capture_output=True,
            text=True,
            check=False,
        )

    def context_for_event(self, event: str) -> str:
        proc = self.run_hook({"hook_event_name": event})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stderr, "")
        return json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_registered_events_match_supported_events(self):
        config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(set(config["hooks"]), SUPPORTED_EVENTS)

    def test_supported_events_inject_time(self):
        for event in sorted(SUPPORTED_EVENTS):
            with self.subTest(event=event):
                output = json.loads(self.run_hook({"hook_event_name": event}).stdout)["hookSpecificOutput"]
                self.assertEqual(output["hookEventName"], event)
                self.assertRegex(output["additionalContext"].split("\n", 1)[0], TIME_PATTERN)

    def test_rules_injected_at_session_and_subagent_start(self):
        body = rules_body()
        for event in sorted(RULES_EVENTS):
            with self.subTest(event=event):
                context = self.context_for_event(event)
                self.assertIn("全局用户约束（必须遵守）", context)
                self.assertTrue(context.endswith(body))
                self.assertNotIn("alwaysApply", context)
                self.assertNotIn("\nname: global-user-constraints", context)

    def test_rules_not_injected_on_other_events(self):
        for event in sorted(SUPPORTED_EVENTS - RULES_EVENTS):
            with self.subTest(event=event):
                context = self.context_for_event(event)
                self.assertEqual(context.count("\n"), 0)
                self.assertNotIn("全局用户约束", context)

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
