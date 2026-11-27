"""链接、图片与 HTML 相关的规则检测。"""

from __future__ import annotations

import re
from urllib.parse import unquote

from markdown_lint.constants import (
    HTML_PAIRED_TAGS,
    HTML_VOID_TAGS,
    LINK_DEF_RE,
    LINK_USE_RE,
    URL_RE,
    WARNING,
)
from markdown_lint.model import Doc, Finding
from markdown_lint.text import collapse_label, github_slug, strip_inline_code


def find_link_definitions(doc: Doc) -> tuple[dict[str, int], list[tuple[int, str]]]:
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


def find_used_link_labels(doc: Doc) -> set[str]:
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
    doc: Doc, defined: dict[str, int]
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


def find_empty_link_definitions(doc: Doc) -> list[tuple[int, str]]:
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


def find_unclosed_inline_html(doc: Doc) -> list[tuple[int, str]]:
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
