"""块级结构规则检测：空行、块间距、标题、引用、围栏、强调与分隔线。"""

from __future__ import annotations

import re

from markdown_lint.constants import BLOCK_START_RE
from markdown_lint.model import Doc
from markdown_lint.text import strip_quote_prefix

BLOCK_BEFORE_LABELS = {
    "heading_open": "标题",
    "fence": "代码块",
    "blockquote_open": "引用块",
    "bullet_list_open": "列表",
    "ordered_list_open": "列表",
    "table_open": "表格",
}

BLOCK_AFTER_LABELS = {
    "fence": "代码块",
    "bullet_list_open": "列表",
    "ordered_list_open": "列表",
    "table_open": "表格",
    "blockquote_open": "引用块",
}


def find_long_blank_runs(doc: Doc, limit: int = 2) -> list[int]:
    """连续多个空行；代码块与 HTML 块里的空行不算。"""
    out: list[int] = []
    run = 0
    skip = doc.code_lines | doc.html_lines
    for i, line in enumerate(doc.raw, 1):
        if i in skip or line.strip():
            run = 0
            continue
        run += 1
        if run == limit:
            out.append(i - limit + 1)
    return out


def find_blocks_without_blank_before(doc: Doc) -> list[tuple[int, str]]:
    """找顶层块前缺少空行的情况。"""
    out: list[tuple[int, str]] = []
    skip = doc.front_matter | doc.code_lines | doc.html_lines
    for token in doc.tokens:
        label = BLOCK_BEFORE_LABELS.get(token.type)
        if not label or token.level != 0 or not token.map:
            continue
        start = token.map[0] + 1
        if start <= 1:
            continue
        previous = start - 1
        if previous in skip:
            continue
        previous_text = strip_quote_prefix(doc.raw[previous - 1]).strip()
        if not previous_text:
            continue
        if re.match(r"^#{1,6}\s", previous_text):
            continue
        out.append((start, label))
    return out


def find_blocks_without_blank_after(doc: Doc) -> list[tuple[int, str]]:
    """找顶层块后直接接正文的情况。"""
    out: list[tuple[int, str]] = []
    skip = doc.front_matter | doc.code_lines | doc.html_lines
    for token in doc.tokens:
        label = BLOCK_AFTER_LABELS.get(token.type)
        if not label or token.level != 0 or not token.map:
            continue
        next_index = token.map[1]
        while next_index > token.map[0] and not doc.raw[next_index - 1].strip():
            next_index -= 1
        if next_index >= len(doc.raw):
            continue
        next_line_no = next_index + 1
        if next_line_no in skip:
            continue
        text = strip_quote_prefix(doc.raw[next_index]).strip()
        if not text or BLOCK_START_RE.match(text):
            continue
        out.append((next_line_no, label))
    return out


def find_headings_with_extra_space(doc: Doc) -> list[int]:
    """找 `#` 后用了多个空格的标题。"""
    out: list[int] = []
    skip = doc.code_lines | doc.html_lines
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        text = strip_quote_prefix(line)
        if re.match(r"^#{1,6} {2,}\S", text):
            out.append(i)
    return out


def find_indented_headings(doc: Doc) -> list[int]:
    """找顶层标题前的 1–3 空格缩进。"""
    out: list[int] = []
    for token in doc.tokens:
        if token.type != "heading_open" or token.level != 0 or not token.map:
            continue
        line = token.map[0] + 1
        if re.match(r"^ {1,3}#{1,6}\s", doc.raw[line - 1]):
            out.append(line)
    return out


def find_quote_marker_space(doc: Doc) -> list[int]:
    """找 `>` 后没有空格的引用行。"""
    out: list[int] = []
    skip = doc.code_lines | doc.html_lines
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        text = line.lstrip(" ")
        if len(line) - len(text) > 3:
            continue
        if re.match(r"^>(?=[^\s>])", text):
            out.append(i)
    return out


def find_fence_style_mismatch(doc: Doc) -> list[tuple[int, str]]:
    """找同一文件里混用的反引号与波浪号围栏。"""
    marks: dict[str, int] = {}
    for token in doc.tokens:
        if token.type != "fence" or not token.map:
            continue
        mark = (token.markup or "`")[0]
        marks.setdefault(mark, token.map[0] + 1)
    if len(marks) <= 1:
        return []
    first = next(iter(marks))
    return [(line, mark) for mark, line in marks.items() if mark != first]


def find_emphasis_style_mismatch(doc: Doc) -> list[tuple[int, str, str]]:
    """找同一文件里混用的斜体或粗体标记。"""
    groups: dict[str, dict[str, int]] = {"斜体": {}, "粗体": {}}
    for token in doc.tokens:
        if token.type != "inline" or not token.map:
            continue
        line = token.map[0] + 1
        for child in token.children or []:
            if child.type == "em_open" and child.markup:
                groups["斜体"].setdefault(child.markup, line)
            elif child.type == "strong_open" and child.markup:
                groups["粗体"].setdefault(child.markup, line)
    out: list[tuple[int, str, str]] = []
    for label, marks in groups.items():
        if len(marks) <= 1:
            continue
        first = next(iter(marks))
        for mark, line in marks.items():
            if mark != first:
                out.append((line, label, mark))
    return out


def find_hr_style_mismatch(doc: Doc) -> list[tuple[int, str]]:
    """找同一文件里混用的分隔线样式。"""
    marks: dict[str, int] = {}
    for token in doc.tokens:
        if token.type != "hr" or not token.map:
            continue
        if token.map[0] + 1 in doc.front_matter:
            continue
        mark = (token.markup or "---").strip()
        marks.setdefault(mark, token.map[0] + 1)
    if len(marks) <= 1:
        return []
    first = next(iter(marks))
    return [(line, mark) for mark, line in marks.items() if mark != first]
