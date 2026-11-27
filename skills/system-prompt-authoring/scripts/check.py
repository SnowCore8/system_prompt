#!/usr/bin/env python3
"""Markdown 格式校验入口：实现位于 markdown_lint 包，本文件保留兼容导出。

用法：python3 check.py [--strict] <目标文件>
退出码：0 无错误；1 有错误；2 参数、依赖或文件问题。
"""

from markdown_lint.checks import check_anchors, check_format
from markdown_lint.cli import main, parse_args
from markdown_lint.constants import ERROR
from markdown_lint.loader import load_markdown_it
from markdown_lint.model import Doc, Finding
from markdown_lint.paths import resolve_reference, safe_exists
from markdown_lint.text import (
    collapse_label,
    count_inline_backticks,
    count_marker,
    count_row_cells,
    github_slug,
    strip_inline_code,
)

__all__ = [
    "Doc",
    "ERROR",
    "Finding",
    "check_anchors",
    "check_format",
    "collapse_label",
    "count_inline_backticks",
    "count_marker",
    "count_row_cells",
    "github_slug",
    "load_markdown_it",
    "main",
    "parse_args",
    "resolve_reference",
    "safe_exists",
    "strip_inline_code",
]

if __name__ == "__main__":
    raise SystemExit(main())
