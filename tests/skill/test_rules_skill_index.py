#!/usr/bin/env python3
"""规则正文与 skill 目录的一致性校验。

常驻规则必须点名本仓库配套的全部 skill，避免智能体把它与其他插件的同类 skill 混淆。
用标准库 unittest 编写：
    python3 -B -m unittest discover -s tests/skill -p 'test_*.py'
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RULES = REPO / "rules" / "global-user-constraints.md"
SKILLS = REPO / "skills"
REFERENCE = re.compile(r"`([a-z][a-z0-9-]*)`")
SUFFIXES = ("-conventions", "-authoring")


def skill_names() -> set[str]:
    return {path.parent.name for path in SKILLS.glob("*/SKILL.md")}


class RulesSkillIndexTest(unittest.TestCase):
    def test_all_skills_are_named(self) -> None:
        text = RULES.read_text(encoding="utf-8")
        named = set(REFERENCE.findall(text))
        missing = sorted(skill_names() - named)
        self.assertEqual(missing, [], "规则正文未点名这些 skill")

    def test_no_unknown_skill_names(self) -> None:
        text = RULES.read_text(encoding="utf-8")
        known = skill_names()
        unknown = sorted(
            name
            for name in set(REFERENCE.findall(text))
            if name.endswith(SUFFIXES) and name not in known
        )
        self.assertEqual(unknown, [], "规则正文点名了不存在的 skill")


if __name__ == "__main__":
    unittest.main()
