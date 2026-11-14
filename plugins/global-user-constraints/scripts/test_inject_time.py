#!/usr/bin/env python3
"""inject-time.py 的表驱动测试。"""

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).with_name("inject-time.py")
HOOKS_JSON = Path(__file__).parents[1] / "hooks" / "hooks.json"
def load_implementation():
    """加载连字符文件名的实现模块，避免在测试里复制事件集合。"""
    spec = importlib.util.spec_from_file_location("inject_time", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

    def load_hooks(self):
        return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]

    def test_registered_events_match_supported_events(self):
        implemented = set(load_implementation().SUPPORTED_EVENTS)
        self.assertEqual(set(self.load_hooks()), implemented)

    def test_registered_commands_are_consistent(self):
        for event, groups in self.load_hooks().items():
            with self.subTest(event=event):
                self.assertTrue(groups)
                for group in groups:
                    self.assertNotIn("matcher", group)
                    for hook in group["hooks"]:
                        self.assertEqual(hook["type"], "command")
                        self.assertEqual(hook["command"], "python")
                        self.assertEqual(hook["args"][:2], ["-X", "utf8"])
                        self.assertTrue(hook["args"][2].endswith("/scripts/inject-time.py"))
                        self.assertGreater(hook["timeout"], 0)

    def test_registered_command_runs(self):
        event, groups = next(iter(self.load_hooks().items()))
        hook = groups[0]["hooks"][0]
        interpreter = shutil.which(hook["command"])
        if interpreter is None:
            self.skipTest("注册命令使用的 python 不在 PATH")
        major = subprocess.run(
            [interpreter, "-c", "import sys; print(sys.version_info[0])"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        if major != "3":
            self.skipTest("注册命令解析到的 python 不是 3.x")
        args = [interpreter] + [
            arg.replace("${QODER_PLUGIN_ROOT}", str(HOOK.parents[1])) for arg in hook["args"]
        ]
        proc = subprocess.run(
            args, input=json.dumps({"hook_event_name": event}),
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0)
        output = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], event)
        self.assertRegex(output["additionalContext"], TIME_PATTERN)

    def test_supported_events_inject_time(self):
        for event in sorted(load_implementation().SUPPORTED_EVENTS):
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
