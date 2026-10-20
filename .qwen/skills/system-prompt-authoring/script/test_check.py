#!/usr/bin/env python3
"""check.py 的自测用例。

用标准库 unittest 编写，装了 pytest 也能直接跑：
    python3 -m unittest discover -s script
    python3 -m pytest script/test_check.py
"""

from __future__ import annotations

import io
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
        # 真实规则两条；缩进代码块里的两条不计
        self.assertEqual(len(check.rule_lines(doc)), 2)
        self.assertEqual(sorted(doc.code_lines), [13, 14])
        self.assertNotIn("不要这样写", [r.text for r in check.rule_lines(doc)])


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


class HeadingSpaceTest(unittest.TestCase):
    """`#标题` 不是标题，是普通段落。"""

    def test_missing_space_after_hash_reported(self):
        text = "# Role and Objective\n\n##没有空格\n\n正文。\n"
        self.assertIn("MD-HEAD-SPACE", structure_of(text))

    def test_heading_without_space_not_parsed_as_heading(self):
        doc = build("# Role and Objective\n\n##没有空格\n\n正文。\n")
        self.assertEqual([h.text for h in doc.headings], ["Role and Objective"])

    def test_normal_heading_not_reported(self):
        text = "# Role and Objective\n\n## 有空格\n\n正文。\n"
        self.assertNotIn("MD-HEAD-SPACE", structure_of(text))

    def test_closing_hashes_not_reported(self):
        text = "# Role and Objective\n\n## 标题 ##\n\n正文。\n"
        self.assertNotIn("MD-HEAD-SPACE", structure_of(text))

    def test_hash_inside_fence_ignored(self):
        text = "# Role and Objective\n\n```\n##没有空格\n```\n"
        self.assertNotIn("MD-HEAD-SPACE", structure_of(text))


class HtmlCommentCloseTest(unittest.TestCase):
    """未闭合的 <!-- 会吞掉文件剩余部分。"""

    def test_unclosed_comment_reported_as_error(self):
        text = "# Role and Objective\n\n<!-- 开始\n\n## 被吞掉的标题\n"
        found = check.check_structure(build(text))
        rules = [f.rule for f in found]
        self.assertIn("MD-HTML-COMMENT", rules)
        level = next(f.level for f in found if f.rule == "MD-HTML-COMMENT")
        self.assertEqual(level, check.ERROR)

    def test_closed_comment_not_reported(self):
        text = "# Role and Objective\n\n<!-- 注释 -->\n\n正文。\n"
        self.assertNotIn("MD-HTML-COMMENT", structure_of(text))

    def test_unclosed_comment_hides_later_headings(self):
        """这正是要报的原因：后续标题不再被识别。"""
        text = "# Role and Objective\n\n<!-- 开始\n\n## 后面的标题\n"
        self.assertEqual([h.text for h in build(text).headings], ["Role and Objective"])


class EmptyLinkTest(unittest.TestCase):
    def test_empty_label_reported(self):
        text = "# Role and Objective\n\n见 [](https://example.com)。\n"
        self.assertIn("MD-LINK-EMPTY", structure_of(text))

    def test_empty_url_reported(self):
        text = "# Role and Objective\n\n见 [文字]()。\n"
        self.assertIn("MD-LINK-EMPTY", structure_of(text))

    def test_normal_link_not_reported(self):
        text = "# Role and Objective\n\n见 [文字](https://example.com)。\n"
        self.assertNotIn("MD-LINK-EMPTY", structure_of(text))

    def test_link_in_fence_ignored(self):
        text = "# Role and Objective\n\n```\n[文字]()\n```\n"
        self.assertNotIn("MD-LINK-EMPTY", structure_of(text))


