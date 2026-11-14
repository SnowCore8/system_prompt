#!/usr/bin/env python3
"""只校验 Markdown 格式。

用法：python3 check.py [--strict] <目标文件>
退出码：0 无错误；1 有错误；2 参数、依赖或文件问题。

解析依赖 markdown-it-py（CommonMark）。脚本不判断内容是否符合任何写作规则。
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

DEPENDENCY = "markdown-it-py==4.2.0"  # 与仓库根 requirements-dev.txt 保持一致

ERROR = "错误"
WARNING = "警告"
SUGGESTION = "建议"

LONG_LINE_LIMIT = 200
LINK_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*\S", re.MULTILINE)
LINK_USE_RE = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")
URL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
BLOCK_START_RE = re.compile(
    r"^(?:#{1,6}\s|```|~~~|\||>|(?:[-*+]|\d+[.)])\s|<[A-Za-z!/])"
)


def load_markdown_it():
    """加载 CommonMark 解析器；缺依赖时给出安装命令并返回 None。"""
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        print(f"缺少依赖，请先安装：python3 -m pip install '{DEPENDENCY}'", file=sys.stderr)
        return None
    return MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")


@dataclass
class Finding:
    level: str
    rule: str
    line: int | None
    message: str
    reason: str
    fix: str


@dataclass
class Heading:
    line: int
    level: int
    text: str


@dataclass
class Table:
    start: int
    cols: list[int]


def strip_quote_prefix(line: str) -> str:
    """去掉引用块的 `>` 前缀，用于按源文本比对围栏与表格。"""
    current = line
    while True:
        stripped = current.lstrip()
        if not stripped.startswith(">"):
            return current
        current = stripped[1:]
        if current.startswith(" "):
            current = current[1:]


def strip_inline_code(line: str) -> str:
    """把行内代码替换成等长空白，保留列位置。"""
    out: list[str] = []
    fence = False
    for ch in line:
        if ch == "`":
            fence = not fence
            out.append(" ")
        elif fence:
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def count_row_cells(line: str) -> int:
    """按 GFM 规则数一行的单元格数：只有反斜杠转义的管道不算分隔符。"""
    text = strip_quote_prefix(line).strip()
    if text.startswith("|"):
        text = text[1:]
    cells = 1
    last_pipe = -1
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            i += 2
            continue
        if text[i] == "|":
            cells += 1
            last_pipe = i
        i += 1
    if last_pipe == len(text) - 1:
        cells -= 1
    return max(cells, 1)


def count_inline_backticks(line: str) -> int:
    """数一行里未转义的反引号个数。"""
    count = 0
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line[i] == "`":
            count += 1
        i += 1
    return count


def count_marker(line: str, marker: str) -> int:
    """数一行里未转义、未被更长标记吞掉的强调标记个数。"""
    count = 0
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line.startswith(marker, i):
            count += 1
            while line.startswith(marker, i):
                i += len(marker)
            continue
        i += 1
    return count


def collapse_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def find_link_definitions(doc: "Doc") -> tuple[dict[str, int], list[tuple[int, str]]]:
    """返回（标签 -> 行号，重复定义列表）。"""
    skip = doc.code_lines | doc.html_lines
    defined: dict[str, int] = {}
    duplicates: list[tuple[int, str]] = []
    for label, info in doc.references.items():
        key = collapse_label(label)
        line = info.get("map", [0, 0])[0] + 1
        if line in skip:
            continue
        defined[key] = line
    label_lines: dict[str, list[int]] = {}
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        text = strip_inline_code(line)
        for match in re.finditer(r"^\s{0,3}\[([^\]]+)\]:", text):
            label_lines.setdefault(collapse_label(match.group(1)), []).append(i)
    for key, lines in label_lines.items():
        for extra in lines[1:]:
            duplicates.append((extra, key))
    return defined, duplicates


def find_used_link_labels(doc: "Doc") -> set[str]:
    """收集被真正用到的引用标签。"""
    used: set[str] = set()
    skip = doc.code_lines | doc.html_lines
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        stripped = strip_inline_code(line)
        if LINK_DEF_RE.match(stripped):
            continue
        for match in LINK_USE_RE.finditer(stripped):
            label = collapse_label(match.group(2) or match.group(1))
            if label:
                used.add(label)
        for match in re.finditer(r"\[([^\]\n]+)\](?![(\[:])", stripped):
            label = collapse_label(match.group(1))
            if label:
                used.add(label)
    return used


def find_undefined_link_refs(
    doc: "Doc", defined: dict[str, int]
) -> list[tuple[int, str]]:
    """找出标签未定义的 `[文字][标签]`。"""
    out: list[tuple[int, str]] = []
    skip = doc.code_lines | doc.html_lines
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        stripped = strip_inline_code(line)
        if LINK_DEF_RE.match(stripped):
            continue
        for match in LINK_USE_RE.finditer(stripped):
            label = collapse_label(match.group(2) or match.group(1))
            if label and label not in defined:
                out.append((i, match.group(0)))
    return out


def find_empty_link_definitions(doc: "Doc") -> list[tuple[int, str]]:
    """找出没有目标地址的链接定义。"""
    out: list[tuple[int, str]] = []
    skip = doc.code_lines | doc.html_lines
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        text = strip_inline_code(line)
        match = re.match(r"^\s{0,3}\[([^\]]*)\]:\s*(.*)$", text)
        if not match:
            continue
        label = match.group(1).strip()
        rest = match.group(2).strip()
        if not label:
            out.append((i, "空标签"))
            continue
        if rest and rest != "<>":
            continue
        if not rest and i < len(doc.raw) and re.match(r"^ {1,3}\S", doc.raw[i]):
            continue
        out.append((i, label))
    return out


def is_external_link(target: str) -> bool:
    """外链、锚点、协议相对地址不查本地存在性。"""
    return (
        not target
        or target.startswith(("#", "//"))
        or bool(URL_RE.match(target))
        or target.startswith("mailto:")
    )


HTML_PAIRED_TAGS = frozenset({
    "a", "abbr", "address", "article", "aside", "b", "bdi", "bdo", "blockquote",
    "caption", "cite", "code", "colgroup", "data", "dd", "del", "details", "dfn",
    "div", "dl", "dt", "em", "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup", "i", "ins", "kbd",
    "label", "legend", "li", "main", "mark", "menu", "nav", "ol", "optgroup",
    "option", "output", "p", "picture", "pre", "q", "rp", "rt", "ruby", "s",
    "samp", "section", "select", "small", "span", "strong", "sub", "summary",
    "sup", "table", "tbody", "td", "tfoot", "th", "thead", "time", "tr", "u",
    "ul", "var",
})
HTML_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})


def find_unclosed_inline_html(doc: "Doc") -> list[tuple[int, str]]:
    """找只开未关的行内 HTML 标签。

    只看解析器产出的 html_inline token：autolink 是 link token，占位符与
    未知标签不在已知标签表里，都不会被误报。
    """
    skip = doc.code_lines | doc.html_lines
    open_tags: dict[str, int] = {}
    for token in doc.tokens:
        if token.type != "inline" or not token.map:
            continue
        line = token.map[0] + 1
        if line in skip:
            continue
        for child in token.children or []:
            if child.type != "html_inline":
                continue
            for match in re.finditer(
                r"<(/?)([A-Za-z][A-Za-z0-9]*)[^>]*>", child.content or ""
            ):
                closing, name = match.group(1), match.group(2).lower()
                if name in HTML_VOID_TAGS or match.group(0).endswith("/>"):
                    continue
                if name not in HTML_PAIRED_TAGS:
                    continue
                if closing:
                    open_tags.pop(name, None)
                else:
                    open_tags.setdefault(name, line)
    return [(line, name) for name, line in open_tags.items()]


def find_long_blank_runs(doc: "Doc", limit: int = 2) -> list[int]:
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


BLOCK_BEFORE_LABELS = {
    "heading_open": "标题",
    "fence": "代码块",
    "blockquote_open": "引用块",
    "bullet_list_open": "列表",
    "ordered_list_open": "列表",
    "table_open": "表格",
}


def find_blocks_without_blank_before(doc: "Doc") -> list[tuple[int, str]]:
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


BLOCK_AFTER_LABELS = {
    "fence": "代码块",
    "bullet_list_open": "列表",
    "ordered_list_open": "列表",
    "table_open": "表格",
    "blockquote_open": "引用块",
}


def find_blocks_without_blank_after(doc: "Doc") -> list[tuple[int, str]]:
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


def find_headings_with_extra_space(doc: "Doc") -> list[int]:
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


def find_indented_headings(doc: "Doc") -> list[int]:
    """找顶层标题前的 1–3 空格缩进。"""
    out: list[int] = []
    for token in doc.tokens:
        if token.type != "heading_open" or token.level != 0 or not token.map:
            continue
        line = token.map[0] + 1
        if re.match(r"^ {1,3}#{1,6}\s", doc.raw[line - 1]):
            out.append(line)
    return out


def find_quote_marker_space(doc: "Doc") -> list[int]:
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


def find_fence_style_mismatch(doc: "Doc") -> list[tuple[int, str]]:
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


def find_emphasis_style_mismatch(doc: "Doc") -> list[tuple[int, str, str]]:
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


def find_hr_style_mismatch(doc: "Doc") -> list[tuple[int, str]]:
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


def github_slug(text: str) -> str:
    """按 GitHub 规则把标题文字转成锚点。"""
    lowered = text.strip().lower()
    kept: list[str] = []
    for ch in lowered:
        if ch.isalnum() or ch in "-_":
            kept.append(ch)
        elif ch.isspace():
            kept.append(" ")
    return "".join(kept).replace(" ", "-")


def safe_exists(path: Path) -> bool:
    """文件系统层查存在，OSError 一律按不存在处理。"""
    try:
        return path.exists()
    except (OSError, ValueError):
        return False


def resolve_reference(ref: str, base: Path) -> bool:
    """把引用解析成本地路径并查存在性。"""
    target = ref.split("#", 1)[0].split("?", 1)[0].strip()
    if not target:
        return True
    try:
        target = unquote(target)
        candidate = Path(target).expanduser()
    except (ValueError, OSError):
        return False
    if candidate.is_absolute():
        return safe_exists(candidate)
    for parent in [base, *list(base.parents)[:5]]:
        if safe_exists(parent / candidate):
            return True
    return False


class Doc:
    """基于 markdown-it token 流的 Markdown 结构视图。"""

    def __init__(self, text: str, md) -> None:
        self.text = text
        self.has_bom = text.startswith("\ufeff")
        self.mixed_eol_line = self._find_mixed_eol_line(text)
        self.raw = [line.replace("\ufeff", "") for line in text.splitlines()]
        self.front_matter = self._detect_front_matter()
        env: dict = {}
        self.tokens = md.parse("\n".join(self.raw), env)
        self.references: dict[str, dict] = env.get("references", {})
        self.headings: list[Heading] = []
        self.fences: list[tuple[int, int, str]] = []
        self.code_lines: set[int] = set(self.front_matter)
        self.html_lines: set[int] = set()
        self.tables: list[Table] = []
        self.list_items: list[tuple[int, int]] = []
        self.list_markers: list[tuple[int, int, bool, str, int | None]] = []
        self.unclosed: tuple[int, str, str] | None = None
        self.unclosed_inline: list[int] = []
        self.unclosed_html: int | None = None
        self.unclosed_raw_html: tuple[int, str] | None = None
        self.unclosed_emphasis: list[tuple[int, str]] = []
        self.links: list[tuple[int, str, str, bool]] = []
        self.missing_heading_space: list[int] = []
        self.heading_starts_deep: Heading | None = None
        self.duplicate_headings: list[tuple[int, str]] = []
        self.list_marker_space: list[int] = []
        self.broken_links: list[tuple[int, str]] = []
        self.unclosed_html_inline: list[int] = []
        self._table_start = 0
        self._walk()
        self._find_duplicate_headings()
        self._find_missing_heading_space()
        self._find_list_marker_space()
        self._find_broken_links()
        self._find_unclosed_html()
        self._find_heading_start()

    @staticmethod
    def _find_mixed_eol_line(text: str) -> int | None:
        """返回第一处与首行不同的换行所在行号；没有混合时返回 None。"""
        endings: list[str] = []
        for line in text.splitlines(keepends=True):
            if line.endswith("\r\n"):
                endings.append("crlf")
            elif line.endswith("\n"):
                endings.append("lf")
            elif line.endswith("\r"):
                endings.append("cr")
            else:
                endings.append("none")
        real = [ending for ending in endings if ending != "none"]
        if len(set(real)) <= 1:
            return None
        first = real[0]
        for i, ending in enumerate(real, 1):
            if ending != first:
                return i
        return None

    def _detect_front_matter(self) -> set[int]:
        """识别文件开头的 YAML front matter，返回其行号集合。"""
        if len(self.raw) < 3 or self.raw[0].strip() != "---":
            return set()
        end = None
        for i in range(1, min(len(self.raw), 200)):
            if self.raw[i].strip() in ("---", "..."):
                end = i
                break
        if end is None:
            return set()
        body = self.raw[1:end]
        if any(not line.strip() for line in body):
            return set()
        if not any(re.match(r"^[A-Za-z_][\w.-]*\s*:", line) for line in body):
            return set()
        return set(range(1, end + 2))

    def _inline_text(self, i: int) -> str:
        """取行内 token 的全部可见文字，标题里的强调与链接也要计入。"""
        if i >= len(self.tokens):
            return ""
        token = self.tokens[i]
        if token.type != "inline":
            return ""
        parts: list[str] = []
        for child in token.children or []:
            if child.type in ("text", "code_inline", "html_inline"):
                parts.append(child.content)
            elif child.type in ("softbreak", "hardbreak"):
                parts.append(" ")
            elif child.type == "image":
                for sub in child.children or []:
                    if sub.type in ("text", "code_inline"):
                        parts.append(sub.content)
        return "".join(parts).strip()

    def _walk(self) -> None:
        tokens = self.tokens
        i = 0
        depth = 0
        in_table = False
        rows: list[int] = []

        while i < len(tokens):
            token = tokens[i]
            kind = token.type

            if token.map and (token.map[0] + 1) in self.front_matter:
                i += 1
                continue

            if kind in ("bullet_list_open", "ordered_list_open"):
                depth += 1
                self.list_markers.append(
                    (
                        token.map[0] + 1 if token.map else 0,
                        depth,
                        token.type == "ordered_list_open",
                        (token.markup or "").strip()
                        or ("." if kind == "ordered_list_open" else "-"),
                        (token.attrs or {}).get("start"),
                    )
                )
            elif kind in ("bullet_list_close", "ordered_list_close"):
                depth -= 1
            elif kind == "list_item_open":
                self.list_items.append(
                    (token.map[0] + 1 if token.map else 0, depth)
                )
            elif kind == "heading_open":
                self.headings.append(
                    Heading(
                        line=token.map[0] + 1 if token.map else 0,
                        level=int(token.tag[1]),
                        text=self._inline_text(i + 1),
                    )
                )
            elif kind == "inline":
                self._scan_inline(i)
                self._scan_links(token)
            elif kind == "fence":
                start, end = token.map[0] + 1, token.map[1]
                self.fences.append((start, end, token.info.strip()))
                self.code_lines.update(range(start, end + 1))
                mark = (token.markup or "`")[0]
                last = (
                    strip_quote_prefix(self.raw[end - 1]).strip()
                    if 0 < end <= len(self.raw)
                    else ""
                )
                if not re.fullmatch(rf"{re.escape(mark)}{{3,}}", last):
                    self.unclosed = (start, token.info.strip(), mark)
            elif kind == "code_block":
                self.code_lines.update(range(token.map[0] + 1, token.map[1] + 1))
            elif kind == "html_block":
                self.html_lines.update(range(token.map[0] + 1, token.map[1] + 1))
            elif kind == "table_open":
                in_table = True
                rows = []
                self._table_start = token.map[0] + 1 if token.map else 0
            elif kind == "tr_open":
                rows.append(token.map[0] + 1 if token.map else 0)
            elif kind == "table_close" and in_table:
                if rows:
                    cols = [
                        count_row_cells(self.raw[n - 1])
                        for n in rows
                        if 0 < n <= len(self.raw)
                    ]
                    self.tables.append(Table(self._table_start, cols))
                in_table = False

            i += 1

    def _scan_links(self, token) -> None:
        """收集行内链接与图片，供链接格式校验使用。"""
        line = token.map[0] + 1 if token.map else 0
        if not line or line in self.code_lines or line in self.html_lines:
            return
        children = token.children or []
        for idx, child in enumerate(children):
            if child.type == "link_open":
                href = (child.attrs or {}).get("href", "")
                label = ""
                for follow in children[idx + 1:]:
                    if follow.type == "link_close":
                        break
                    if follow.type in ("text", "code_inline"):
                        label += follow.content
                    elif follow.type == "image":
                        label += follow.content or ""
                self.links.append((line, label, href, False))
            elif child.type == "image":
                attrs = child.attrs or {}
                self.links.append(
                    (line, child.content or "", attrs.get("src", ""), True)
                )

    def _scan_inline(self, i: int) -> None:
        """校验反引号与强调标记是否配对，按解析器没消化的标记判断。"""
        token = self.tokens[i]
        if not token.map:
            return
        first = token.map[0] + 1
        if first in self.code_lines or first in self.html_lines:
            return
        parts: list[str] = []
        for child in token.children or []:
            if child.type == "text":
                parts.append(child.content)
            elif child.type in ("softbreak", "hardbreak"):
                parts.append("\n")
        leftover = "".join(parts)
        if leftover.count("`") % 2 == 1:
            for offset, raw_line in enumerate(self.raw[token.map[0]:token.map[1]]):
                if count_inline_backticks(raw_line) % 2 == 1:
                    self.unclosed_inline.append(first + offset)
                    break

        for marker in ("**", "__", "~~"):
            if leftover.count(marker) % 2 == 1:
                for offset, raw_line in enumerate(self.raw[token.map[0]:token.map[1]]):
                    if count_marker(strip_inline_code(raw_line), marker) % 2 == 1:
                        self.unclosed_emphasis.append((first + offset, marker))
                        break

    def _find_duplicate_headings(self) -> None:
        seen: dict[str, int] = {}
        for heading in self.headings:
            key = " ".join(heading.text.split()).casefold()
            if not key:
                continue
            if key in seen:
                self.duplicate_headings.append((heading.line, heading.text))
            else:
                seen[key] = heading.line

    def _find_missing_heading_space(self) -> None:
        skip = self.code_lines | self.html_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            if re.match(r"^#{1,6}[^#\s]", line):
                self.missing_heading_space.append(i)

    def _find_list_marker_space(self) -> None:
        skip = self.code_lines | self.html_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            if not re.match(r"^ {0,3}(?:[-*+]|\d+[.)])\S", line):
                continue
            body = line.lstrip()
            if re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", body):
                continue
            if re.match(r"^[-+]\d", body) or re.match(r"^--?[A-Za-z]", body):
                continue
            if re.match(r"^[*_]\S.*[*_]$", body):
                continue
            self.list_marker_space.append(i)

    def _find_broken_links(self) -> None:
        """找没被解析成链接的 `[文字](` 与 `![文字](`。

        markdown-it 只给出段落的行范围，不给每个链接链接的行号，所以按
        段落（inline token）聚合原文匹配数再与已解析数比较；否则多行段落
        里第二行之后的合法链接会被误报。
        """
        ranges: list[tuple[int, int, int]] = []
        for token in self.tokens:
            if token.type != "inline" or not token.map:
                continue
            parsed = sum(
                1 for child in token.children or [] if child.type in ("link_open", "image")
            )
            ranges.append((token.map[0] + 1, token.map[1] + 1, parsed))
        skip = self.code_lines | self.html_lines
        written: dict[int, int] = {}
        first_line: dict[int, int] = {}
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            text = strip_inline_code(line)
            found = len(re.findall(r"!?\[[^\]\n]*\]\(", text))
            if not found:
                continue
            for index, (start, end, _parsed) in enumerate(ranges):
                if start <= i < end:
                    written[index] = written.get(index, 0) + found
                    first_line.setdefault(index, i)
                    break
        for index, (_start, _end, parsed) in enumerate(ranges):
            if written.get(index, 0) > parsed:
                line = first_line[index]
                self.broken_links.append((line, self.raw[line - 1].strip()[:40]))

    def _find_unclosed_html(self) -> None:
        """找未闭合的 HTML 注释、raw-text 块与行内注释。"""
        raw_tags = ("script", "style", "pre", "textarea")
        for token in self.tokens:
            if token.type != "html_block" or not token.map:
                continue
            content = (token.content or "").lstrip()
            start = token.map[0] + 1
            lowered = content.lower()
            if lowered.startswith("<!--") and "-->" not in content:
                self.unclosed_html = start
                return
            for tag in raw_tags:
                if not lowered.startswith(f"<{tag}"):
                    continue
                head = lowered.split(">", 1)[0]
                if head.rstrip().endswith("/"):
                    continue
                if f"</{tag}>" not in lowered:
                    self.unclosed_raw_html = (start, tag)
                    return

        skip = self.code_lines | self.html_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            text = strip_inline_code(line)
            if "<!--" in text and text.count("<!--") > text.count("-->"):
                self.unclosed_html_inline.append(i)

    def _find_heading_start(self) -> None:
        if self.headings and self.headings[0].level > 1:
            self.heading_starts_deep = self.headings[0]

    @property
    def content_lines(self) -> list[tuple[int, str]]:
        """非空且不在代码块、HTML 块与 front matter 内的行。"""
        skip = self.code_lines | self.html_lines
        return [
            (i, line)
            for i, line in enumerate(self.raw, 1)
            if line.strip() and i not in skip
        ]

    @property
    def blank_count(self) -> int:
        return sum(1 for line in self.raw if not line.strip())


def check_anchors(doc: Doc) -> list[Finding]:
    """校验页内锚点是否指向存在的标题或显式 id。"""
    slugs: dict[str, int] = {}
    for heading in doc.headings:
        slug = github_slug(heading.text)
        if slug:
            if slug in slugs:
                n = 1
                while f"{slug}-{n}" in slugs:
                    n += 1
                slugs[f"{slug}-{n}"] = heading.line
            else:
                slugs[slug] = heading.line
    for i, line in enumerate(doc.raw, 1):
        for match in re.finditer(
            r"""<a\s+(?:id|name)\s*=\s*["']([^"']+)["']""",
            strip_inline_code(line),
        ):
            slugs.setdefault(match.group(1).lower(), i)

    findings: list[Finding] = []
    skip = doc.code_lines | doc.html_lines
    for line_no, label, target, is_image in doc.links:
        if is_image or not target.startswith("#") or target in ("#", "#top"):
            continue
        if line_no in skip:
            continue
        anchor = target[1:]
        try:
            anchor = unquote(anchor)
        except (ValueError, OSError):
            pass
        if anchor.lower() in slugs or anchor in slugs:
            continue
        findings.append(
            Finding(
                WARNING,
                "MD-ANCHOR",
                line_no,
                f"页内锚点指向不存在的标题：{target}",
                "锚点对不上时点击不跳转，读者停在原地，而 Markdown 不报错",
                "改成实际标题的锚点（GitHub 规则：小写、空格换连字符、去标点）",
            )
        )
    return findings


def check_format(doc: Doc, base: Path) -> list[Finding]:
    """校验 Markdown 格式，返回全部发现。"""
    findings: list[Finding] = []

    if doc.has_bom:
        findings.append(
            Finding(
                WARNING,
                "MD-BOM",
                1,
                "文件以 BOM 开头",
                "BOM 会让部分编辑器或渲染器把首行标题当成普通文本",
                "保存为无 BOM 的 UTF-8",
            )
        )
    if doc.mixed_eol_line:
        findings.append(
            Finding(
                WARNING,
                "MD-EOL",
                doc.mixed_eol_line,
                "混合使用 CRLF、LF 或 CR 换行",
                "换行不一致会让 diff 噪声变大，部分工具还会按不同行尾处理",
                "统一为 LF 换行",
            )
        )

    defined, duplicate_defs = find_link_definitions(doc)
    for line, label in duplicate_defs:
        findings.append(
            Finding(
                WARNING,
                "MD-LINK-DEF-DUP",
                line,
                f"链接引用重复定义：{label}",
                "同名定义前一条生效、后一条被忽略，改错位置时改动不会起作用",
                "删掉多余的定义，只保留一条",
            )
        )
    for line, label in find_empty_link_definitions(doc):
        findings.append(
            Finding(
                WARNING,
                "MD-LINK-DEF-EMPTY",
                line,
                f"链接定义缺少地址：{label}",
                "定义没有目标时引用它的链接不会成立，渲染器还可能原样显示方括号",
                "补上目标地址：`[标签]: 地址`",
            )
        )
    for line, text in find_undefined_link_refs(doc, defined):
        findings.append(
            Finding(
                WARNING,
                "MD-LINK-REF",
                line,
                f"链接引用的标签未定义：{text}",
                "标签找不到定义时渲染器原样输出方括号，链接不成立",
                "补一行 `[标签]: 地址`，或改成行内链接 `[文字](地址)`",
            )
        )

    used_labels = find_used_link_labels(doc)
    for label, line in defined.items():
        if label in used_labels:
            continue
        findings.append(
            Finding(
                SUGGESTION,
                "MD-LINK-DEF-UNUSED",
                line,
                f"链接定义未被引用：{label}",
                "没人使用的定义只会增加维护负担，改地址时也不会有人发现",
                "删掉这一行，或补上使用它的引用",
            )
        )

    for line, label, target, is_image in doc.links:
        kind = "图片" if is_image else "链接"
        if not label.strip():
            findings.append(
                Finding(
                    WARNING,
                    "MD-LINK-EMPTY",
                    line,
                    f"{kind}缺少文字：{target or '空地址'}",
                    "没有文字的链接在页面上不可见，读者无法判断点向哪里",
                    "补上链接文字；装饰性图片改用 alt 描述",
                )
            )
        elif label != label.strip():
            findings.append(
                Finding(
                    SUGGESTION,
                    "MD-LINK-TEXT-SPACE",
                    line,
                    f"{kind}文字首尾有空白：{label.strip()}",
                    "首尾空白会进入可点击区域，视觉上像排版错误",
                    "删掉文字首尾的空白",
                )
            )
        if not target.strip():
            findings.append(
                Finding(
                    WARNING,
                    "MD-LINK-EMPTY",
                    line,
                    f"{kind}缺少地址：{label or '空文字'}",
                    "空地址点击后没有任何反应，等于死链",
                    "补上目标地址，或去掉链接语法只留文字",
                )
            )
        elif not is_external_link(target) and not resolve_reference(target, base):
            findings.append(
                Finding(
                    WARNING,
                    "MD-LINK-TARGET",
                    line,
                    f"{kind}目标不存在：{target}",
                    "相对路径写错时渲染出来是死链，而 Markdown 不会报错",
                    f"改成实际路径（基准目录 {base}），或改成外链",
                )
            )

    for line, name in find_unclosed_inline_html(doc):
        findings.append(
            Finding(
                WARNING,
                "MD-INLINE-HTML",
                line,
                f"行内标签 <{name}> 没有闭合",
                "标签不闭合时后续内容的样式会被它影响，而 Markdown 不报错",
                f"补上 </{name}>，或删掉这个标签只留文字",
            )
        )

    for line in doc.unclosed_html_inline:
        findings.append(
            Finding(
                WARNING,
                "MD-HTML-COMMENT",
                line,
                "行内 HTML 注释没有闭合",
                "`<!--` 之后没有 `-->` 时注释内容会原样显示在页面上",
                "补上 -->，或删掉这处注释",
            )
        )

    if doc.unclosed_raw_html:
        line, tag = doc.unclosed_raw_html
        findings.append(
            Finding(
                ERROR,
                "MD-HTML-BLOCK",
                line,
                f"<{tag}> 块没有闭合",
                f"未闭合的 <{tag}> 会一路吃到文件末尾，后面的标题与正文全部不渲染",
                f"补上 </{tag}>",
            )
        )

    for line in doc.list_marker_space:
        findings.append(
            Finding(
                WARNING,
                "MD-LIST-SPACE",
                line,
                "列表标记后缺空格，不构成列表项",
                "CommonMark 要求 `-`、`*`、`+`、`1.` 之后至少一个空格，否则整行按段落渲染",
                "在标记后补一个空格",
            )
        )

    for line, snippet in doc.broken_links:
        findings.append(
            Finding(
                WARNING,
                "MD-LINK-SYNTAX",
                line,
                f"链接语法未生效，整段被当成文字：{snippet}",
                "括号没闭合、地址含空格或标题引号没配对时整段退化成文字，页面显示方括号",
                "检查圆括号与引号是否配对；地址含空格时用尖括号包住：`[文字](<my file.md>)`",
            )
        )

    for line in find_long_blank_runs(doc):
        findings.append(
            Finding(
                WARNING,
                "MD-BLANK-RUN",
                line,
                "连续多个空行",
                "一个空行已足够分段，多出的空行只是文件里的空洞，改动时容易误删或多删",
                "删到只留一个空行",
            )
        )

    if doc.unclosed:
        start, info, mark = doc.unclosed
        findings.append(
            Finding(
                ERROR,
                "MD-FENCE",
                start,
                f"代码围栏未闭合（{mark * 3} {info}）",
                "未闭合的围栏会把后续内容全部当成代码，标题与列表失效",
                f"在围栏结束处补一行 {mark * 3}",
            )
        )

    for start, _end, info in doc.fences:
        if info:
            continue
        findings.append(
            Finding(
                SUGGESTION,
                "MD-FENCE-LANG",
                start,
                "代码围栏没有语言标记",
                "没有语言标记时渲染器无法高亮，读者也难以判断代码类型",
                "在围栏后补语言，如 ```python",
            )
        )

    for line, mark in find_fence_style_mismatch(doc):
        findings.append(
            Finding(
                SUGGESTION,
                "MD-FENCE-STYLE",
                line,
                f"代码围栏样式不一致：另用了 {mark * 3}",
                "同一文件混用两种围栏会让源文件风格不统一",
                "统一使用一种围栏：``` 或 ~~~",
            )
        )

    prev: Heading | None = None
    for heading in doc.headings:
        if prev and heading.level > prev.level + 1:
            findings.append(
                Finding(
                    WARNING,
                    "MD-HEAD-JUMP",
                    heading.line,
                    f"标题层级跳跃 h{prev.level} → h{heading.level}",
                    "跳级会让目录结构错乱，读者无法判断归属",
                    f"改为 h{prev.level + 1}，或补齐中间层级",
                )
            )
        prev = heading

    if doc.heading_starts_deep:
        heading = doc.heading_starts_deep
        findings.append(
            Finding(
                WARNING,
                "MD-HEAD-START",
                heading.line,
                f"首个标题是 h{heading.level}，不是 h1",
                "整篇没有一级标题时，目录里缺少总的入口，后续层级也随之整体偏移",
                "把首个标题改为 `#`，其余层级依次上调",
            )
        )

    parsed_table_lines: set[int] = set()
    for token in doc.tokens:
        if token.type == "tr_open" and token.map:
            parsed_table_lines.add(token.map[0] + 1)
    skip_table = doc.code_lines | doc.html_lines
    run: list[int] = []
    for i, raw_line in enumerate(doc.raw + [""], 1):
        stripped = strip_inline_code(strip_quote_prefix(raw_line)).strip()
        is_pipe_row = (
            i <= len(doc.raw) and i not in skip_table and stripped.startswith("|")
        )
        if is_pipe_row:
            run.append(i)
            continue
        if len(run) >= 2 and not any(n in parsed_table_lines for n in run):
            findings.append(
                Finding(
                    WARNING,
                    "MD-TABLE-BROKEN",
                    run[0],
                    f"这 {len(run)} 行像表格，但没有被解析成表格",
                    "分隔行缺列、少横线或含非法字符时整张表退化成段落，竖线原样显示",
                    "分隔行列数必须与表头一致，每列至少三个 -，例如 `| --- | --- |`",
                )
            )
        run = []

    for table in doc.tables:
        cols = table.cols
        if len(set(cols)) > 1:
            expected = max(set(cols), key=cols.count)
            findings.append(
                Finding(
                    WARNING,
                    "MD-TABLE-COLS",
                    table.start,
                    f"表格列数不一致：{cols}",
                    "列数不匹配时多余单元格会被丢弃，渲染结果与源文件不符",
                    f"统一为 {expected} 列，补齐或删掉多余单元格",
                )
            )

    for line in doc.unclosed_inline:
        findings.append(
            Finding(
                WARNING,
                "MD-INLINE-CODE",
                line,
                "行内代码的反引号没有配对",
                "落单的 ` 会被渲染成字面量，后面的内容不会按代码样式显示",
                "补齐反引号，或用转义 \\` 表示字面量",
            )
        )

    if doc.unclosed_html:
        findings.append(
            Finding(
                ERROR,
                "MD-HTML-COMMENT",
                doc.unclosed_html,
                "HTML 注释没有闭合",
                "未闭合的 <!-- 会一直吃到文件末尾，后面的标题和正文全部不渲染",
                "在注释结束处补 -->",
            )
        )

    for line, marker in doc.unclosed_emphasis:
        findings.append(
            Finding(
                WARNING,
                "MD-EMPHASIS",
                line,
                f"强调标记 {marker} 没有配对",
                "未配对的标记会原样显示成符号，读者看到的是星号而不是加粗",
                f"补齐 {marker}，或用转义 \\{marker[0]} 表示字面量",
            )
        )

    for line, label, mark in find_emphasis_style_mismatch(doc):
        findings.append(
            Finding(
                SUGGESTION,
                "MD-EMPHASIS-STYLE",
                line,
                f"{label}样式不一致：另用了 {mark}",
                "同一文件混用两种标记会让源文件风格不统一",
                f"统一使用一种{label}标记",
            )
        )

    for line in doc.missing_heading_space:
        findings.append(
            Finding(
                WARNING,
                "MD-HEAD-SPACE",
                line,
                "`#` 后缺空格，不构成标题",
                "CommonMark 要求 # 后至少一个空格，否则整行按普通段落渲染，目录里不会出现",
                "在 # 后补一个空格",
            )
        )

    for line in find_headings_with_extra_space(doc):
        findings.append(
            Finding(
                WARNING,
                "MD-HEAD-MULTI-SPACE",
                line,
                "标题的 `#` 后有多个空格",
                "多个空格不影响渲染，但同一文件里空格数不一致会让源文件显得随意",
                "改为一个空格",
            )
        )

    for line in find_indented_headings(doc):
        findings.append(
            Finding(
                SUGGESTION,
                "MD-HEAD-INDENT",
                line,
                "标题前有缩进",
                "标题缩进不参与列表层级，只会让源文件结构看起来不一致",
                "把标题移到行首",
            )
        )

    for line in find_quote_marker_space(doc):
        findings.append(
            Finding(
                SUGGESTION,
                "MD-QUOTE-SPACE",
                line,
                "引用标记后缺空格",
                "`>text` 虽然能渲染，但和同文件里的 `> text` 不一致",
                "在 > 后补一个空格",
            )
        )

    for line, text in doc.duplicate_headings:
        findings.append(
            Finding(
                WARNING,
                "MD-HEAD-DUP",
                line,
                f"标题重名：{text}",
                "同名标题的锚点冲突，目录和页内跳转只会落到第一个",
                "改成可区分的标题，或把第二个降级为正文",
            )
        )

    for heading in doc.headings:
        if heading.line >= len(doc.raw):
            continue
        next_line = strip_quote_prefix(doc.raw[heading.line]).strip()
        if not next_line or BLOCK_START_RE.match(next_line):
            continue
        findings.append(
            Finding(
                SUGGESTION,
                "MD-HEAD-BLANK-AFTER",
                heading.line,
                "标题后缺少空行",
                "标题紧接正文时源文件难读，部分目录生成器也会把后续内容并进标题",
                "在标题后补一个空行",
            )
        )

    for heading in doc.headings:
        if not heading.text:
            findings.append(
                Finding(
                    WARNING,
                    "MD-HEAD-EMPTY",
                    heading.line,
                    "标题为空",
                    "空标题在目录里显示为空白行，读者无法判断这一节讲什么",
                    "补上标题文字，或删掉这一行",
                )
            )

    prev_line = 0
    prev_depth = 0
    markers_by_depth: dict[tuple[int, bool], tuple[str, int]] = {}
    for line, depth, ordered, marker, start in doc.list_markers:
        if line > prev_line + 1 or depth < prev_depth:
            markers_by_depth.clear()
        key = (depth, ordered)
        seen = markers_by_depth.get(key)
        if seen and seen[0] != marker:
            findings.append(
                Finding(
                    WARNING,
                    "MD-LIST-MARKER",
                    line,
                    f"同段列表标记不一致：深度 {depth} 用了 {seen[0]} 与 {marker}",
                    "不同的标记会被解析成并列的多个列表，间距与后续编号会断开",
                    f"统一用 {seen[0]}",
                )
            )
        else:
            markers_by_depth[key] = (marker, line)
        prev_line, prev_depth = line, depth
        if ordered and start not in (None, 1):
            findings.append(
                Finding(
                    WARNING,
                    "MD-LIST-START",
                    line,
                    f"有序列表从 {start} 开始编号",
                    "改写或增删条目后编号与实际顺序不一致，读者会按编号理解优先级",
                    "改为从 1 开始，或在正文里说明这是续接上一段编号",
                )
            )

    declared_items = {line for line, _ in doc.list_items}
    inline_first_lines = {
        token.map[0] + 1
        for token in doc.tokens
        if token.type == "inline" and token.map
    }
    for line in declared_items:
        if line in inline_first_lines:
            continue
        if not 0 < line <= len(doc.raw):
            continue
        if re.match(r"^\s*(?:[-*+]|\d+[.)])\s*$", doc.raw[line - 1]):
            findings.append(
                Finding(
                    WARNING,
                    "MD-LIST-EMPTY",
                    line,
                    "列表项没有内容",
                    "空列表项只渲染出一个符号，读者会以为是漏写",
                    "补上内容，或删掉这一行",
                )
            )

    indent_by_depth: dict[int, int] = {}
    prev_depth = 0
    for line, depth in doc.list_items:
        if not 0 < line <= len(doc.raw):
            continue
        raw_line = doc.raw[line - 1]
        indent = len(raw_line) - len(raw_line.lstrip())
        if depth < prev_depth:
            for stale in [d for d in indent_by_depth if d > depth]:
                del indent_by_depth[stale]
        if depth > 1:
            sibling = indent_by_depth.get(depth)
            if sibling is not None and sibling != indent:
                findings.append(
                    Finding(
                        WARNING,
                        "MD-LIST-INDENT",
                        line,
                        f"同级列表项缩进不一致：{sibling} 与 {indent}",
                        "同级缩进不同时，解析器可能把后一项降为正文或提为上一级",
                        f"统一为 {sibling} 空格",
                    )
                )
        indent_by_depth[depth] = indent
        prev_depth = depth

    parsed_lines = {line for line, _ in doc.list_items}
    skip = doc.code_lines | doc.html_lines
    for i, raw_line in enumerate(doc.raw, 1):
        if i in skip or i in parsed_lines:
            continue
        if not re.match(r"^\s{4,}(?:[-*+]|\d+[.)])\s+\S", raw_line):
            continue
        findings.append(
            Finding(
                WARNING,
                "MD-LIST-INDENT",
                i,
                "缩进过深，这一行没被当成列表项",
                "解析器把超过 4 空格的缩进并入上一项正文，列表结构丢失，- 号会原样显示",
                "缩进减到 2–4 空格，或与前一项对齐",
            )
        )

    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        stripped_line = strip_quote_prefix(line).strip()
        if not stripped_line or stripped_line.startswith("|"):
            continue
        if "http://" in line or "https://" in line:
            continue
        if len(line) > LONG_LINE_LIMIT:
            findings.append(
                Finding(
                    WARNING,
                    "MD-LINE-LEN",
                    i,
                    f"单行超过 {LONG_LINE_LIMIT} 字",
                    "过长单行不利于 diff 审查与定位，窄窗口还会横向滚动",
                    f"按句子拆行，每行不超过 {LONG_LINE_LIMIT} 字；表格、代码、URL 与 front matter 除外",
                )
            )

    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        if line != line.rstrip():
            findings.append(
                Finding(
                    WARNING,
                    "MD-TRAILING-WS",
                    i,
                    "行尾空白",
                    "Markdown 中行尾两个空格是强制换行，多余空白会意外改变渲染",
                    "删除行尾空白",
                )
            )
        if "\t" in line:
            findings.append(
                Finding(
                    WARNING,
                    "MD-TAB",
                    i,
                    "含制表符",
                    "制表符宽度依渲染器而变，缩进会错位",
                    "改为空格",
                )
            )

    for line, label in find_blocks_without_blank_before(doc):
        findings.append(
            Finding(
                SUGGESTION,
                "MD-BLANK-BEFORE-BLOCK",
                line,
                f"{label}前缺少空行",
                "块紧接上一段时源文件难读，部分渲染器也可能把两块并在一起",
                "在块前补一个空行",
            )
        )

    for line, label in find_blocks_without_blank_after(doc):
        findings.append(
            Finding(
                SUGGESTION,
                "MD-BLANK-AFTER-BLOCK",
                line,
                f"{label}后直接接正文",
                "块后没有空行时源文件难读，列表或引用还可能把下一行当成续行",
                "在块后补一个空行",
            )
        )

    for line, mark in find_hr_style_mismatch(doc):
        findings.append(
            Finding(
                SUGGESTION,
                "MD-HR-STYLE",
                line,
                f"分隔线样式不一致：另用了 {mark}",
                "同一文件混用不同分隔线会让源文件风格不统一",
                "统一使用一种分隔线：---、*** 或 ___",
            )
        )

    if doc.text.endswith("\n\n"):
        findings.append(
            Finding(
                WARNING,
                "MD-FINAL-BLANK",
                len(doc.raw),
                "文件末尾有多余空行",
                "文件已经以换行结尾，再留空行只会增加 diff 噪音",
                "删掉末尾多余空行，只保留一个换行",
            )
        )

    if not doc.text.endswith("\n"):
        findings.append(
            Finding(
                ERROR,
                "MD-FINAL-NEWLINE",
                len(doc.raw),
                "文件末尾缺少换行",
                "POSIX 文本约定要求文件以换行结尾，否则追加内容时与末行粘连",
                "在文件末尾补一个换行",
            )
        )

    return findings


USAGE = "用法: python3 check.py [--strict] <目标文件>"


def parse_args(argv: list[str]) -> tuple[str, bool]:
    positional: list[str] = []
    strict = False
    for arg in argv:
        if arg in ("-h", "--help"):
            print(USAGE)
            raise SystemExit(0)
        if arg == "--strict":
            strict = True
        elif arg.startswith("--"):
            print(f"未知参数: {arg}", file=sys.stderr)
            raise SystemExit(2)
        else:
            positional.append(arg)
    if len(positional) != 1:
        print(USAGE, file=sys.stderr)
        raise SystemExit(2)
    return positional[0], strict


def main() -> int:
    target, strict = parse_args(sys.argv[1:])
    path = Path(target)
    if not path.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        return 2

    md = load_markdown_it()
    if md is None:
        return 2

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"读取失败: {path}: {exc}", file=sys.stderr)
        return 2

    doc = Doc(text, md)
    findings = check_format(doc, path.resolve().parent) + check_anchors(doc)
    order = {ERROR: 0, WARNING: 1, SUGGESTION: 2}
    findings.sort(key=lambda f: (order[f.level], f.line or 0))

    longest = max(
        ((len(line), i) for i, line in doc.content_lines), default=(0, 0)
    )
    print(
        f"文件 {path} | 行数 {len(doc.content_lines)}"
        f"（不含空行、代码块、HTML 块与 front matter，空行 {doc.blank_count}）"
        f" | 标题 {len(doc.headings)} 个 | 围栏 {len(doc.fences)} 个"
        f" | 表格 {len(doc.tables)} 个 | 链接 {len(doc.links)} 个"
    )
    print(f"最长行 {longest[0]} 字（{'L' + str(longest[1]) if longest[1] else '无'}）")
    print()

    for level in (ERROR, WARNING, SUGGESTION):
        items = [finding for finding in findings if finding.level == level]
        print(f"[{level}] {len(items)} 项")
        for finding in items:
            where = f"L{finding.line}" if finding.line else "全文"
            print(f"  - {where}  {finding.rule}  {finding.message}")
            print(f"      原因：{finding.reason}")
            print(f"      建议：{finding.fix}")
        print()

    errors = sum(1 for finding in findings if finding.level == ERROR)
    warnings = sum(1 for finding in findings if finding.level == WARNING)
    failed = errors + warnings > 0 if strict else errors > 0
    print(
        "结果:",
        "失败" if failed else "通过",
        "（严格模式：警告也计失败）" if strict else "",
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
