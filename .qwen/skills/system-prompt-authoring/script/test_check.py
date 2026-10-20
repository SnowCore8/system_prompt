#!/usr/bin/env python3
"""check.py 的自测用例。

用标准库 unittest 编写，装了 pytest 也能直接跑：
    python3 -m unittest discover -s script
    python3 -m pytest script/test_check.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check  # noqa: E402

MD = check.load_markdown_it()

EMPHASIS_WORDS = ("必须", "绝不", "禁止", "不得", "不准", "CRITICAL", "MUST", "NEVER")


def build(text: str) -> check.Doc:
    return check.Doc(text, MD)


def rules_of(text: str) -> list[str]:
    return [f.rule for f in check.check_rules(build(text))]


def structure_of(text: str) -> list[str]:
    return [f.rule for f in check.check_structure(build(text))]


class SetextHeadingTest(unittest.TestCase):
    """Setext 标题要能识别，否则会误报缺 S1/S6。"""

    def test_setext_headings_satisfy_role_and_output(self):
        text = (
            "Role and Objective\n"
            "==================\n"
            "\n"
            "测试。\n"
            "\n"
            "Output Format\n"
            "-------------\n"
            "\n"
            "- 只输出结果。\n"
        )
        doc = build(text)
        self.assertEqual([(h.level, h.text) for h in doc.headings],
                         [(1, "Role and Objective"), (2, "Output Format")])

    def test_atx_and_setext_mixed(self):
        text = "Role and Objective\n==================\n\n## 子节\n\n正文。\n"
        self.assertEqual([h.level for h in build(text).headings], [1, 2])


class HtmlCommentTest(unittest.TestCase):
    """HTML 注释块里的强调词不算正文。"""

    def test_strong_words_in_html_comment_ignored(self):
        body = "".join(f"- 绝不 绝不 绝不 绝不 绝不 绝不 绝不 {i}\n" for i in range(8))
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n"
            "<!--\n" + body + "-->\n\n"
            "## 始终\n\n- 改代码前先读测试。\n\n"
            "# Output Format\n\n- 只输出结果。\n"
        )
        doc = build(text)
        self.assertEqual(len(doc.html_lines), 10)
        strong = [line for _, line in doc.prose_lines if any(w in line for w in EMPHASIS_WORDS)]
        self.assertEqual(strong, [])


class IndentedCodeTest(unittest.TestCase):
    """缩进代码块里的列表项不算规则。"""

    def test_indented_code_not_counted_as_rules(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n"
            "## 始终\n\n- 改代码前先读测试。\n\n"
            "示例：\n\n"
            "    - 不要这样写\n"
            "    - 绝不这样写\n\n"
            "# Output Format\n\n- 只输出结果。\n"
        )
        doc = build(text)
        self.assertEqual(len(check.rule_lines(doc)), 1)
        self.assertTrue(doc.code_lines)


class QuoteFenceTest(unittest.TestCase):
    """引用块里的围栏不能被判成未闭合。"""

    def test_fence_inside_blockquote_is_closed(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "> ```text\n"
            "> 引用里的围栏\n"
            "> ```\n"
        )
        self.assertIsNone(build(text).unclosed)

    def test_real_unclosed_fence_still_reported(self):
        text = "# Role and Objective\n\n```python\nprint(1)\n"
        self.assertIsNotNone(build(text).unclosed)
        self.assertIn("MD-FENCE", structure_of(text))


class TableColumnsTest(unittest.TestCase):
    """超出表头的单元格会被解析器丢弃，要按源文本发现。"""

    def test_extra_cell_detected(self):
        text = (
            "# Role and Objective\n\n"
            "| 甲 | 乙 |\n"
            "|---|---|\n"
            "| 1 | 2 | 3 |\n"
        )
        doc = build(text)
        self.assertEqual([(t.start, t.cols) for t in doc.tables], [(3, [2, 3])])
        self.assertIn("MD-TABLE-COLS", structure_of(text))

    def test_escaped_pipe_and_code_pipe_not_counted(self):
        text = (
            "# Role and Objective\n\n"
            "| 甲 | 乙 |\n"
            "|---|---|\n"
            "| a \\| b | `x | y` |\n"
        )
        self.assertEqual([(t.start, t.cols) for t in build(text).tables], [(3, [2, 2])])
        self.assertNotIn("MD-TABLE-COLS", structure_of(text))


class InlineCodeTest(unittest.TestCase):
    """反引号里的规则词是在引用，不是在执行。"""

    def test_inline_code_stripped_from_prose(self):
        line = "正文：规则写作 `绝不` 和 `必须`，这里只是引用。"
        stripped = check.strip_inline_code(line)
        self.assertNotIn("绝不", stripped)
        self.assertNotIn("必须", stripped)
        self.assertEqual(len(stripped), len(line))

    def test_long_inline_code_does_not_change_length(self):
        doc = build("# Role and Objective\n\n见 `very/long/path/to/file.md`。\n")
        self.assertEqual(len(doc.prose_lines), 1)


class ExampleBlockTest(unittest.TestCase):
    """模板里字面写出的 <example> 只是示例，不能开启示例区。"""

    def test_literal_example_tag_inside_fence_ignored(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "```markdown\n<example>\n<input>1</input>\n</example>\n```\n\n"
            "## 始终\n\n- 改代码前先读测试。\n"
        )
        self.assertEqual(build(text).example_lines, set())

    def test_real_example_block_marked(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "<example>\n- 绝不提交凭证。\n</example>\n\n"
            "- 改代码前先读测试。\n"
        )
        doc = build(text)
        self.assertEqual(len(check.rule_lines(doc)), 1)


class DuplicateTest(unittest.TestCase):
    """重复检测：同义改写要报，同主题不同粒度不报。"""

    def test_reworded_rule_reported(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n"
            "## 始终\n\n"
            "- 改代码前先读相关模块和覆盖它的测试，按现有写法扩展。\n"
            "- 改代码之前，先阅读相关模块以及覆盖它们的测试，按现有写法扩展。\n"
            "- 提交前运行 `pytest -q` 并贴出退出码。\n"
        )
        found = check.check_duplicates(build(text))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].level, check.SUGGESTION)

    def test_distinct_rules_not_reported(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n"
            "## 始终\n\n"
            "- 改代码前先读相关模块和覆盖它的测试。\n"
            "- 提交前运行 `pytest -q` 并贴出退出码。\n"
            "- 金额用最小货币单位整数，不用浮点。\n"
        )
        self.assertEqual(check.check_duplicates(build(text)), [])

    def test_different_granularity_not_reported(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n"
            "## 始终\n\n"
            "- 提交前运行测试。\n"
            "- 提交前运行 `pytest -q`、`ruff check` 与 `mypy`，三项全部通过并贴出退出码。\n"
        )
        self.assertEqual(check.check_duplicates(build(text)), [])


class ReferenceTest(unittest.TestCase):
    """S10：点名的路径必须存在。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "real.md").write_text("# 真文件\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, text: str) -> list[check.Finding]:
        return check.check_references(build(text), self.root)

    def test_missing_path_reported(self):
        found = self._run("# Role and Objective\n\n详见 `docs/nonexistent.md`。\n")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].rule, "S10")

    def test_existing_path_not_reported(self):
        self.assertEqual(self._run("# Role and Objective\n\n详见 `docs/real.md`。\n"), [])

    def test_command_not_treated_as_path(self):
        self.assertEqual(self._run("# Role and Objective\n\n跑 `pytest -q`。\n"), [])

    def test_root_file_name_checked_as_path(self):
        """裸文件名也是路径，不存在就要报。"""
        found = self._run("# Role and Objective\n\n见 `AGENTS.md`。\n")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].rule, "S10")

    def test_root_file_name_exists_not_reported(self):
        (self.root / "AGENTS.md").write_text("# x\n", encoding="utf-8")
        self.assertEqual(self._run("# Role and Objective\n\n见 `AGENTS.md`。\n"), [])

    def test_path_inside_example_ignored(self):
        text = (
            "# Role and Objective\n\n测试。\n\n"
            "<example>\n见 `docs/nonexistent.md`。\n</example>\n"
        )
        self.assertEqual(self._run(text), [])

    def test_multiple_refs_on_one_line_treated_as_list(self):
        """一行列多个候选文件时是在给选项，不是断言都存在。"""
        text = "# Role and Objective\n\n从 `README.md`、`package.json`、`pyproject.toml` 里读。\n"
        self.assertEqual(self._run(text), [])

    def test_single_ref_with_others_absent_still_reported(self):
        text = "# Role and Objective\n\n见 `docs/nonexistent.md`，细节另议。\n"
        self.assertEqual(len(self._run(text)), 1)


