#!/usr/bin/env python3
"""inject-constraints.py 的表驱动测试。"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).parents[2] / "shared" / "scripts" / "inject-constraints.py"
HOOKS_JSON = Path(__file__).parents[2] / "plugins" / "qoder" / "hooks" / "hooks.json"
RULES = "global-user-constraints.md"
MARKER = "# 测试约束\n\nMARKER-7f3a9c\n"


def load_hooks():
    return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]


class InjectConstraintsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plugin = self.root / "plugin"
        (self.plugin / "rules").mkdir(parents=True)
        (self.plugin / "rules" / RULES).write_text(MARKER, encoding="utf-8")
        self.home = self.root / "home"
        self.home.mkdir()
        self.cn = self.root / "cn"
        self.en = self.root / "en"
        self.cn.mkdir()
        self.en.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def env(self):
        return {
            "QODER_PLUGIN_ROOT": str(self.plugin),
            "HOME": str(self.home),
            "QODERCN_CONFIG_DIR": str(self.cn),
            "QODER_CONFIG_DIR": str(self.en),
        }

    def run_hook(self, payload, env=None):
        raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        return subprocess.run(
            [sys.executable, "-B", str(HOOK)],
            input=raw,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, **(env if env is not None else self.env())},
            cwd=self.project,
        )

    def test_hooks_config_points_to_scripts(self):
        hooks = load_hooks()
        self.assertEqual(set(hooks), {"SessionStart", "UserPromptSubmit"})
        names = [hook["name"] for hook in hooks["SessionStart"][0]["hooks"]]
        self.assertEqual(names, ["inject-constraints", "inject-clock"])
        entry = hooks["SessionStart"][0]["hooks"][0]
        self.assertEqual(entry["command"], "python")
        self.assertEqual(entry["args"][:2], ["-X", "utf8"])
        self.assertTrue(entry["args"][2].endswith("/scripts/inject-constraints.py"))
        self.assertGreater(entry["timeout"], 0)

    def test_injects_full_rules(self):
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        self.assertIn("MARKER-7f3a9c", output["additionalContext"])

    def test_skips_resume_source(self):
        proc = self.run_hook({"hook_event_name": "SessionStart", "source": "resume",
                              "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_injects_after_clear_or_compact(self):
        for source in ("startup", "new", "clear", "compact"):
            with self.subTest(source=source):
                proc = self.run_hook({"hook_event_name": "SessionStart", "source": source,
                                      "cwd": str(self.project)})
                self.assertIn("MARKER-7f3a9c", proc.stdout)

    def test_skips_when_user_rule_matches(self):
        target = self.cn / "rules"
        target.mkdir(parents=True)
        (target / RULES).write_text(MARKER, encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_skips_when_project_rule_matches(self):
        (self.project / ".git").mkdir()
        target = self.project / ".qoder" / "rules"
        target.mkdir(parents=True)
        (target / RULES).write_text(MARKER, encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_skips_when_project_agents_matches(self):
        (self.project / ".git").mkdir()
        (self.project / "AGENTS.md").write_text(MARKER, encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_skips_when_qwen_agents_matches(self):
        target = self.home / ".qwen"
        target.mkdir()
        (target / "AGENTS.md").write_text(MARKER, encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_skips_when_qwen_project_rule_matches(self):
        (self.project / ".git").mkdir()
        target = self.project / ".qwen" / "rules"
        target.mkdir(parents=True)
        (target / RULES).write_text(MARKER, encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_constraints_directory_is_supported(self):
        (self.plugin / "rules" / RULES).unlink()
        (self.plugin / "constraints").mkdir()
        (self.plugin / "constraints" / RULES).write_text(MARKER, encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertIn("MARKER-7f3a9c", proc.stdout)

    def test_claude_plugin_root_env_is_supported(self):
        env = self.env()
        env.pop("QODER_PLUGIN_ROOT")
        env["CLAUDE_PLUGIN_ROOT"] = str(self.plugin)
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)}, env=env)
        self.assertIn("MARKER-7f3a9c", proc.stdout)

    def test_root_argument_wins_over_env(self):
        env = self.env()
        env.pop("QODER_PLUGIN_ROOT")
        raw = json.dumps({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        proc = subprocess.run(
            [sys.executable, "-B", str(HOOK), str(self.plugin)],
            input=raw, capture_output=True, text=True, check=False,
            env={**os.environ, **env}, cwd=self.project,
        )
        self.assertIn("MARKER-7f3a9c", proc.stdout)

    def test_ignores_other_events(self):
        for event in ("UserPromptSubmit", "PreToolUse", "SessionEnd"):
            proc = self.run_hook({"hook_event_name": event, "cwd": str(self.project)})
            self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_invalid_payload_is_silent(self):
        for payload in ("", "not json", "[]", '"text"', "{}"):
            proc = self.run_hook(payload)
            self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_missing_rules_file_is_silent(self):
        (self.plugin / "rules" / RULES).unlink()
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
