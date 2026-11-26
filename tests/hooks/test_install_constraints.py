#!/usr/bin/env python3
"""install_constraints.py 的表驱动测试。"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).parents[2] / "shared" / "scripts" / "install_constraints.py"
RULES = "global-user-constraints.md"
MARKER = "# 测试约束\n\nMARKER-install-4c1d\n"
MARKER2 = "# 测试约束\n\nMARKER-updated-9e2b\n"


class InstallConstraintsTest(unittest.TestCase):
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

    def env(self, cn=True, en=True):
        values = {"QODER_PLUGIN_ROOT": str(self.plugin), "HOME": str(self.home)}
        if cn:
            values["QODERCN_CONFIG_DIR"] = str(self.cn)
        if en:
            values["QODER_CONFIG_DIR"] = str(self.en)
        return values

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

    def test_installs_to_cn_without_emitting_context(self):
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        target = self.cn / "rules" / RULES
        self.assertEqual(target.read_text(encoding="utf-8"), MARKER)

    def test_second_run_is_silent(self):
        self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_overwrites_changed_rules(self):
        (self.plugin / "rules" / RULES).write_text(MARKER, encoding="utf-8")
        self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        (self.plugin / "rules" / RULES).write_text(MARKER2, encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        self.assertEqual((self.cn / "rules" / RULES).read_text(encoding="utf-8"), MARKER2)

    def test_uses_en_config_dir_when_cn_is_absent(self):
        proc = self.run_hook(
            {"hook_event_name": "SessionStart", "cwd": str(self.project)},
            env=self.env(cn=False, en=True),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.en / "rules" / RULES).is_file())
        self.assertFalse((self.cn / "rules" / RULES).exists())

    def test_ignores_non_session_start(self):
        proc = self.run_hook({"hook_event_name": "UserPromptSubmit", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        self.assertFalse((self.cn / "rules" / RULES).exists())

    def test_oversized_rules_are_not_installed(self):
        (self.plugin / "rules" / RULES).write_text(MARKER + "x" * (40 * 1024), encoding="utf-8")
        proc = self.run_hook({"hook_event_name": "SessionStart", "cwd": str(self.project)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        self.assertFalse((self.cn / "rules" / RULES).exists())


if __name__ == "__main__":
    unittest.main()
