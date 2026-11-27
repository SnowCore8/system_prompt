"""共享常量与正则。"""

import re

DEPENDENCY = "markdown-it-py==4.3.0"  # 与仓库根 requirements-dev.txt 保持一致

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
