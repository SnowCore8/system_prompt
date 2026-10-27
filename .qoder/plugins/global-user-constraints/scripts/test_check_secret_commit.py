#!/usr/bin/env python3
"""Table-driven tests for check-secret-commit.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).with_name("check-secret-commit.py")
SECRET = "sk_live_" + "A1b2C3d4E5f6G7h8I9j0K1l2"
PUBLIC_KEY = "pk_live_" + "A1b2C3d4E5f6G7h8I9j0K1l2"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


class SecretCommitHookTest(unittest.TestCase):
    def make_repo(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name)
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.invalid")
        git(repo, "config", "user.name", "test")
        (repo / "clean.txt").write_text("clean\n", encoding="utf-8")
        git(repo, "add", "clean.txt")
        git(repo, "commit", "-q", "-m", "init")
        return repo

    def prepare(self, repo: Path, state: str) -> None:
        if state == "clean":
            return
        if state == "public":
            (repo / "public.txt").write_text(
                f"NEXT_PUBLIC_STRIPE_KEY={PUBLIC_KEY}\n", encoding="utf-8"
            )
            git(repo, "add", "public.txt")
            return
        content = f"TOKEN={SECRET}\n"
        if state == "unstaged":
            (repo / "secret.txt").write_text("TOKEN=clean\n", encoding="utf-8")
            git(repo, "add", "secret.txt")
            git(repo, "commit", "-q", "-m", "track secret file")
        (repo / "secret.txt").write_text(content, encoding="utf-8")
        if state == "staged":
            git(repo, "add", "secret.txt")

    def run_hook(self, repo: Path, command: str) -> subprocess.CompletedProcess:
        payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(repo)}
        return subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_command_matrix(self) -> None:
        cases = [
            ("clean commit", "clean", "git commit -m ok", 0),
            ("staged secret", "staged", "git commit -m ok", 2),
            ("staged secret amend", "staged", "git commit --amend --no-edit", 2),
            ("unstaged secret without all", "unstaged", "git commit -m ok", 0),
            ("unstaged secret with -a", "unstaged", "git commit -a -m ok", 2),
            ("unstaged secret with -am", "unstaged", "git commit -am ok", 2),
            ("unstaged secret with -av", "unstaged", "git commit -av -m ok", 2),
            ("unstaged secret with --all", "unstaged", "git commit --all -m ok", 2),
            ("unstaged secret with --all only", "unstaged", "git commit --all", 2),
            ("message option looks like all", "unstaged", "git commit -ma ok", 0),
            ("git log mentions commit", "staged", "git log --grep commit", 0),
            ("echo mentions commit", "staged", "echo git commit", 0),
            ("git status", "staged", "git status", 0),
            ("help", "staged", "git commit --help", 0),
            ("short help", "staged", "git commit -h", 0),
            ("dry run", "staged", "git commit --dry-run", 0),
            ("other subcommand", "staged", "git commit-tree HEAD^{tree}", 0),
            ("public key is allowed", "public", "git commit -m ok", 0),
            ("chained command", "staged", "git add . && git commit -m ok", 2),
            ("quoted separator", "staged", 'echo "a;b" && git commit -m ok', 2),
            ("env prefix", "staged", "GIT_AUTHOR_NAME=x git commit -m ok", 2),
            ("sudo prefix", "staged", "sudo git commit -m ok", 2),
            ("git -C option", "staged", "git -C . commit -m ok", 2),
            ("newline separated", "staged", "echo hi\ngit commit -m ok", 2),
            ("secret in message", "clean", f"git commit -m {SECRET}", 2),
        ]
        for name, state, command, expected in cases:
            with self.subTest(name):
                repo = self.make_repo()
                self.prepare(repo, state)
                proc = self.run_hook(repo, command)
                self.assertEqual(
                    proc.returncode,
                    expected,
                    f"{command!r} -> {proc.returncode}\n{proc.stderr}",
                )

    def test_invalid_payload_exits_zero(self) -> None:
        for raw in ("", "not json", "[]", '"text"', "null"):
            with self.subTest(raw):
                proc = subprocess.run(
                    [sys.executable, str(HOOK)],
                    input=raw,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