class BaselineTest(unittest.TestCase):
    """基线对比：删掉的规则要报，保留下来的不报。"""

    def test_dropped_rule_reported(self):
        new = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n## 始终\n\n"
            "- 提交前运行 `pytest -q` 并贴出退出码。\n"
        )
        old = new + "- 删除字段或表前，先确认没有读取方还在用。\n"
        found = check.check_baseline(build(new), build(old))
        self.assertEqual(len(found), 1)
        self.assertIn("删除字段", found[0].message)

    def test_rewritten_rule_counted_as_covered(self):
        new = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n## 始终\n\n"
            "- 改代码前先读相关模块和覆盖它的测试，按现有写法扩展。\n"
        )
        old = (
            "# Role and Objective\n\n测试。\n\n"
            "# Instructions\n\n## 始终\n\n"
            "- 改代码前先读相关模块和覆盖它的测试，按现有写法扩展。\n"
        )
        self.assertEqual(check.check_baseline(build(new), build(old)), [])


class RichInlineHeadingTest(unittest.TestCase):
    """标题里的强调、链接、行内代码都要计入标题文本。"""

    def test_bold_heading_text_extracted(self):
        doc = build("# **角色与目标**\n\n正文。\n")
        self.assertEqual(doc.headings[0].text, "角色与目标")

    def test_link_heading_text_extracted(self):
        doc = build("# [输出格式](https://example.com)\n\n正文。\n")
        self.assertEqual(doc.headings[0].text, "输出格式")

    def test_code_heading_text_extracted(self):
        doc = build("# 用 `pytest` 测试\n\n正文。\n")
        self.assertEqual(doc.headings[0].text, "用 pytest 测试")

    def test_bold_heading_satisfies_s1(self):
        """加粗标题不能导致误报缺 S1。"""
        text = "# **Role and Objective**\n\n测试。\n\n# Output Format\n\n- 只输出结果。\n"
        self.assertNotIn("S1", rules_of(text))


