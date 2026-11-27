"""文档结构模型：基于 markdown-it token 流的 Markdown 结构视图。"""

from __future__ import annotations

import re
from dataclasses import dataclass

from markdown_lint.text import (
    count_inline_backticks,
    count_marker,
    count_row_cells,
    strip_inline_code,
    strip_quote_prefix,
)


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

        markdown-it 只给出段落的行范围，不给每个链接的行号，所以按
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
        table_rows = {
            token.map[0] + 1
            for token in self.tokens
            if token.type == "tr_open" and token.map
        }
        written: dict[int, int] = {}
        first_line: dict[int, int] = {}
        for i, line in enumerate(self.raw, 1):
            if i in skip or i in table_rows:
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
