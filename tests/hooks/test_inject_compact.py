#!/usr/bin/env python3
"""inject_compact.py 与压缩后 hook 配置测试。"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).parents[2] / "shared" / "scripts" / "inject_compact.py"
HOOKS_JSON = Path(__file__).parents[2] / "plugins" / "qoder" / "hooks" / "hooks.json"


def run_hook(payload):
    return subprocess.run(
        [sys.executable, "-B", str(HOOK)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TZ": "Asia/Shanghai"},
    )


class InjectCompactTest(unittest.TestCase):
    def test_emits_constraint_and_time_after_compaction(self):
        proc = run_hook({"hook_event_name": "SessionStart", "source": "compact"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        context = output["additionalContext"]
        self.assertIn("Never violate global user constraints.", context)
        self.assertIn("Time sampled after context compaction:", context)
        self.assertIn("Browser time zone for this request:", context)

    def test_ignores_non_compact_sources(self):
        for source in ("startup", "resume", "clear", "new"):
            with self.subTest(source=source):
                proc = run_hook({"hook_event_name": "SessionStart", "source": source})
                self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_ignores_other_events(self):
        proc = run_hook({"hook_event_name": "PostCompact", "source": "auto"})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_hooks_config_has_compact_matcher(self):
        hooks = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]["SessionStart"]
        compact = [group for group in hooks if group.get("matcher") == "compact"]
        self.assertEqual(len(compact), 1)
        self.assertEqual(compact[0]["hooks"][0]["name"], "inject-compact-constraints")


if __name__ == "__main__":
    unittest.main()