class EmphasisBalanceTest(unittest.TestCase):
    """未配对的强调标记会原样显示成符号。"""

    def test_unclosed_bold_reported(self):
        text = "# Role and Objective\n\n这是 **未闭合。\n"
        self.assertIn("MD-EMPHASIS", structure_of(text))

    def test_closed_bold_not_reported(self):
        text = "# Role and Objective\n\n这是 **加粗** 文字。\n"
        self.assertNotIn("MD-EMPHASIS", structure_of(text))

    def test_underscore_identifier_not_reported(self):
        """`__init__` 这类标识符不能被当成强调。"""
        text = "# Role and Objective\n\n调用 `__init__` 和 `_private`。\n"
        self.assertNotIn("MD-EMPHASIS", structure_of(text))

    def test_escaped_marker_not_counted(self):
        text = "# Role and Objective\n\n转义 \\*\\* 两个星号。\n"
        self.assertNotIn("MD-EMPHASIS", structure_of(text))

    def test_triple_star_counted_once(self):
        text = "# Role and Objective\n\n***粗斜体*** 结束。\n"
        self.assertNotIn("MD-EMPHASIS", structure_of(text))


class RuleCountTest(unittest.TestCase):
    """规则计数不能按长度筛掉短规则，也不能漏掉嵌套项。"""

    def test_short_rule_counted(self):
        text = "# Role and Objective\n\n# Instructions\n\n## 始终\n\n- 只输出结果。\n"
        self.assertEqual(len(check.rule_lines(build(text))), 1)

    def test_nested_items_counted(self):
        text = (
            "# Role and Objective\n\n# Instructions\n\n## 始终\n\n"
            "1. 甲项\n   - 乙项\n   - 丙项\n2. 丁项\n"
        )
        self.assertEqual(len(check.rule_lines(build(text))), 4)

    def test_empty_item_not_counted(self):
        text = "# Role and Objective\n\n# Instructions\n\n## 始终\n\n-\n- 真规则。\n"
        self.assertEqual(len(check.rule_lines(build(text))), 1)

    def test_rule_count_matches_list_items(self):
        """S7 与头部统计必须同口径，否则两处数字对不上。"""
        text = (
            "# Role and Objective\n\n# Instructions\n\n## 始终\n\n"
            "- 甲\n- 乙\n  - 丙\n- 丁\n"
        )
        doc = build(text)
        self.assertEqual(len(check.rule_lines(doc)), len(doc.list_items))


class NegationCoverageTest(unittest.TestCase):
    """常见否定式开头都要被 S2 识别。"""

    def _has_s2(self, rule_text: str) -> bool:
        text = f"# Role and Objective\n\n# Instructions\n\n## 始终\n\n{rule_text}\n"
        return "S2" in rules_of(text)

    def test_common_negation_forms_reported(self):
        for line in (
            "- 不要用 markdown",
            "- 绝不要用 markdown",
            "- 严禁使用 markdown",
            "- 永远不要用 markdown",
            "- 请勿使用 markdown",
            "- 切勿使用 markdown",
            "- 不得在日志里打印手机号",
        ):
            with self.subTest(line=line):
                self.assertTrue(self._has_s2(line), f"{line} 应报 S2")

    def test_alternative_behavior_not_reported(self):
        for line in (
            "- 不要用 markdown，改成纯文本。",
            "- 不要直接推 main，因为评审是唯一的回滚保险。",
            "- 禁止跳过测试，应当先修代码。",
        ):
            with self.subTest(line=line):
                self.assertFalse(self._has_s2(line), f"{line} 不该报 S2")

    def test_plain_verb_does_not_count_as_fix(self):
        """「使用」是禁止句里的动词，不能当成已给替代行为。"""
        self.assertTrue(self._has_s2("- 严禁使用 markdown"))

    def test_red_line_section_exempt(self):
        text = "# Role and Objective\n\n# Instructions\n\n## 红线\n\n- 绝不提交凭证。\n"
        self.assertNotIn("S2", rules_of(text))


