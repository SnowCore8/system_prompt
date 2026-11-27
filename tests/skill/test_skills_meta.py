#!/usr/bin/env python3
"""skill 结构契约：解剖、维度索引、去重与当前事实表述。

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
REQUIRED_SECTIONS = ("适用范围与优先级", "生命周期定位", "门禁与证据", "维度索引", "参考资料")
MAX_LINES = 250
HINT = re.compile(r"\[[^\]]+\]")
INDEX_HEADER = "| 编号 | 维度名 | 首条规则 | 详情 |"
NUMBERED_HEADING = re.compile(r"^## (\d+)\.")
HISTORY_TERMS = ("来源清单", "取证日期", "版本基线", "历史沿革", "新旧对照", "迁移说明")


def skill_files() -> list[Path]:
    return sorted(SKILLS.glob("*/SKILL.md"))


def body_of(path: Path) -> str:
    parts = path.read_text(encoding="utf-8").split("---", 2)
    return parts[2] if len(parts) == 3 else ""


def frontmatter_of(path: Path) -> dict[str, str]:
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) != 3:
        return {}
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            meta[match.group(1)] = match.group(2).strip()
    return meta


def paragraphs(text: str) -> set[str]:
    blocks = re.split(r"\n\s*\n", text)
    return {block.strip() for block in blocks if len(block.strip()) > 80}


class SkillsMetaTest(unittest.TestCase):
    def test_name_matches_directory(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                self.assertEqual(frontmatter_of(path).get("name"), path.parent.name)

    def test_argument_hint_uses_brackets(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                hint = frontmatter_of(path).get("argument-hint", "")
                self.assertTrue(hint, "缺少 argument-hint")
                self.assertRegex(hint, HINT)

    def test_description_states_scope_and_exclusion(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                description = frontmatter_of(path).get("description", "")
                self.assertIn("适用于", description)
                self.assertIn("不适用于", description)

    def test_required_sections_in_order(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                titles = H2.findall(body_of(path))
                self.assertTrue(titles, "缺少二级标题")
                self.assertEqual(titles[0], REQUIRED_SECTIONS[0])
                self.assertEqual(titles[-1], REQUIRED_SECTIONS[-1])
                found = [title for title in titles if title in REQUIRED_SECTIONS]
                self.assertEqual(found, list(REQUIRED_SECTIONS), "必要节缺失或顺序错误")

    def test_body_length(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                self.assertLessEqual(len(body_of(path).splitlines()), MAX_LINES)

    def test_dimension_index(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                body = body_of(path)
                section = self._section(body, "维度索引")
                self.assertIsNotNone(section, "缺少 维度索引 节")
                self.assertIn(INDEX_HEADER, section, "维度索引表头不符")
                rows = re.findall(r"^\|\s*(\d+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", section, re.M)
                self.assertTrue(rows, "维度索引没有可解析的行")
                numbers = [int(row[0]) for row in rows]
                self.assertEqual(numbers, list(range(1, len(rows) + 1)), "维度编号不连续")
                for number, _name, rule, detail in rows:
                    self.assertTrue(rule.strip().endswith("。"), "首条规则列应是一句规则")
                    match = re.fullmatch(r"\s*`?references/([\w./-]+)`?\s+第\s+(\d+)\s+节\s*", detail.strip())
                    self.assertTrue(match, f"详情列格式不符: {detail}")
                    reference = path.parent / "references" / match.group(1)
                    self.assertTrue(reference.is_file(), f"缺少 {match.group(1)}")
                    headings = NUMBERED_HEADING.findall(reference.read_text(encoding="utf-8"))
                    self.assertGreaterEqual(
                        len(headings), int(match.group(2)),
                        f"{match.group(1)} 的编号节不足",
                    )

    def test_no_prefix_self_reference(self) -> None:
        pattern = re.compile(r"`[a-z0-9-]+/references/[^`]+`")
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                body = body_of(path)
                self.assertIsNone(pattern.search(body), "references 应使用同目录相对名")

    def test_no_verbatim_duplication(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                body_blocks = paragraphs(body_of(path))
                reference_blocks: set[str] = set()
                for reference in (path.parent / "references").glob("*.md"):
                    reference_blocks |= paragraphs(reference.read_text(encoding="utf-8"))
                self.assertEqual(sorted(body_blocks & reference_blocks), [], "正文与 references 存在逐字重复段落")

    def test_no_cross_reference_duplication(self) -> None:
        corpus: dict[Path, set[str]] = {}
        for path in skill_files():
            blocks = paragraphs(body_of(path))
            for reference in (path.parent / "references").glob("*.md"):
                blocks |= paragraphs(reference.read_text(encoding="utf-8"))
            corpus[path.parent] = blocks
        seen: dict[str, Path] = {}
        for skill, blocks in corpus.items():
            for block in blocks:
                owner = seen.get(block)
                if owner is not None and owner != skill:
                    self.fail(f"{owner.name} 与 {skill.name} 存在逐字重复段落: {block[:60]}...")
                seen.setdefault(block, skill)

    def test_no_history_wording(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                texts = [body_of(path)]
                texts += [reference.read_text(encoding="utf-8") for reference in (path.parent / "references").glob("*.md")]
                for term in HISTORY_TERMS:
                    for text in texts:
                        self.assertNotIn(term, text, f"出现历史性措辞: {term}")

    @staticmethod
    def _section(body: str, title: str) -> str | None:
        match = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
        return match.group(1) if match else None


if __name__ == "__main__":
    unittest.main()
