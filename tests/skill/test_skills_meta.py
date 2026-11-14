#!/usr/bin/env python3
"""skill 元规范校验。

把 `skills/skill-authoring` 的结构要求变成可执行断言，避免正文与 references 再次分叉。
用标准库 unittest 编写：
    python3 -B -m unittest discover -s tests/skill -p 'test_*.py'
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / "skills"

FIRST_SECTION = "适用范围与优先级"
LAST_SECTION = "参考资料"
INDEX_HEADER = "| 维度 | 首条规则 | 详情 |"
INDEX_SENTENCE = (
    "每个维度的详细规则、示例与边界情况见 `references/dimensions.md`；"
    "维度列中的编号就是该文件中的节号。"
)
MAX_LINES = 250
MIN_DUPLICATE = 24

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
FIELD = re.compile(r"^(name|description|argument-hint):[ \t]*(.+)$", re.M)
H2 = re.compile(r"^## (.+)$", re.M)
HINT = re.compile(r"^'\[[^\[\]<>]+\]'$")
INDEX_SECTION = re.compile(r"^## 维度索引\n(.*?)(?=^## )", re.M | re.S)
INDEX_ROW = re.compile(r"^\| (\d+)\. [^|]+ \| [^|]+ \| `references/dimensions\.md` 第 (\d+) 节 \|$", re.M)
DIM_SECTION = re.compile(r"^## (\d+)\. ", re.M)
SELF_REFERENCE = re.compile(r"references/[a-z0-9-]+\.md")
CJK = re.compile(r"[\u4e00-\u9fff]")


def skill_files() -> list[Path]:
    return sorted(SKILLS.glob("*/SKILL.md"))


def parse(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    body = text[match.end():]
    # description 可能以折叠标量续行出现，取首行已足够判定触发面
    return dict(FIELD.findall(match.group(1))), body


def paragraphs(text: str) -> list[str]:
    """取可比较的段落：去掉列表标记与首尾空白，只保留含中文的长行。"""
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        stripped = re.sub(r"^(?:[-*]|\d+\.)\s*(?:\[[ x]\]\s*)?", "", stripped)
        if len(stripped) >= MIN_DUPLICATE and CJK.search(stripped):
            out.append(re.sub(r"\s+", "", stripped))
    return out


class FrontmatterTest(unittest.TestCase):
    def test_name_matches_directory(self) -> None:
        for path in skill_files():
            meta, _ = parse(path)
            with self.subTest(skill=path.parent.name):
                self.assertEqual(meta.get("name"), path.parent.name)

    def test_argument_hint_uses_brackets(self) -> None:
        for path in skill_files():
            meta, _ = parse(path)
            with self.subTest(skill=path.parent.name):
                self.assertTrue(meta.get("argument-hint"), "缺少 argument-hint")
                self.assertRegex(meta["argument-hint"], HINT)

    def test_description_states_scope_and_exclusion(self) -> None:
        for path in skill_files():
            meta, _ = parse(path)
            description = meta.get("description", "")
            with self.subTest(skill=path.parent.name):
                self.assertIn("适用于", description)
                self.assertIn("不适用于", description)


class StructureTest(unittest.TestCase):
    def test_first_and_last_section(self) -> None:
        for path in skill_files():
            _, body = parse(path)
            titles = H2.findall(body)
            with self.subTest(skill=path.parent.name):
                self.assertTrue(titles, "缺少二级标题")
                self.assertEqual(titles[0], FIRST_SECTION)
                self.assertEqual(titles[-1], LAST_SECTION)

    def test_body_length(self) -> None:
        for path in skill_files():
            with self.subTest(skill=path.parent.name):
                self.assertLessEqual(len(path.read_text(encoding="utf-8").splitlines()), MAX_LINES)

    def test_dimension_index(self) -> None:
        for path in skill_files():
            reference = path.parent / "references" / "dimensions.md"
            if not reference.is_file():
                continue  # 元规范 skill 的 references 不按维度切分
            _, body = parse(path)
            section = INDEX_SECTION.search(body)
            with self.subTest(skill=path.parent.name):
                self.assertIsNotNone(section, "缺少 维度索引 节")
                assert section is not None
                block = section.group(1)
                self.assertIn(INDEX_SENTENCE, block)
                self.assertIn(INDEX_HEADER, block)
                rows = INDEX_ROW.findall(block)
                self.assertEqual([n for n, _ in rows], [m for m, _ in rows], "详情列节号与维度编号不一致")
                numbers = DIM_SECTION.findall(reference.read_text(encoding="utf-8"))
                self.assertEqual([n for n, _ in rows], numbers)
                for line in block.splitlines():
                    if line.startswith("|---"):
                        continue
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    if len(cells) != 3 or cells[0] == "维度":
                        continue
                    self.assertNotIn("references/", cells[1], "首条规则列混入了详情内容")
                    self.assertFalse(cells[0].endswith("。"), "维度名列写成了规则句")
                    self.assertTrue(cells[1].endswith("。"), "首条规则列应是一句规则")
                    self.assertEqual(cells[2], f"`references/dimensions.md` 第 {cells[0].split('.')[0]} 节")


class ReferenceTest(unittest.TestCase):
    def test_no_prefix_self_reference(self) -> None:
        for path in skill_files():
            for reference in sorted((path.parent / "references").glob("*.md")):
                text = reference.read_text(encoding="utf-8")
                with self.subTest(file=reference.relative_to(SKILLS)):
                    self.assertIsNone(SELF_REFERENCE.search(text), "references 内应使用同目录相对名")

    def test_no_verbatim_duplication(self) -> None:
        for path in skill_files():
            _, body = parse(path)
            own = set(paragraphs(body))
            for reference in sorted((path.parent / "references").glob("*.md")):
                shared = own & set(paragraphs(reference.read_text(encoding="utf-8")))
                with self.subTest(file=reference.relative_to(SKILLS)):
                    self.assertEqual(sorted(shared), [], "正文与 references 存在逐字重复段落")


if __name__ == "__main__":
    unittest.main()
