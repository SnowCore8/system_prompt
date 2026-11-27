#!/usr/bin/env python3
"""Markdown 校验器的确定性模糊测试：任意输入不得崩溃。"""

from __future__ import annotations

import random
import string
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "mdcheck"))

import check  # noqa: E402

MD = check.load_markdown_it()
BASE = Path(__file__).resolve().parents[2]

PIECES = [
    "# 标题\n\n正文。\n",
    "```python\nprint(1)\n```\n",
    "| a | b |\n|---|---|\n| 1 | 2 |\n",
    "[链接](x.md) [引用][r]\n\n[r]: x.md\n",
    "> 引用\n> 继续\n",
    "- 列表\n  - 嵌套\n",
    "![图](x.png)\n",
    "<div>未闭合\n",
    "<!-- 注释",
    "**强调** ~~删除~~ `代码`\n",
    "```",
    "\\\n",
    "\t制表符行\n",
    "a" * 300,
    "\n\n\n\n",
    "普通文本。\n",
    "emoji 🚀 与中文标点：，。！\n",
]


def random_document(rng: random.Random) -> str:
    count = rng.randint(1, 12)
    parts = [rng.choice(PIECES) for _ in range(count)]
    if rng.random() < 0.3:
        parts.append("".join(rng.choices(string.printable, k=rng.randint(1, 200))))
    return "\n".join(parts) + ("\n" if rng.random() < 0.5 else "")


class MarkdownFuzzTest(unittest.TestCase):
    def test_random_documents_never_crash(self) -> None:
        rng = random.Random(20261127)
        for _ in range(300):
            text = random_document(rng)
            doc = check.Doc(text, MD)
            findings = check.check_format(doc, BASE) + check.check_anchors(doc)
            self.assertIsInstance(findings, list)
            for finding in findings:
                self.assertIsInstance(finding.level, str)
                self.assertIsInstance(finding.rule, str)


if __name__ == "__main__":
    unittest.main()
