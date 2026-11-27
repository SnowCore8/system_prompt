"""CommonMark 解析器加载。"""

import sys

from markdown_lint.constants import DEPENDENCY


def load_markdown_it():
    """加载 CommonMark 解析器；缺依赖时给出安装命令并返回 None。"""
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        print(f"缺少依赖，请先安装：python3 -m pip install '{DEPENDENCY}'", file=sys.stderr)
        return None
    return MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
