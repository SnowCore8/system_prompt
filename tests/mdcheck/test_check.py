#!/usr/bin/env python3
"""check.py 的自测用例。

用标准库 unittest 编写：
    python3 -B -m unittest discover -s tests/skill -p 'test_*.py'
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "mdcheck"))

import check  # noqa: E402

MD = check.load_markdown_it()
BASE = Path("/nonexistent-base")


def build(text: str) -> check.Doc:
    return check.Doc(text, MD)


def all_findings(text: str, base: Path = BASE) -> list[check.Finding]:
    return check.check_format(build(text), base)


def rules_of(text: str, base: Path = BASE) -> list[str]:
    return [finding.rule for finding in all_findings(text, base)]


def run_main(*args: str) -> tuple[int, str, str]:
    old_argv = sys.argv
    out, err = io.StringIO(), io.StringIO()
    sys.argv = ["check.py", *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check.main()
    finally:
        sys.argv = old_argv
    return code, out.getvalue(), err.getvalue()


class DocParsingTest(unittest.TestCase):
    """Markdown 结构的基本解析。"""

    def test_setext_headings(self):
        text = "Role and Objective\n==================\n\nOutput Format\n-------------\n\n- 结果。\n"
        doc = build(text)
        self.assertEqual(
            [(h.level, h.text) for h in doc.headings],
            [(1, "Role and Objective"), (2, "Output Format")],
        )

    def test_atx_and_setext_mixed(self):
        text = "Role and Objective\n==================\n\n## 子节\n\n正文。\n"
        self.assertEqual([h.level for h in build(text).headings], [1, 2])

    def test_rich_heading_text(self):
        doc = build("# **角色** 与 [目标](https://example.invalid)\n\n正文。\n")
        self.assertEqual(doc.headings[0].text, "角色 与 目标")

    def test_inline_code_in_heading(self):
        doc = build("# 用 `pytest` 测试\n\n正文。\n")
        self.assertEqual(doc.headings[0].text, "用 pytest 测试")

    def test_bom_stripped(self):
        doc = build("\ufeff# 标题\n\n正文。\n")
        self.assertEqual([h.level for h in doc.headings], [1])

    def test_front_matter_skipped(self):
        text = "---\nname: demo\ndescription: 说明\n---\n\n# 标题\n\n正文。\n"
        doc = build(text)
        self.assertEqual(doc.front_matter, {1, 2, 3, 4})
        self.assertEqual([h.text for h in doc.headings], ["标题"])

    def test_blank_line_inside_delimiters_not_front_matter(self):
        text = "---\nname: demo\n\n# 标题\n---\n\n正文。\n"
        self.assertEqual(build(text).front_matter, set())

    def test_thematic_breaks_not_front_matter(self):
        text = "---\n\n# 标题\n\n---\n\n正文\n"
        self.assertEqual(build(text).front_matter, set())

    def test_quote_fence_closed(self):
        text = "> ```text\n> 引用里的围栏\n> ```\n"
        self.assertIsNone(build(text).unclosed)

    def test_indented_code_lines(self):
        text = "# 标题\n\n正文。\n\n    code\n    more\n"
        self.assertEqual(build(text).code_lines, {5, 6})

    def test_table_cells(self):
        text = "| 甲 | 乙 |\n|---|---|\n| 1 | 2 | 3 |\n"
        self.assertEqual([(t.start, t.cols) for t in build(text).tables], [(1, [2, 3])])

    def test_html_block_lines(self):
        text = "# 标题\n\n<div>\n正文\n</div>\n"
        self.assertEqual(build(text).html_lines, {3, 4, 5})

    def test_content_lines_and_blank_count(self):
        text = "# 标题\n\n```\ncode\n```\n\n正文。\n"
        doc = build(text)
        self.assertEqual(doc.blank_count, 2)
        self.assertEqual([line for _, line in doc.content_lines], ["# 标题", "正文。"])


class HeadingTest(unittest.TestCase):
    def test_missing_space_reported(self):
        self.assertIn("MD-HEAD-SPACE", rules_of("# 标题\n\n##没有空格\n"))

    def test_closing_hashes_not_reported(self):
        self.assertNotIn("MD-HEAD-SPACE", rules_of("# 标题\n\n## 子节 ##\n"))

    def test_heading_space_in_fence_ignored(self):
        self.assertNotIn("MD-HEAD-SPACE", rules_of("# 标题\n\n```\n##没有空格\n```\n"))

    def test_first_heading_not_h1(self):
        self.assertIn("MD-HEAD-START", rules_of("## 标题\n\n正文。\n"))

    def test_first_heading_h1(self):
        self.assertNotIn("MD-HEAD-START", rules_of("# 标题\n\n## 子节\n"))

    def test_level_jump(self):
        self.assertIn("MD-HEAD-JUMP", rules_of("# 标题\n\n### 子节\n"))

    def test_normal_levels(self):
        self.assertNotIn("MD-HEAD-JUMP", rules_of("# 标题\n\n## 子节\n\n### 孙节\n"))

    def test_empty_heading(self):
        self.assertIn("MD-HEAD-EMPTY", rules_of("# 标题\n\n##\n\n正文。\n"))

    def test_duplicate_heading_case_insensitive(self):
        text = "# 标题\n\n## Example\n\n甲。\n\n## example\n\n乙。\n"
        self.assertIn("MD-HEAD-DUP", rules_of(text))

    def test_distinct_headings(self):
        self.assertNotIn("MD-HEAD-DUP", rules_of("# 标题\n\n## 甲\n\n## 乙\n"))


class ListTest(unittest.TestCase):
    def test_missing_space_cjk(self):
        self.assertIn("MD-LIST-SPACE", rules_of("# 标题\n\n-项内容。\n"))

    def test_missing_space_latin(self):
        self.assertIn("MD-LIST-SPACE", rules_of("# 标题\n\n1.项内容。\n"))

    def test_glob_flag_negative_not_reported(self):
        for line in ("- 只改 *.py 文件。", "- 用 --flag 参数。", "- 温度 -5 度。"):
            with self.subTest(line=line):
                self.assertNotIn("MD-LIST-SPACE", rules_of(f"# 标题\n\n{line}\n"))

    def test_thematic_break_not_reported(self):
        self.assertNotIn(
            "MD-LIST-SPACE", rules_of("# 标题\n\n- 上一条。\n\n---\n\n- 下一条。\n")
        )

    def test_mixed_marker_same_run(self):
        self.assertIn("MD-LIST-MARKER", rules_of("# 标题\n\n- a\n* b\n"))

    def test_marker_change_between_runs_allowed(self):
        self.assertNotIn("MD-LIST-MARKER", rules_of("# 标题\n\n- a\n\n* b\n"))

    def test_nested_mixed_marker(self):
        self.assertIn("MD-LIST-MARKER", rules_of("# 标题\n\n- a\n  - b\n  * c\n"))

    def test_ordered_list_not_starting_at_one(self):
        self.assertIn("MD-LIST-START", rules_of("# 标题\n\n5. a\n6. b\n"))

    def test_ordered_list_from_one(self):
        self.assertNotIn("MD-LIST-START", rules_of("# 标题\n\n1. a\n2. b\n"))

    def test_empty_list_item(self):
        self.assertIn("MD-LIST-EMPTY", rules_of("# 标题\n\n- \n- b\n"))

    def test_sibling_indent_mismatch(self):
        self.assertIn("MD-LIST-INDENT", rules_of("# 标题\n\n- a\n    - a1\n  - a2\n"))

    def test_too_deep_loses_structure(self):
        self.assertIn("MD-LIST-INDENT", rules_of("# 标题\n\n- a\n      - b\n"))

    def test_valid_indents(self):
        text = "# 标题\n\n- a\n  - b\n\n- c\n   - d\n\n- e\n    - f\n"
        self.assertNotIn("MD-LIST-INDENT", rules_of(text))

    def test_separate_lists_do_not_conflict(self):
        self.assertNotIn("MD-LIST-INDENT", rules_of("# 标题\n\n- a\n  - b\n\n- c\n    - d\n"))

    def test_ordered_deep_indent_ok(self):
        self.assertNotIn("MD-LIST-INDENT", rules_of("# 标题\n\n1. a\n      1. b\n"))

    def test_indented_code_exempt(self):
        self.assertNotIn("MD-LIST-INDENT", rules_of("# 标题\n\n正文。\n\n    - 代码里的\n"))


class TableTest(unittest.TestCase):
    def test_extra_cell(self):
        text = "# 标题\n\n| 甲 | 乙 |\n|---|---|\n| 1 | 2 | 3 |\n"
        self.assertIn("MD-TABLE-COLS", rules_of(text))

    def test_escaped_pipe_not_counted(self):
        text = "# 标题\n\n| 甲 | 乙 |\n|---|---|\n| a \\| b | c |\n"
        self.assertNotIn("MD-TABLE-COLS", rules_of(text))

    def test_unescaped_pipe_in_code_span_is_counted(self):
        text = "# 标题\n\n| 甲 | 乙 |\n|---|---|\n| `x | y` | 2 |\n"
        self.assertIn("MD-TABLE-COLS", rules_of(text))

    def test_missing_delimiter_row(self):
        self.assertIn("MD-TABLE-BROKEN", rules_of("# 标题\n\n|a|b|\n|1|2|\n"))

    def test_short_delimiter_row(self):
        self.assertIn("MD-TABLE-BROKEN", rules_of("# 标题\n\n|a|b|\n|-|\n|1|2|\n"))

    def test_valid_table(self):
        self.assertNotIn("MD-TABLE-BROKEN", rules_of("# 标题\n\n|a|b|\n|-|-|\n|1|2|\n"))

    def test_single_pipe_line(self):
        self.assertNotIn("MD-TABLE-BROKEN", rules_of("# 标题\n\n| 命令 | 说明 |\n"))

    def test_pipe_rows_in_fence(self):
        self.assertNotIn("MD-TABLE-BROKEN", rules_of("# 标题\n\n```\n|a|b|\n|1|2|\n```\n"))

    def test_broken_table_in_quote(self):
        self.assertIn("MD-TABLE-BROKEN", rules_of("> # 标题\n>\n> |a|b|\n> |1|2|\n"))

    def test_valid_table_in_quote(self):
        self.assertNotIn(
            "MD-TABLE-BROKEN", rules_of("> # 标题\n>\n> |a|b|\n> |-|-|\n> |1|2|\n")
        )


class LinkTest(unittest.TestCase):
    def test_undefined_reference(self):
        self.assertIn("MD-LINK-REF", rules_of("# 标题\n\n见 [文字][没有定义]。\n"))

    def test_defined_reference(self):
        text = "# 标题\n\n见 [文字][docs]。\n\n[docs]: https://example.invalid\n"
        self.assertNotIn("MD-LINK-REF", rules_of(text))

    def test_definition_in_fence_not_counted(self):
        text = "# 标题\n\n见 [文字][docs]。\n\n```\n[docs]: /x.md\n```\n"
        self.assertIn("MD-LINK-REF", rules_of(text))

    def test_duplicate_definition(self):
        text = "# 标题\n\n见 [文字][docs]。\n\n[docs]: /a.md\n[docs]: /b.md\n"
        self.assertIn("MD-LINK-DEF-DUP", rules_of(text))

    def test_inline_link_not_reference(self):
        self.assertNotIn(
            "MD-LINK-REF", rules_of("# 标题\n\n见 [文字](https://example.invalid)。\n")
        )

    def test_multiline_definition(self):
        text = "见 [文字][doc]。\n\n[doc]:\n  https://a.invalid\n"
        self.assertNotIn("MD-LINK-REF", rules_of(text))

    def test_definition_inside_list(self):
        text = "见 [文字][doc]。\n\n- [doc]: https://a.invalid\n"
        self.assertNotIn("MD-LINK-REF", rules_of(text))

    def test_collapsed_reference_used(self):
        text = "见 [doc]。\n\n[doc]: https://a.invalid\n"
        self.assertNotIn("MD-LINK-DEF-UNUSED", rules_of(text))

    def test_uppercase_label_matches(self):
        text = "见 [文字][DOC]。\n\n[doc]: https://a.invalid\n"
        self.assertNotIn("MD-LINK-REF", rules_of(text))

    def test_unused_definition(self):
        self.assertIn("MD-LINK-DEF-UNUSED", rules_of("# 标题\n\n[a]: https://a.invalid\n"))

    def test_empty_label(self):
        self.assertIn("MD-LINK-EMPTY", rules_of("# 标题\n\n见 [](https://example.invalid)。\n"))

    def test_empty_target(self):
        self.assertIn("MD-LINK-EMPTY", rules_of("# 标题\n\n见 [文字]()。\n"))

    def test_empty_image_alt(self):
        self.assertIn("MD-LINK-EMPTY", rules_of("# 标题\n\n![](https://example.invalid/a.png)\n"))

    def test_image_wrapped_link_not_empty(self):
        text = "# 标题\n\n[![图](https://example.invalid/a.png)](https://example.invalid/b)\n"
        self.assertNotIn("MD-LINK-EMPTY", rules_of(text))

    def test_broken_link_syntax(self):
        self.assertIn("MD-LINK-SYNTAX", rules_of("# 标题\n\n- 读 [说明](a.md 再改。\n"))

    def test_space_in_target(self):
        self.assertIn("MD-LINK-SYNTAX", rules_of("# 标题\n\n- 读 [说明](my file.md) 再改。\n"))

    def test_valid_link(self):
        self.assertNotIn(
            "MD-LINK-SYNTAX", rules_of("# 标题\n\n- 读 [说明](https://a.invalid) 再改。\n")
        )

    def test_one_good_one_bad_on_same_line(self):
        text = "# 标题\n\n- 读 [好](https://a.invalid) 与 [坏](b.md。\n"
        self.assertIn("MD-LINK-SYNTAX", rules_of(text))

    def test_link_syntax_in_fence_ignored(self):
        text = "# 标题\n\n```\n- 读 [说明](a.md 再改。\n```\n"
        self.assertNotIn("MD-LINK-SYNTAX", rules_of(text))

    def test_valid_link_on_second_line_of_paragraph(self):
        text = "# 标题\n\n第一行。\n第二行 [说明](https://a.invalid)。\n"
        self.assertNotIn("MD-LINK-SYNTAX", rules_of(text))

    def test_broken_link_on_second_line_of_paragraph(self):
        text = "# 标题\n\n第一行。\n第二行 [说明](a.md 再改。\n"
        self.assertIn("MD-LINK-SYNTAX", rules_of(text))

    def test_mixed_links_across_paragraph_lines(self):
        text = "# 标题\n\n第一行 [好](https://a.invalid)。\n第二行 [坏](b.md。\n"
        self.assertIn("MD-LINK-SYNTAX", rules_of(text))


class LinkTargetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "real.md").write_text("# x\n", encoding="utf-8")
        (self.root / "docs" / "我 的.md").write_text("# x\n", encoding="utf-8")
        (self.root / "img").mkdir()
        (self.root / "img" / "a.png").write_text("x", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _rules(self, text: str) -> list[str]:
        return rules_of(text, self.root)

    def test_missing_target(self):
        self.assertIn("MD-LINK-TARGET", self._rules("# 标题\n\n见 [文档](docs/nope.md)。\n"))

    def test_existing_target(self):
        self.assertNotIn("MD-LINK-TARGET", self._rules("# 标题\n\n见 [文档](docs/real.md)。\n"))

    def test_external_target(self):
        self.assertNotIn(
            "MD-LINK-TARGET", self._rules("# 标题\n\n[文档](https://e.invalid/a.md)\n")
        )

    def test_anchor_target_not_checked_here(self):
        self.assertNotIn("MD-LINK-TARGET", self._rules("# 标题\n\n[跳转](#标题)\n"))

    def test_missing_image_target(self):
        self.assertIn("MD-LINK-TARGET", self._rules("# 标题\n\n![图](img/nope.png)\n"))

    def test_existing_image_target(self):
        self.assertNotIn("MD-LINK-TARGET", self._rules("# 标题\n\n![图](img/a.png)\n"))

    def test_percent_encoded_target(self):
        self.assertNotIn(
            "MD-LINK-TARGET", self._rules("# 标题\n\n[文档](docs/我 的.md)\n")
        )

    def test_very_long_target_does_not_crash(self):
        self.assertIn("MD-LINK-TARGET", self._rules("# 标题\n\n[x](" + "a" * 5000 + ")\n"))

    def test_safe_exists_swallows_oserror(self):
        self.assertFalse(check.safe_exists(self.root / ("a" * 5000)))

    def test_resolve_reference_absolute_missing(self):
        self.assertFalse(check.resolve_reference("/definitely/not/here.md", self.root))

    def test_resolve_reference_empty(self):
        self.assertTrue(check.resolve_reference("", self.root))


class AnchorTest(unittest.TestCase):
    def _anchors(self, text: str) -> list[str]:
        return [f.rule for f in check.check_anchors(build(text))]

    def test_valid_cjk_anchor(self):
        self.assertNotIn("MD-ANCHOR", self._anchors("# 输出格式\n\n见 [格式](#输出格式)。\n"))

    def test_wrong_cjk_anchor(self):
        self.assertIn("MD-ANCHOR", self._anchors("# 输出格式\n\n见 [格式](#输出规范)。\n"))

    def test_english_slug(self):
        self.assertNotIn(
            "MD-ANCHOR", self._anchors("## Role and Objective\n\n见 [角色](#role-and-objective)。\n")
        )

    def test_explicit_html_id(self):
        text = '<a id="custom"></a>\n\n# 标题\n\n见 [跳转](#custom)。\n'
        self.assertNotIn("MD-ANCHOR", self._anchors(text))

    def test_duplicate_heading_suffix(self):
        text = "# 甲\n\n# 甲\n\n见 [第二个](#甲-1)。\n"
        self.assertNotIn("MD-ANCHOR", self._anchors(text))

    def test_external_and_top_skipped(self):
        text = "# 标题\n\n见 [外](https://e.invalid) 与 [顶](#top)。\n"
        self.assertNotIn("MD-ANCHOR", self._anchors(text))

    def test_anchor_in_fence_ignored(self):
        text = "# 标题\n\n```\n[跳转](#不存在)\n```\n"
        self.assertNotIn("MD-ANCHOR", self._anchors(text))


class InlineTest(unittest.TestCase):
    def test_unbalanced_backtick(self):
        self.assertIn("MD-INLINE-CODE", rules_of("# 标题\n\n见 `pytest 的用法。\n"))

    def test_balanced_backticks(self):
        self.assertNotIn("MD-INLINE-CODE", rules_of("# 标题\n\n见 `pytest` 的用法。\n"))

    def test_escaped_backtick(self):
        self.assertNotIn("MD-INLINE-CODE", rules_of("# 标题\n\n见 \\` 字面量的用法 `x`。\n"))

    def test_backtick_in_fence(self):
        self.assertNotIn("MD-INLINE-CODE", rules_of("# 标题\n\n```\n单个 ` 反引号\n```\n"))

    def test_multiline_code_span(self):
        doc = build("# 标题\n\n第一行 `abc\n第二行 def` 结束\n")
        self.assertEqual(doc.unclosed_inline, [])

    def test_unclosed_code_span_across_lines_once(self):
        doc = build("# 标题\n\n第一行 `abc\n第二行 def 结束\n")
        self.assertEqual(doc.unclosed_inline, [3])

    def test_unclosed_bold(self):
        self.assertIn("MD-EMPHASIS", rules_of("# 标题\n\n这是 **未闭合。\n"))

    def test_closed_bold(self):
        self.assertNotIn("MD-EMPHASIS", rules_of("# 标题\n\n这是 **加粗** 文字。\n"))

    def test_identifier_inside_code(self):
        self.assertNotIn(
            "MD-EMPHASIS", rules_of("# 标题\n\n调用 `__init__` 和 `_private`。\n")
        )

    def test_escaped_markers(self):
        self.assertNotIn("MD-EMPHASIS", rules_of("# 标题\n\n转义 \\*\\* 两个星号。\n"))

    def test_triple_star(self):
        self.assertNotIn("MD-EMPHASIS", rules_of("# 标题\n\n***粗斜体*** 结束。\n"))

    def test_multiline_emphasis(self):
        doc = build("# 标题\n\n这里有 **加粗\n结束** 文本\n")
        self.assertEqual(doc.unclosed_emphasis, [])

    def test_unclosed_emphasis_across_lines_once(self):
        doc = build("# 标题\n\n这里有 **加粗\n结束 文本\n")
        self.assertEqual(doc.unclosed_emphasis, [(3, "**")])


class InlineHtmlTest(unittest.TestCase):
    def test_unclosed_tag(self):
        self.assertIn("MD-INLINE-HTML", rules_of("# 标题\n\n<b>粗\n"))

    def test_closed_tag(self):
        self.assertNotIn("MD-INLINE-HTML", rules_of("# 标题\n\n<b>粗</b>\n"))

    def test_void_and_self_closing(self):
        text = "# 标题\n\n换行<br>继续 <img src='x' />\n"
        self.assertNotIn("MD-INLINE-HTML", rules_of(text))

    def test_tag_in_fence(self):
        self.assertNotIn("MD-INLINE-HTML", rules_of("# 标题\n\n```\n<b>粗\n```\n"))

    def test_autolink_url(self):
        self.assertNotIn(
            "MD-INLINE-HTML", rules_of("# 标题\n\n见 <https://example.invalid> 说明。\n")
        )

    def test_autolink_email(self):
        self.assertNotIn(
            "MD-INLINE-HTML", rules_of("# 标题\n\n联系 <user@example.invalid>。\n")
        )

    def test_placeholders_ignored(self):
        for line in ("把 <target-file> 换成路径。", "返回 <T> 类型。", "见 <file>。"):
            with self.subTest(line=line):
                self.assertNotIn("MD-INLINE-HTML", rules_of(f"# 标题\n\n{line}\n"))

    def test_uppercase_tag_paired(self):
        self.assertNotIn("MD-INLINE-HTML", rules_of("# 标题\n\n<DIV>x</div>\n"))


class HtmlBlockTest(unittest.TestCase):
    def test_unclosed_block_comment(self):
        text = "# 标题\n\n<!-- 开始\n\n## 被吞掉的标题\n"
        findings = all_findings(text)
        self.assertIn("MD-HTML-COMMENT", [f.rule for f in findings])
        self.assertEqual(
            next(f.level for f in findings if f.rule == "MD-HTML-COMMENT"), check.ERROR
        )

    def test_closed_block_comment(self):
        self.assertNotIn(
            "MD-HTML-COMMENT", rules_of("# 标题\n\n<!-- 注释 -->\n\n正文。\n")
        )

    def test_unclosed_inline_comment(self):
        self.assertIn(
            "MD-HTML-COMMENT", rules_of("# 标题\n\n- 正文 <!-- 注释开始\n- 下一条\n")
        )

    def test_closed_inline_comment(self):
        self.assertNotIn(
            "MD-HTML-COMMENT", rules_of("# 标题\n\n- 正文 <!-- 注释 --> 结束\n")
        )

    def test_unclosed_script(self):
        self.assertIn("MD-HTML-BLOCK", rules_of("<script>\nvar x=1;\n\n# 标题\n"))

    def test_unclosed_style(self):
        self.assertIn("MD-HTML-BLOCK", rules_of("<style>\na{}\n\n# 标题\n"))

    def test_closed_pre(self):
        self.assertNotIn("MD-HTML-BLOCK", rules_of("<pre>\n文字\n</pre>\n\n# 标题\n"))

    def test_self_closing_script(self):
        self.assertNotIn("MD-HTML-BLOCK", rules_of('<script src="x" />\n\n# 标题\n'))


class FormatTest(unittest.TestCase):
    def test_long_prose_line(self):
        self.assertIn("MD-LINE-LEN", rules_of("# 标题\n\n" + "字" * 201 + "\n"))

    def test_exactly_limit(self):
        self.assertNotIn("MD-LINE-LEN", rules_of("# 标题\n\n" + "字" * 200 + "\n"))

    def test_long_table_row_ignored(self):
        self.assertNotIn("MD-LINE-LEN", rules_of("# 标题\n\n| " + "字" * 220 + " |\n"))

    def test_long_fence_line_ignored(self):
        self.assertNotIn("MD-LINE-LEN", rules_of("# 标题\n\n```\n" + "字" * 220 + "\n```\n"))

    def test_long_url_ignored(self):
        text = "# 标题\n\n参见 https://example.invalid/" + "a" * 220 + "\n"
        self.assertNotIn("MD-LINE-LEN", rules_of(text))

    def test_long_front_matter_ignored(self):
        text = "---\ndescription: " + "字" * 220 + "\n---\n\n# 标题\n"
        self.assertNotIn("MD-LINE-LEN", rules_of(text))

    def test_long_html_block_ignored(self):
        text = "# 标题\n\n<div>\n" + "字" * 220 + "\n</div>\n"
        self.assertNotIn("MD-LINE-LEN", rules_of(text))

    def test_two_blank_lines(self):
        self.assertIn("MD-BLANK-RUN", rules_of("# 标题\n\n\n正文\n"))

    def test_one_blank_line(self):
        self.assertNotIn("MD-BLANK-RUN", rules_of("# 标题\n\n正文\n"))

    def test_blank_run_reported_once(self):
        found = [f for f in all_findings("# 标题\n\n\n\n正文\n") if f.rule == "MD-BLANK-RUN"]
        self.assertEqual(len(found), 1)

    def test_blank_lines_in_fence_ignored(self):
        self.assertNotIn("MD-BLANK-RUN", rules_of("# 标题\n\n```\n\n\n```\n"))

    def test_blank_lines_in_html_ignored(self):
        self.assertNotIn("MD-BLANK-RUN", rules_of("# 标题\n\n<pre>\n\n\n</pre>\n"))

    def test_trailing_whitespace(self):
        self.assertIn("MD-TRAILING-WS", rules_of("# 标题\n\n正文。 \n"))

    def test_tab(self):
        self.assertIn("MD-TAB", rules_of("# 标题\n\n正文\t继续。\n"))

    def test_tab_in_fence_ignored(self):
        self.assertNotIn("MD-TAB", rules_of("# 标题\n\n```\n\tx\n```\n"))

    def test_missing_final_newline(self):
        self.assertIn("MD-FINAL-NEWLINE", rules_of("# 标题\n\n正文。"))

    def test_present_final_newline(self):
        self.assertNotIn("MD-FINAL-NEWLINE", rules_of("# 标题\n\n正文。\n"))


class FenceTest(unittest.TestCase):
    def test_unclosed_fence_error(self):
        findings = all_findings("# 标题\n\n```python\nprint(1)\n")
        self.assertIn("MD-FENCE", [f.rule for f in findings])
        self.assertEqual(next(f.level for f in findings if f.rule == "MD-FENCE"), check.ERROR)

    def test_closed_fence(self):
        self.assertNotIn("MD-FENCE", rules_of("# 标题\n\n```python\nprint(1)\n```\n"))


class BomEolTest(unittest.TestCase):
    def test_bom_reported(self):
        self.assertIn("MD-BOM", rules_of("\ufeff# 标题\n\n正文。\n"))

    def test_no_bom_not_reported(self):
        self.assertNotIn("MD-BOM", rules_of("# 标题\n\n正文。\n"))

    def test_mixed_eol_reported(self):
        found = [f for f in all_findings("# 标题\r\n\r\n正文。\n") if f.rule == "MD-EOL"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].line, 3)

    def test_uniform_lf_not_reported(self):
        self.assertNotIn("MD-EOL", rules_of("# 标题\n\n正文。\n"))

    def test_uniform_crlf_not_reported(self):
        self.assertNotIn("MD-EOL", rules_of("# 标题\r\n\r\n正文。\r\n"))


class HeadBlankAfterTest(unittest.TestCase):
    def test_missing_blank_after_reported(self):
        self.assertIn("MD-HEAD-BLANK-AFTER", rules_of("# 标题\n正文。\n"))

    def test_blank_after_not_reported(self):
        self.assertNotIn("MD-HEAD-BLANK-AFTER", rules_of("# 标题\n\n正文。\n"))

    def test_heading_at_end_not_reported(self):
        self.assertNotIn("MD-HEAD-BLANK-AFTER", rules_of("# 标题\n"))

    def test_list_after_heading_not_reported(self):
        self.assertNotIn("MD-HEAD-BLANK-AFTER", rules_of("# 标题\n- a\n"))

    def test_quote_blank_not_reported(self):
        self.assertNotIn("MD-HEAD-BLANK-AFTER", rules_of("> # 标题\n>\n> 正文。\n"))


class FenceLangTest(unittest.TestCase):
    def test_missing_language_reported(self):
        self.assertIn("MD-FENCE-LANG", rules_of("# 标题\n\n```\nx\n```\n"))

    def test_language_present_not_reported(self):
        self.assertNotIn("MD-FENCE-LANG", rules_of("# 标题\n\n```python\nx\n```\n"))


class EmptyLinkDefinitionTest(unittest.TestCase):
    def test_empty_definition_reported(self):
        self.assertIn("MD-LINK-DEF-EMPTY", rules_of("# 标题\n\n[a]:\n"))

    def test_empty_destination_reported(self):
        self.assertIn("MD-LINK-DEF-EMPTY", rules_of("# 标题\n\n[a]: <>\n"))

    def test_multiline_definition_ok(self):
        text = "# 标题\n\n[a]:\n  https://example.invalid\n"
        self.assertNotIn("MD-LINK-DEF-EMPTY", rules_of(text))

    def test_normal_definition_ok(self):
        text = "# 标题\n\n[a]: https://example.invalid\n"
        self.assertNotIn("MD-LINK-DEF-EMPTY", rules_of(text))

    def test_definition_in_fence_ignored(self):
        text = "# 标题\n\n```\n[a]:\n```\n"
        self.assertNotIn("MD-LINK-DEF-EMPTY", rules_of(text))


class BlankBeforeBlockTest(unittest.TestCase):
    def test_list_after_heading_not_reported(self):
        self.assertNotIn("MD-BLANK-BEFORE-BLOCK", rules_of("# 标题\n- a\n"))

    def test_list_after_paragraph_without_blank(self):
        self.assertIn("MD-BLANK-BEFORE-BLOCK", rules_of("正文\n- a\n"))

    def test_list_after_heading_with_blank(self):
        self.assertNotIn("MD-BLANK-BEFORE-BLOCK", rules_of("# 标题\n\n- a\n"))

    def test_heading_after_paragraph_without_blank(self):
        self.assertIn("MD-BLANK-BEFORE-BLOCK", rules_of("正文\n# 标题\n"))

    def test_fence_after_paragraph_without_blank(self):
        self.assertIn("MD-BLANK-BEFORE-BLOCK", rules_of("正文\n```python\nx\n```\n"))

    def test_nested_list_not_reported(self):
        self.assertNotIn("MD-BLANK-BEFORE-BLOCK", rules_of("- a\n  - b\n"))

    def test_heading_in_quote_not_reported(self):
        self.assertNotIn("MD-BLANK-BEFORE-BLOCK", rules_of("> # 标题\n"))

    def test_table_at_start_not_reported(self):
        self.assertNotIn("MD-BLANK-BEFORE-BLOCK", rules_of("|a|b|\n|-|-|\n|1|2|\n"))


class HeadSpacingTest(unittest.TestCase):
    def test_extra_space_after_hash_reported(self):
        self.assertIn("MD-HEAD-MULTI-SPACE", rules_of("#  标题\n"))

    def test_single_space_after_hash_not_reported(self):
        self.assertNotIn("MD-HEAD-MULTI-SPACE", rules_of("# 标题\n"))

    def test_indented_heading_reported(self):
        self.assertIn("MD-HEAD-INDENT", rules_of(" # 标题\n"))

    def test_heading_at_column_zero_not_reported(self):
        self.assertNotIn("MD-HEAD-INDENT", rules_of("# 标题\n"))

    def test_heading_in_quote_not_indented(self):
        self.assertNotIn("MD-HEAD-INDENT", rules_of("> # 标题\n"))


class QuoteSpaceTest(unittest.TestCase):
    def test_missing_space_reported(self):
        self.assertIn("MD-QUOTE-SPACE", rules_of(">引用\n"))

    def test_space_not_reported(self):
        self.assertNotIn("MD-QUOTE-SPACE", rules_of("> 引用\n"))

    def test_nested_quote_not_reported(self):
        self.assertNotIn("MD-QUOTE-SPACE", rules_of(">> 引用\n"))

    def test_empty_quote_not_reported(self):
        self.assertNotIn("MD-QUOTE-SPACE", rules_of(">\n"))


class BlankAfterBlockTest(unittest.TestCase):
    def test_fence_followed_by_text_reported(self):
        self.assertIn("MD-BLANK-AFTER-BLOCK", rules_of("```python\nx\n```\n正文\n"))

    def test_fence_followed_by_blank_not_reported(self):
        self.assertNotIn(
            "MD-BLANK-AFTER-BLOCK", rules_of("```python\nx\n```\n\n正文\n")
        )

    def test_fence_followed_by_heading_not_reported(self):
        self.assertNotIn(
            "MD-BLANK-AFTER-BLOCK", rules_of("```python\nx\n```\n# 标题\n")
        )

    def test_list_with_blank_after_not_reported(self):
        self.assertNotIn("MD-BLANK-AFTER-BLOCK", rules_of("- a\n\n正文\n"))


class FinalBlankTest(unittest.TestCase):
    def test_extra_blank_reported(self):
        self.assertIn("MD-FINAL-BLANK", rules_of("# 标题\n\n正文。\n\n"))

    def test_single_newline_not_reported(self):
        self.assertNotIn("MD-FINAL-BLANK", rules_of("# 标题\n\n正文。\n"))


class LinkTextSpaceTest(unittest.TestCase):
    def test_outer_space_reported(self):
        self.assertIn(
            "MD-LINK-TEXT-SPACE",
            rules_of("[ 文字 ](https://example.invalid)\n"),
        )

    def test_normal_text_not_reported(self):
        self.assertNotIn(
            "MD-LINK-TEXT-SPACE",
            rules_of("[文字](https://example.invalid)\n"),
        )


class FenceStyleTest(unittest.TestCase):
    def test_mixed_style_reported(self):
        text = "```python\nx\n```\n\n~~~python\ny\n~~~\n"
        self.assertIn("MD-FENCE-STYLE", rules_of(text))

    def test_single_style_not_reported(self):
        text = "```python\nx\n```\n\n```python\ny\n```\n"
        self.assertNotIn("MD-FENCE-STYLE", rules_of(text))


class HrStyleTest(unittest.TestCase):
    def test_mixed_style_reported(self):
        self.assertIn("MD-HR-STYLE", rules_of("---\n\n正文\n\n***\n"))

    def test_single_style_not_reported(self):
        self.assertNotIn("MD-HR-STYLE", rules_of("---\n\n正文\n\n---\n"))


class EmphasisStyleTest(unittest.TestCase):
    def test_mixed_em_reported(self):
        self.assertIn("MD-EMPHASIS-STYLE", rules_of("*a* 与 _b_\n"))

    def test_single_em_not_reported(self):
        self.assertNotIn("MD-EMPHASIS-STYLE", rules_of("*a* 与 *b*\n"))

    def test_mixed_strong_reported(self):
        self.assertIn("MD-EMPHASIS-STYLE", rules_of("**a** 与 __b__\n"))

    def test_single_strong_not_reported(self):
        self.assertNotIn("MD-EMPHASIS-STYLE", rules_of("**a** 与 **b**\n"))


class FormatOnlyTest(unittest.TestCase):
    """内容问题不由脚本判断：这是纯格式校验脚本的边界。"""

    def test_content_problems_produce_no_findings(self):
        text = "# 随便\n\n- 只写一句。\n"
        self.assertEqual(all_findings(text), [])

    def test_no_content_check_api(self):
        for name in (
            "check_rules",
            "rule_lines",
            "check_duplicates",
            "check_references",
            "check_baseline",
            "check_structure",
        ):
            with self.subTest(name=name):
                self.assertFalse(hasattr(check, name))


class HelperTest(unittest.TestCase):
    def test_strip_inline_code(self):
        line = "正文：`代码` 结束。"
        stripped = check.strip_inline_code(line)
        self.assertEqual(len(stripped), len(line))
        self.assertNotIn("代码", stripped)

    def test_collapse_label(self):
        self.assertEqual(check.collapse_label("  A   B "), "a b")

    def test_github_slug(self):
        self.assertEqual(check.github_slug("Role and Objective"), "role-and-objective")
        self.assertEqual(check.github_slug("规则 S1–S13"), "规则-s1s13")

    def test_count_row_cells(self):
        self.assertEqual(check.count_row_cells("| a | b |"), 2)
        self.assertEqual(check.count_row_cells("| a \\| b | c |"), 2)
        # GFM 要求代码跨度内的管道也转义，未转义时按分隔符计数
        self.assertEqual(check.count_row_cells("| `x | y` | 2 |"), 3)

    def test_count_inline_backticks(self):
        self.assertEqual(check.count_inline_backticks("`a` 和 \\`"), 2)

    def test_count_marker(self):
        self.assertEqual(check.count_marker("**x**", "**"), 2)
        self.assertEqual(check.count_marker("***x***", "**"), 2)


class CliTest(unittest.TestCase):
    def test_parse_args_strict(self):
        target, strict = check.parse_args(["--strict", "a.md"])
        self.assertEqual(target, "a.md")
        self.assertTrue(strict)

    def test_parse_args_rejects_unknown(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            check.parse_args(["--nope", "a.md"])
        self.assertEqual(ctx.exception.code, 2)

    def test_parse_args_requires_one_target(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            check.parse_args([])
        self.assertEqual(ctx.exception.code, 2)

    def test_help_exits_zero(self):
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            check.parse_args(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_missing_file_returns_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = run_main(str(Path(tmp) / "nope.md"))
        self.assertEqual(code, 2)
        self.assertIn("文件不存在", err)

    def test_clean_file_returns_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("# 标题\n\n正文。\n", encoding="utf-8")
            code, out, _ = run_main(str(path))
        self.assertEqual(code, 0)
        self.assertIn("结果: 通过", out)

    def test_warning_only_returns_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("## 标题\n\n正文。\n", encoding="utf-8")
            code, out, _ = run_main(str(path))
        self.assertEqual(code, 0)
        self.assertIn("MD-HEAD-START", out)

    def test_strict_warning_returns_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("## 标题\n\n正文。\n", encoding="utf-8")
            code, _, _ = run_main("--strict", str(path))
        self.assertEqual(code, 1)

    def test_error_returns_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text("# 标题\n\n```\nx\n", encoding="utf-8")
            code, out, _ = run_main(str(path))
        self.assertEqual(code, 1)
        self.assertIn("MD-FENCE", out)

    def test_invalid_utf8_returns_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_bytes(b"\xff\xfe")
            code, _, err = run_main(str(path))
        self.assertEqual(code, 2)
        self.assertIn("读取失败", err)


if __name__ == "__main__":
    unittest.main()


class TableLinkRegressionTest(unittest.TestCase):
    def test_link_inside_table_row_is_not_broken(self):
        text = "# t\n\n| 步骤 | 动作 |\n|---|---|\n| 发布 | 按 [x.md](x.md) 走发布门 |\n"
        findings = all_findings(text)
        self.assertEqual([f.rule for f in findings if f.rule == "MD-LINK-SYNTAX"], [])
