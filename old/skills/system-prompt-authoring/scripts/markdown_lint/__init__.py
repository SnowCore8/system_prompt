"""Markdown 格式校验器：只校验格式，不判断内容是否符合写作规则。"""

from markdown_lint.checks import check_anchors, check_format
from markdown_lint.model import Doc, Finding

__all__ = ["Doc", "Finding", "check_anchors", "check_format"]