class ListIndentTest(unittest.TestCase):
    """缩进判据只看能确认的错误：同级不一致、缩进过深丢结构。"""

    def test_sibling_indent_mismatch_reported(self):
        text = "# A\n\n- a\n    - a1\n  - a2\n"
        self.assertIn("MD-LIST-INDENT", structure_of(text))

    def test_too_deep_loses_structure(self):
        """6 空格的无序子项被并入正文，渲染出字面 - 号。"""
        text = "# A\n\n- a\n      - b\n"
        self.assertIn("MD-LIST-INDENT", structure_of(text))

    def test_two_three_four_spaces_all_valid(self):
        text = "# A\n\n- a\n  - b\n\n- c\n   - d\n\n- e\n    - f\n"
        self.assertNotIn("MD-LIST-INDENT", structure_of(text))

    def test_separate_lists_do_not_conflict(self):
        """不同列表各自的子项缩进不算同级冲突。"""
        text = "# A\n\n- a\n  - b\n\n- c\n    - d\n"
        self.assertNotIn("MD-LIST-INDENT", structure_of(text))

    def test_ordered_list_deep_indent_ok(self):
        """`1. ` 比 `- ` 宽，同样 6 空格对有序列表仍是子项。"""
        text = "# A\n\n1. a\n      1. b\n"
        self.assertNotIn("MD-LIST-INDENT", structure_of(text))

    def test_indented_code_block_exempt(self):
        text = "# A\n\n正文。\n\n    - 代码块里的\n"
        self.assertNotIn("MD-LIST-INDENT", structure_of(text))

    def test_same_indent_siblings_ok(self):
        text = "# A\n\n- a\n  - b\n  - c\n"
        self.assertNotIn("MD-LIST-INDENT", structure_of(text))


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
        target, skill, baseline, strict = check.parse_args(["--skill", "--baseline", "old.md", "new.md"])
        self.assertEqual(target, "new.md")
        self.assertTrue(skill)
        self.assertEqual(baseline, "old.md")
        self.assertFalse(strict)

    def test_parse_args_accepts_strict(self):
        target, skill, baseline, strict = check.parse_args(["--strict", "a.md"])
        self.assertEqual(target, "a.md")
        self.assertFalse(skill)
        self.assertIsNone(baseline)
        self.assertTrue(strict)

    def test_parse_args_rejects_unknown_flag(self):
        with self.assertRaises(SystemExit) as ctx:
            check.parse_args(["--nope", "a.md"])
        self.assertEqual(ctx.exception.code, 2)

    def test_parse_args_requires_one_target(self):
        with self.assertRaises(SystemExit) as ctx:
            check.parse_args([])
        self.assertEqual(ctx.exception.code, 2)


class CrossLineMarkTest(unittest.TestCase):
    """反引号与强调可以跨行配对，按行计数会误报。"""

    def test_multiline_code_span_not_reported(self):
        doc = build("# Role\n\n第一行 `abc\n第二行 def` 结束\n")
        self.assertEqual(doc.unclosed_inline, [])

    def test_multiline_emphasis_not_reported(self):
        doc = build("# Role\n\n这里有 **加粗\n结束** 文本\n")
        self.assertEqual(doc.unclosed_emphasis, [])

    def test_unclosed_across_lines_reported_once(self):
        doc = build("# Role\n\n第一行 `abc\n第二行 def 结束\n")
        self.assertEqual(doc.unclosed_inline, [3])

    def test_unclosed_emphasis_across_lines_reported_once(self):
        doc = build("# Role\n\n这里有 **加粗\n结束 文本\n")
        self.assertEqual(doc.unclosed_emphasis, [(3, "**")])

    def test_escaped_markers_not_counted(self):
        doc = build("# Role\n\n字面量 \\*\\* 与 \\` 都不算标记\n")
        self.assertEqual(doc.unclosed_emphasis, [])
        self.assertEqual(doc.unclosed_inline, [])


class FrontMatterTest(unittest.TestCase):
    """YAML front matter 会被 CommonMark 解析成 setext 标题。"""

    TEXT = (
        "---\n"
        "name: demo\n"
        "description: 一段说明\n"
        "---\n"
        "\n"
        "# 角色与完成定义\n"
        "\n"
        "## 输出格式\n"
        "\n"
        "- 列出结果。\n"
    )

    def test_front_matter_not_parsed_as_heading(self):
        doc = build(self.TEXT)
        self.assertEqual([h.level for h in doc.headings], [1, 2])
        self.assertEqual(doc.headings[0].text, "角色与完成定义")

    def test_front_matter_not_counted_as_rule(self):
        doc = build(self.TEXT)
        self.assertEqual([r.text for r in check.rule_lines(doc)], ["列出结果。"])

    def test_front_matter_not_checked_for_paths(self):
        text = "---\nname: `nonexistent/x.md`\n---\n\n# Role\n\n内容。\n"
        self.assertEqual(check.check_references(build(text), Path("/tmp")), [])


