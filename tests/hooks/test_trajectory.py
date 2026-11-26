#!/usr/bin/env python3
"""trajectory.py 的全事件轨迹测试。"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).parents[2] / "shared" / "scripts" / "trajectory.py"
HOOKS_JSON = Path(__file__).parents[2] / "plugins" / "qoder" / "hooks" / "hooks.json"
EVENTS = {
    "SessionStart", "SessionEnd", "UserPromptSubmit", "PreToolUse", "PostToolUse",
    "PostToolUseFailure", "PermissionRequest", "PermissionDenied", "Stop", "StopFailure",
    "SubagentStart", "SubagentStop", "PreCompact", "PostCompact", "PreModelSwitch",
    "PostModelSwitch", "Notification", "InstructionsLoaded", "ConfigChange", "CwdChanged",
    "FileChanged", "WorktreeCreate", "WorktreeRemove", "Elicitation", "ElicitationResult",
}


def run(payload, env):
    return subprocess.run(
        [sys.executable, "-B", str(HOOK)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TZ": "Asia/Shanghai", **env},
    )


class TrajectoryTest(unittest.TestCase):
    def test_logs_every_event_and_context_only_where_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {"QODER_PLUGIN_DATA": tmp}
            first = run(
                {"hook_event_name": "PreToolUse", "session_id": "trajectory-test", "tool_name": "Bash"},
                env,
            )
            second = run(
                {"hook_event_name": "FileChanged", "session_id": "trajectory-test", "file_path": "/tmp/a"},
                env,
            )
            third = run(
                {"hook_event_name": "UserPromptSubmit", "session_id": "trajectory-test"},
                env,
            )
            log = next((Path(tmp) / "trajectory").glob("*.jsonl"))
            records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("Time sampled at PreToolUse", first.stdout)
        self.assertEqual((second.returncode, second.stdout), (0, ""))
        self.assertEqual((third.returncode, third.stdout), (0, ""))
        self.assertEqual([record["event"] for record in records], [
            "PreToolUse", "FileChanged", "UserPromptSubmit",
        ])
        self.assertEqual(records[0]["tool_name"], "Bash")
        self.assertEqual(records[0]["elapsed"], "unavailable")
        self.assertRegex(records[2]["ts"], r"^\d{4}-\d{2}-\d{2}T")

    def test_session_end_removes_trajectory_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {"QODER_PLUGIN_DATA": tmp}
            run({"hook_event_name": "PreToolUse", "session_id": "cleanup-trajectory"}, env)
            state_dir = Path(tmp) / "trajectory"
            state = next(state_dir.glob("*.json"))
            end = run({"hook_event_name": "SessionEnd", "session_id": "cleanup-trajectory"}, env)
            self.assertEqual((end.returncode, end.stdout), (0, ""))
            self.assertFalse(state.exists())
            log = next(state_dir.glob("*.jsonl"))
            events = [json.loads(line)["event"] for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(events[-1], "SessionEnd")

    def test_all_qoder_events_have_a_trajectory_hook(self):
        hooks = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(set(hooks), EVENTS)
        for event, groups in hooks.items():
            names = [hook["name"] for group in groups for hook in group["hooks"]]
            self.assertIn("trajectory", names, event)

    def test_emits_time_without_plugin_data(self):
        proc = run({"hook_event_name": "PreToolUse"}, {})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Time sampled at PreToolUse", proc.stdout)


if __name__ == "__main__":
    unittest.main()
