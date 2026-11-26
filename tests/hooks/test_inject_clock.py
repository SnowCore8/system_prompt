#!/usr/bin/env python3
"""inject_clock.py 与双端 hook 配置的表驱动测试。"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).parents[2] / "shared" / "scripts" / "inject_clock.py"
ROOT = Path(__file__).parents[2]
QODER_HOOKS = ROOT / "plugins/qoder/hooks/hooks.json"
QWEN_HOOKS = ROOT / "plugins/qwen/hooks/qwen-hooks.json"
QODER_MANIFEST = ROOT / "plugins/qoder/.qoder-plugin/plugin.json"
QWEN_MANIFEST = ROOT / "plugins/qwen/qwen-extension.json"
CLOCK_PATTERN = re.compile(
    r"^当前时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:\d{2}"
    r"（[^）]*星期[一二三四五六日]）。"
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_hook(payload):
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    return subprocess.run(
        [sys.executable, "-B", str(HOOK)],
        input=raw, capture_output=True, text=True, check=False,
        env={**os.environ, "TZ": "Asia/Shanghai"},
    )


class InjectClockTest(unittest.TestCase):
    def test_injects_clock_on_session_start(self):
        proc = run_hook({"hook_event_name": "SessionStart"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        self.assertRegex(output["additionalContext"], CLOCK_PATTERN)
        self.assertIn("Asia/Shanghai", output["additionalContext"])

    def test_injects_clock_on_user_prompt_submit(self):
        proc = run_hook({"hook_event_name": "UserPromptSubmit"})
        output = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "UserPromptSubmit")
        self.assertRegex(output["additionalContext"], CLOCK_PATTERN)

    def test_ignores_other_events(self):
        for event in ("PreToolUse", "PostToolUse", "SessionEnd"):
            proc = run_hook({"hook_event_name": event})
            self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_invalid_payload_is_silent(self):
        for payload in ("", "not json", "[]", '"text"', "{}"):
            proc = run_hook(payload)
            self.assertEqual((proc.returncode, proc.stdout), (0, ""))


class HookConfigTest(unittest.TestCase):
    def test_qoder_hooks_register_clock(self):
        hooks = load_json(QODER_HOOKS)["hooks"]
        self.assertEqual(set(hooks), {"SessionStart", "UserPromptSubmit"})
        names = [h["name"] for h in hooks["SessionStart"][0]["hooks"]]
        self.assertEqual(names, ["install-constraints", "inject-clock"])
        user_names = [h["name"] for h in hooks["UserPromptSubmit"][0]["hooks"]]
        self.assertEqual(user_names, ["inject-constraints-reminder", "inject-clock"])
        clock = hooks["UserPromptSubmit"][0]["hooks"][1]
        self.assertEqual(clock["name"], "inject-clock")
        self.assertTrue(clock["args"][2].endswith("/scripts/inject_clock.py"))

    def test_qwen_hooks_register_clock(self):
        hooks = load_json(QWEN_HOOKS)
        self.assertEqual(set(hooks), {"SessionStart", "UserPromptSubmit"})
        names = [h["name"] for h in hooks["SessionStart"][0]["hooks"]]
        self.assertEqual(names, ["inject-constraints", "inject-clock"])
        for hook in hooks["SessionStart"][0]["hooks"] + hooks["UserPromptSubmit"][0]["hooks"]:
            self.assertIn('"${CLAUDE_PLUGIN_ROOT}/scripts/', hook["command"])
            self.assertNotIn("args", hook)
        constraints = hooks["SessionStart"][0]["hooks"][0]["command"]
        self.assertTrue(constraints.endswith('"${CLAUDE_PLUGIN_ROOT}"'))
        self.assertIn("inject_constraints.py", constraints)

    def test_manifests_agree_on_version_and_hooks_path(self):
        qoder = load_json(QODER_MANIFEST)
        qwen = load_json(QWEN_MANIFEST)
        self.assertEqual(qoder["version"], qwen["version"])
        hooks_path = QWEN_MANIFEST.parent / qwen["hooks"]
        self.assertTrue(hooks_path.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "qwen"
            subprocess.run(
                ["bash", str(ROOT / "scripts/materialize.sh"), "qwen", str(target)],
                check=True, capture_output=True, text=True,
            )
            self.assertTrue((target / qwen["skills"]).is_dir())
            self.assertTrue((target / qwen["commands"]).is_dir())
            self.assertTrue((target / "constraints/global-user-constraints.md").is_file())


if __name__ == "__main__":
    unittest.main()