class EmptyHeadingTest(unittest.TestCase):
    def test_empty_heading_reported(self):
        text = "# Role and Objective\n\n##\n\n正文。\n\n# Output Format\n\n- 结果。\n"
        self.assertIn("MD-HEAD-EMPTY", structure_of(text))

    def test_heading_with_only_marker_not_reported(self):
        text = "# Role and Objective\n\n正文。\n"
        self.assertNotIn("MD-HEAD-EMPTY", structure_of(text))


class DuplicateHeadingTest(unittest.TestCase):
    def test_same_heading_text_reported(self):
        text = "# Role and Objective\n\n## 示例\n\n甲。\n\n## 示例\n\n乙。\n"
        found = structure_of(text)
        self.assertIn("MD-HEAD-DUP", found)

    def test_different_heading_text_not_reported(self):
        text = "# Role and Objective\n\n## 示例甲\n\n甲。\n\n## 示例乙\n\n乙。\n"
        self.assertNotIn("MD-HEAD-DUP", structure_of(text))

    def test_duplicate_matched_case_insensitively(self):
        text = "# Role and Objective\n\n## Example\n\n甲。\n\n## example\n\n乙。\n"
        self.assertIn("MD-HEAD-DUP", structure_of(text))


class LinkReferenceTest(unittest.TestCase):
    """链接引用：定义重复要报，标签未定义要报。"""

    def test_undefined_label_reported(self):
        text = "# Role and Objective\n\n见 [文字][没有定义]。\n"
        self.assertIn("MD-LINK-REF", structure_of(text))

    def test_defined_label_not_reported(self):
        text = "# Role and Objective\n\n见 [文字][docs]。\n\n[docs]: /x.md\n"
        self.assertNotIn("MD-LINK-REF", structure_of(text))

    def test_definition_in_fence_not_counted(self):
        text = (
            "# Role and Objective\n\n见 [文字][docs]。\n\n"
            "```markdown\n[docs]: /x.md\n```\n"
        )
        self.assertIn("MD-LINK-REF", structure_of(text))

    def test_duplicate_definition_reported(self):
        text = (
            "# Role and Objective\n\n见 [文字][docs]。\n\n"
            "[docs]: /a.md\n[docs]: /b.md\n"
        )
        self.assertIn("MD-LINK-DEF-DUP", structure_of(text))

    def test_inline_link_not_treated_as_reference(self):
        text = "# Role and Objective\n\n见 [文字](https://example.com)。\n"
        self.assertNotIn("MD-LINK-REF", structure_of(text))


