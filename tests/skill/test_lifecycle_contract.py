#!/usr/bin/env python3
"""skill 生命周期契约校验。

每个 skill 必须把生命周期写进正文与 references，而不是只在规则文件里点名。
用标准库 unittest 编写：
    python3 -B -m unittest discover -s tests/skill -p 'test_*.py'
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / "skills"
H2 = re.compile(r"^## (.+)$", re.M)
STAGE = re.compile(r"S[0-7]")
GATE = re.compile(r"G[0-7]")
LIFECYCLE_HEADINGS = (
    "## 阶段职责",
    "## 门禁证据",
    "## 交接与升级",
    "## 裁剪与度量",
)
STAGE_TABLE = "| 阶段 | 本 skill 的职责 | 产出 / 证据 |"
GATE_TABLE = "| 门禁 | 必须提供的证据 | 不满足时 |"


def skill_files() -> list[Path]:
    return sorted(SKILLS.glob("*/SKILL.md"))


def body_of(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) == 3:
        return parts[2]
    return text


class LifecycleContractTest(unittest.TestCase):
    def test_every_skill_has_lifecycle_sections(self) -> None:
        for path in skill_files():
            body = body_of(path)
            titles = H2.findall(body)
            with self.subTest(skill=path.parent.name):
                self.assertIn("生命周期定位", titles, "缺少 生命周期定位")
                self.assertIn("门禁与证据", titles, "缺少 门禁与证据")
                self.assertIn(STAGE_TABLE, body, "缺少阶段职责表")
                self.assertIn(GATE_TABLE, body, "缺少门禁证据表")

    def test_every_skill_has_lifecycle_reference(self) -> None:
        for path in skill_files():
            reference = path.parent / "references" / "lifecycle.md"
            with self.subTest(skill=path.parent.name):
                self.assertTrue(reference.is_file(), "缺少 references/lifecycle.md")
                text = reference.read_text(encoding="utf-8")
                for heading in LIFECYCLE_HEADINGS:
                    self.assertIn(heading, text, f"缺少 {heading}")
                self.assertGreaterEqual(len(set(STAGE.findall(text))), 3, "阶段覆盖不足")
                self.assertGreaterEqual(len(set(GATE.findall(text))), 1, "缺少门禁")
                body = body_of(path)
                self.assertIn("references/lifecycle.md", body, "正文未链接 lifecycle.md")


if __name__ == "__main__":
    unittest.main()