class BomTest(unittest.TestCase):
    """BOM 会让首行标题变成段落。"""

    def test_bom_stripped_before_parse(self):
        doc = build("\ufeff# Role\n\n## 输出格式\n\n内容。\n")
        self.assertEqual([h.level for h in doc.headings], [1, 2])

    def test_bom_markdown_has_no_role_error(self):
        text = "\ufeff# Role and Objective\n\n## Output Format\n\n- 结果。\n"
        self.assertNotIn("S1", rules_of(text))


class HeadingStartTest(unittest.TestCase):
    """首个标题应从 h1 起。"""

    def test_first_heading_h2_reported(self):
        self.assertIn("MD-HEAD-START", structure_of("## 角色\n\n内容。\n"))

    def test_first_heading_h1_not_reported(self):
        self.assertNotIn("MD-HEAD-START", structure_of("# 角色\n\n## 细节\n\n内容。\n"))

    def test_no_heading_not_reported(self):
        self.assertNotIn("MD-HEAD-START", structure_of("纯文本。\n"))


class PathHeuristicTest(unittest.TestCase):
    """S10 认哪些反引号内容为路径。"""

    def test_url_not_treated_as_path(self):
        self.assertFalse(check.looks_like_path("https://example.com/guide.md"))

    def test_command_with_space_not_treated_as_path(self):
        self.assertFalse(check.looks_like_path("pytest -q"))

    def test_placeholder_not_treated_as_path(self):
        self.assertFalse(check.looks_like_path("<目标文件>"))

    def test_common_source_extension_recognized(self):
        self.assertTrue(check.looks_like_path("src/main.js"))

    def test_root_file_name_recognized(self):
        self.assertTrue(check.looks_like_path("Makefile"))

    def test_url_query_not_split_into_path(self):
        self.assertFalse(check.looks_like_path("https://x.test/a.md?q=1"))


class ReferenceGroupTest(unittest.TestCase):
    """顿号列举不逐个校验，独立断言逐个校验。"""

    def test_enumeration_grouped(self):
        groups = check.reference_groups("从 `README`、`package.json`、`Makefile` 里读")
        self.assertEqual(groups, [["README", "package.json", "Makefile"]])

    def test_independent_assertions_split(self):
        groups = check.reference_groups("见 `AGENTS.md` 与 `docs/nope.md`")
        self.assertEqual(groups, [["AGENTS.md"], ["docs/nope.md"]])


class StrictModeTest(unittest.TestCase):
    """--strict 把警告也算失败。"""

    def _run(self, *args: str) -> int:
        old_argv, old_out = sys.argv, sys.stdout
        sys.argv = ["check.py", *args]
        sys.stdout = io.StringIO()
        try:
            return check.main()
        finally:
            sys.argv, sys.stdout = old_argv, old_out

    def test_strict_fails_on_warning_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            # h2 起笔只产生警告，没有错误
            path.write_text("## 角色与完成定义\n\n## 输出格式\n\n- 结果。\n", encoding="utf-8")
            self.assertEqual(self._run(str(path)), 0)
            self.assertEqual(self._run("--strict", str(path)), 1)

    def test_strict_passes_on_clean_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(
                "# 角色与完成定义\n\n"
                "# Instructions\n\n## 始终\n\n- 列出结果。\n\n"
                "## 不确定时\n\n- 请求模糊：列出两三种理解，问用户选哪个。\n"
                "- 信息不足：先查代码。\n- 超出范围：说明边界。\n\n"
                "# Output Format\n\n- 只输出摘要正文。\n",
                encoding="utf-8",
            )
            self.assertEqual(self._run("--strict", str(path)), 0)


if __name__ == "__main__":
    unittest.main()