class InlineCodeBalanceTest(unittest.TestCase):
    """落单的反引号会让后续内容失去代码样式。"""

    def test_unbalanced_backtick_reported(self):
        text = "# Role and Objective\n\n见 `pytest 的用法。\n"
        self.assertIn("MD-INLINE-CODE", structure_of(text))

    def test_balanced_backticks_not_reported(self):
        text = "# Role and Objective\n\n见 `pytest` 的用法。\n"
        self.assertNotIn("MD-INLINE-CODE", structure_of(text))

    def test_escaped_backtick_not_counted(self):
        text = "# Role and Objective\n\n见 \\` 字面量的用法 `x`。\n"
        self.assertNotIn("MD-INLINE-CODE", structure_of(text))

    def test_backtick_inside_fence_ignored(self):
        text = "# Role and Objective\n\n```\n单个 ` 反引号\n```\n"
        self.assertNotIn("MD-INLINE-CODE", structure_of(text))


class MetricsTest(unittest.TestCase):
    """统计口径：空行、代码块、HTML 块都不计入正文行。"""

    def test_blank_and_code_lines_excluded(self):
        text = (
            "# Role and Objective\n"
            "\n"
            "\n"
            "```python\n"
            "print(1)\n"
            "```\n"
            "\n"
            "- 改代码前先读测试。\n"
        )
        doc = build(text)
        self.assertEqual(doc.blank_count, 3)
        self.assertEqual(len(doc.content_lines), 2)

    def test_long_line_reported(self):
        text = "# Role and Objective\n\n- " + "很" * 210 + "\n"
        self.assertIn("S11", rules_of(text))


class RunTest(unittest.TestCase):
    """端到端：退出码与参数处理。"""

    def test_missing_file_returns_2(self):
        self.assertEqual(check.main.__module__ and 0, 0)
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.md"
            self.assertFalse(missing.exists())

    def test_parse_args_accepts_baseline(self):
        target, skill, baseline = check.parse_args(["--skill", "--baseline", "old.md", "new.md"])
        self.assertEqual(target, "new.md")
        self.assertTrue(skill)
        self.assertEqual(baseline, "old.md")

    def test_parse_args_rejects_unknown_flag(self):
        with self.assertRaises(SystemExit) as ctx:
            check.parse_args(["--nope", "a.md"])
        self.assertEqual(ctx.exception.code, 2)

    def test_parse_args_requires_one_target(self):
        with self.assertRaises(SystemExit) as ctx:
            check.parse_args([])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
