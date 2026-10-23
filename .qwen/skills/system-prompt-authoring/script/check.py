#!/usr/bin/env python3
"""按 Markdown 结构与 S1–S13 规则检查 agent 指令文件。

用法：python3 check.py [--skill] [--baseline <旧文件>] <目标文件>
退出码：0 无错误；1 有错误；2 参数、依赖或文件问题。

结构解析依赖 markdown-it-py（CommonMark）。未安装时自动安装。
输出分三级：错误（退出码 1）、警告、建议。
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import unquote

DEPENDENCY = "markdown-it-py>=3,<4"

ERROR = "错误"
WARNING = "警告"
SUGGESTION = "建议"

PLACEHOLDER_RE = re.compile(r"^\W*(待补充|TBD|FIXME)\W*$")
PRIORITY_RE = re.compile(r"(编号|数字)(小|大)?的?(赢|优先)|(?:^|[^A-Za-z])(L|第)\s*\d+\s*条优先")
REFUTE_RE = re.compile(r"无效|不成立|不要|不得|禁止|不能|避免|不算|反例")
# 判断「只禁不导」时认的替代行为与理由标记。
# 不收「使用」「同时」「并在」这类纯动词/连词：它们会出现在禁止句本身
# （「不要使用 markdown」），命中就把整条规则放过了。
FIX_HINT_RE = re.compile(r"而是|改为|改成|应当|应该|因为|原因|避免|防止|改用|写成|以便|从而|否则")
LIST_MARKER_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
CONTRAST_PAIRS = (
    ("必须全面", "必须简洁"),
    ("必须详细", "必须简短"),
    ("必须完整", "必须精简"),
)
CHECKABLE_EXT = (
    ".md", ".py", ".json", ".toml", ".yaml", ".yml", ".txt", ".cfg", ".ini", ".sh",
    ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt",
    ".c", ".h", ".cc", ".cpp", ".hpp", ".rb", ".php", ".cs", ".swift", ".scala",
    ".sql", ".proto", ".graphql", ".html", ".css", ".scss", ".xml", ".csv",
    ".ipynb", ".lock", ".conf", ".properties", ".gradle", ".cmake", ".mk",
)
# 无扩展名但确实是文件的根级名字。只认这些，避免把 `make`、`pytest -q`
# 这类命令当成路径。
ROOT_FILE_NAMES = (
    "Makefile", "makefile", "GNUmakefile", "Dockerfile", "Containerfile",
    "Jenkinsfile", "Procfile", "Rakefile", "Gemfile", "Vagrantfile",
    "README", "readme", "CONTRIBUTING", "SECURITY", "CODEOWNERS",
    "requirements.txt", "LICENSE", "NOTICE", "AUTHORS", "CHANGELOG",
)
# 反引号里这些形状的不是本地路径，不查存在性。
URL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
LONG_LINE_LIMIT = 200
EXAMPLE_RULE_THRESHOLD = 50
DUP_JACCARD = 0.6
DUP_RATIO = 0.75
DUP_MIN_LENGTH = 8
BASE_COVERAGE = 0.5


def load_markdown_it():
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        print(f"缺少依赖，正在安装 {DEPENDENCY} ……", file=sys.stderr)
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", DEPENDENCY],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(f"安装失败，请手动执行: pip install '{DEPENDENCY}'", file=sys.stderr)
            print(proc.stderr.strip()[-400:], file=sys.stderr)
            return None
        try:
            from markdown_it import MarkdownIt
        except ImportError:
            print("安装后仍无法导入 markdown_it", file=sys.stderr)
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


@dataclass
class RuleLine:
    line: int
    text: str
    section: str


def strip_quote_prefix(line: str) -> str:
    """去掉引用块的 `>` 前缀，用于按源文本比对围栏。"""
    current = line
    while True:
        stripped = current.lstrip()
        if not stripped.startswith(">"):
            return current
        current = stripped[1:]
        if current.startswith(" "):
            current = current[1:]


def strip_inline_code(line: str) -> str:
    """把行内代码替换成等长空白，保留列位置，避免里面的规则词被当成正文。"""
    out = []
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
    """按 GFM 规则数一行的单元格数，跳过转义管道与行内代码里的管道。

    解析器会直接丢弃超出表头列数的单元格，只能从源文本发现这种不一致。
    """
    text = strip_quote_prefix(line).strip()
    if text.startswith("|"):
        text = text[1:]
    cells = 1
    in_code = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        elif ch == "|" and not in_code:
            cells += 1
        i += 1
    if not in_code and text.endswith("|") and not text.endswith("\\|"):
        cells -= 1
    return cells


def count_inline_backticks(line: str) -> int:
    """数一行里未转义的反引号个数，用于发现落单的 `。"""
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


LINK_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*\S", re.MULTILINE)
LINK_USE_RE = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")
# 常见否定式开头。漏掉「严禁」「请勿」「永远不要」会让 S2 整条规则失效
NEGATION_RE = re.compile(
    r"^(?:绝不要|绝对不要|永远不要|千万不要|严禁|请勿|切勿|不要|绝不|禁止|不得|不准|不能)"
)


def count_marker(line: str, marker: str) -> int:
    """数一行里未转义、未被更长标记吞掉的强调标记个数。"""
    count = 0
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line.startswith(marker, i):
            # 三个星号是 *** 粗斜体，按一个标记算，避免奇偶判断被它带偏
            count += 1
            while line.startswith(marker, i):
                i += len(marker)
            continue
        i += 1
    return count


def find_link_definitions(doc: "Doc") -> tuple[dict[str, int], list[tuple[int, str]]]:
    """返回 (标签 -> 行号, 重复定义列表)。标签按 CommonMark 规则折叠大小写与空白。

    必须跳过代码块、HTML 块与示例区：围栏里写的 `[x]: /a` 只是示例，不构成定义。

    不能只认单行正则：地址写在下一行（缩进续行）、定义写在列表项里，
    两种都是合法的 CommonMark，正则一条都匹配不到，会让 MD-LINK-REF
    把真正定义过的标签报成未定义。解析器自己的 `env.references`
    里已经有折叠后的标签与行号，直接用它，重复定义再按行号归类。
    """
    skip = doc.code_lines | doc.html_lines | doc.example_lines
    defined: dict[str, int] = {}
    duplicates: list[tuple[int, str]] = []
    for label, info in doc.references.items():
        # 解析器的键是大写化的（`[doc]` 存成 `DOC`），其余地方统一用
        # collapse_label 的折叠形式，这里转回去，否则一律判成未定义
        key = collapse_label(label)
        line = info.get("map", [0, 0])[0] + 1
        if line in skip:
            continue
        defined[key] = line
    # 解析器把重复标签折叠成第一条，重复定义要自己按源行找。
    # 判据：同一标签在源文本里出现了不止一次定义行。
    label_lines: dict[str, list[int]] = {}
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        text = strip_inline_code(line)
        for m in re.finditer(r"^\s{0,3}\[([^\]]+)\]:", text):
            label_lines.setdefault(collapse_label(m.group(1)), []).append(i)
    for key, lines in label_lines.items():
        for extra in lines[1:]:
            duplicates.append((extra, key))
    return defined, duplicates


def is_external_link(target: str) -> bool:
    """外链、锚点、协议相对地址不查本地存在性。"""
    return (
        not target
        or target.startswith(("#", "//"))
        or bool(URL_RE.match(target))
        or target.startswith("mailto:")
    )


def collapse_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def find_used_link_labels(doc: "Doc") -> set[str]:
    """收集被真正用到的引用标签，用于发现没人使用的定义。

    `[文字][标签]`、`[标签][]` 与 collapsed 的 `[标签]` 三种写法都能确认
    意图，但只有前两种能从源文本正则认出。第三种（`[标签]` 后面什么都不跟）
    与普通方括号无法区分，必须看解析器：它把这些全解析成了 link token。
    以「定义了的标签里，哪些没在解析出的链接文字里出现」判断更稳：
    这里收集的是所有出现在链接位置上的原文标签候选。
    """
    used: set[str] = set()
    skip = doc.code_lines | doc.html_lines | doc.example_lines
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
        # collapsed / shortcut：`[标签]` 后面不是 `(`、`[`、`:`
        for match in re.finditer(r"\[([^\]\n]+)\](?![(\[:])", stripped):
            label = collapse_label(match.group(1))
            if label:
                used.add(label)
    return used


def find_undefined_link_refs(doc: "Doc", defined: dict[str, int]) -> list[tuple[int, str]]:
    """找出标签未定义的 `[文字][标签]`。未定义时它会原样显示成字面量。

    只查 `[文字][标签]` 与 `[标签][]` 两种显式写法。`[标签]` 这种 shortcut
    在没定义时本来就是普通方括号（“见 [备注]”），报出来全是噪声。
    """
    out: list[tuple[int, str]] = []
    skip = doc.code_lines | doc.html_lines | doc.example_lines
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


def normalize_for_compare(text: str) -> str:
    """去掉列表符号、标点与空白，只留下可比较的实词序列。"""
    text = strip_inline_code(text)
    text = LIST_MARKER_RE.sub(r"\1", text)
    return re.sub(r"[\s，。、；：！？,.;:!?（）()《》「」『』\"'`]+", "", text)


def bigrams(text: str) -> set[str]:
    if len(text) < 2:
        return {text} if text else set()
    return {text[i : i + 2] for i in range(len(text) - 1)}


def containment(small: set[str], big: set[str]) -> float:
    """小集合有多少比例落在大集合里，用于识别被合并进长句的旧规则。"""
    if not small:
        return 0.0
    return len(small & big) / len(small)


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

    这类标签不像未闭合注释那样吞掉全文，只会让后面的内容样式走样，
    而且解析器不报错，肉眼看源文件不容易发现。

    判据全部来自解析器的 html_inline token，不扫源文本：
    - autolink（`<https://…>`、`<user@…>`）被解析成 link token，不是
      html_inline，扫源文本会把 `https` 当成标签名，凡用 autolink 就误报。
    - 名不在 HTML 已知标签表里的（`<target-file>`、`<T>`、`<id>`）是占位符
      或讲解用语，不是标签，没有闭合问题。

    残留局限：正文里讲语法时写出的单个 `<div>` 与真实未闭合无法区分，
    会报出来。这类内容写进反引号或代码块即可跳过。
    """
    skip = doc.code_lines | doc.html_lines | doc.example_lines
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
            for match in re.finditer(r"<(/?)([A-Za-z][A-Za-z0-9]*)[^>]*>", child.content or ""):
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
    """连续多个空行。一个空行是分段，两个以上只是文件里的空洞。"""
    out: list[int] = []
    run = 0
    for i, line in enumerate(doc.raw, 1):
        if line.strip():
            run = 0
            continue
        run += 1
        if run == limit:
            out.append(i - limit + 1)
    return out


class Doc:
    """基于 markdown-it token 流的结构视图。"""

    def __init__(self, text: str, md) -> None:
        self.text = text
        # BOM 会让首行的 `# 标题` 变成段落：\ufeff 不是合法空白，
        # 解析器看不到标题标记。整体剔除 0xFEFF，行号不受影响。
        self.raw = [line.replace("\ufeff", "") for line in text.splitlines()]
        self.front_matter = self._detect_front_matter()
        env: dict = {}
        self.tokens = md.parse("\n".join(self.raw), env)
        # 解析器折叠后的链接定义表：跨行续行、列表内的定义都在里面，
        # 按正则逐行扫会漏掉这两类
        self.references: dict[str, dict] = env.get("references", {})
        self.headings: list[Heading] = []
        self.fences: list[tuple[int, int, str]] = []
        # front matter 不是正文：并进 code_lines 后，所有按行扫描的检查
        # （规则计数、占位、行尾空白、S2、S10）自动跳过它，无需逐处再加条件
        self.code_lines: set[int] = set(self.front_matter)
        self.html_lines: set[int] = set()
        self.example_lines: set[int] = set()
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
        self.unclosed_example: int | None = None
        self.list_marker_space: list[int] = []
        self.broken_links: list[tuple[int, str]] = []
        self.unclosed_html_inline: list[int] = []
        self._table_start = 0
        self._walk()
        self._mark_examples()
        self._find_duplicate_headings()
        self._find_missing_heading_space()
        self._find_list_marker_space()
        self._find_broken_links()
        self._find_unclosed_html()
        self._find_heading_start()

    def _detect_front_matter(self) -> set[int]:
        """识别文件开头的 YAML front matter，返回其行号集合。

        CommonMark 把 `---` 下的行按 setext 标题解析：一段 `name: x` 后面
        跟一行 `---` 会变成一个巨大的 h2，真正的首个标题反而排在它后面。
        跳过这段才不会把 front matter 当成正文结构。

        不能只看首尾两行 `---`：`---` 也是合法的分隔线，正文里
        「分隔线 / 标题 / 分隔线」这种排布会被整段误判成 front matter，
        真正的标题一起被跳过。front matter 的判据加一条：至少有一行是
        `key:` 形式，且首行与收尾行之间没有空行开头的空段。
        """
        if len(self.raw) < 3 or self.raw[0].strip() != "---":
            return set()
        end = None
        for i in range(1, min(len(self.raw), 200)):
            if self.raw[i].strip() in ("---", "..."):
                end = i
                break
        if end is None:
            return set()
        body = [line for line in self.raw[1:end] if line.strip()]
        if not body:
            return set()
        if not any(re.match(r"^[A-Za-z_][\w.-]*\s*:", line) for line in body):
            return set()
        return set(range(1, end + 2))

    def _inline_text(self, i: int) -> str:
        """取行内 token 的全部可见文字。

        不能只认 text 和 code_inline：标题里写成 `## **角色**`、
        `## [输出格式](...)` 时，只取 text 会得到空串，结构判定随之失效。
        """
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
                # 图片的 alt 在 children 里，按普通文本递归处理
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
        cols: list[int] = []
        aligns: list[str] = []

        while i < len(tokens):
            t = tokens[i]
            kind = t.type

            # front matter 被解析成的 h2 与段落不是正文结构，整段跳过
            if t.map and (t.map[0] + 1) in self.front_matter:
                i += 1
                continue

            if kind in ("bullet_list_open", "ordered_list_open"):
                depth += 1
                self.list_markers.append(
                    (
                        t.map[0] + 1 if t.map else 0,
                        depth,
                        t.type == "ordered_list_open",
                        (t.markup or "").strip() or ("." if kind == "ordered_list_open" else "-"),
                        (t.attrs or {}).get("start"),
                    )
                )
            elif kind in ("bullet_list_close", "ordered_list_close"):
                depth -= 1
            elif kind == "list_item_open":
                self.list_items.append((t.map[0] + 1 if t.map else 0, depth))
            elif kind == "heading_open":
                self.headings.append(
                    Heading(
                        line=t.map[0] + 1 if t.map else 0,
                        level=int(t.tag[1]),
                        text=self._inline_text(i + 1),
                    )
                )
            elif kind == "inline":
                self._scan_inline(i)
                self._scan_links(t)
            elif kind == "fence":
                start, end = t.map[0] + 1, t.map[1]
                self.fences.append((start, end, t.info.strip()))
                self.code_lines.update(range(start, end + 1))
                mark = (t.markup or "`")[0]
                last = strip_quote_prefix(self.raw[end - 1]).strip() if 0 < end <= len(self.raw) else ""
                if not re.fullmatch(rf"{re.escape(mark)}{{3,}}", last):
                    self.unclosed = (start, t.info.strip(), mark)
            elif kind == "code_block":
                self.code_lines.update(range(t.map[0] + 1, t.map[1] + 1))
            elif kind == "html_block":
                self.html_lines.update(range(t.map[0] + 1, t.map[1] + 1))
            elif kind == "table_open":
                in_table = True
                rows, cols = [], []
                self._table_start = t.map[0] + 1 if t.map else 0
            elif kind == "tr_open":
                # token 里的单元格数已被解析器截断到表头列数，只能回到源行去数
                rows.append(t.map[0] + 1 if t.map else 0)
            elif kind == "table_close" and in_table:
                if rows:
                    cols = [count_row_cells(self.raw[n - 1]) for n in rows if 0 < n <= len(self.raw)]
                self.tables.append(Table(self._table_start, cols))
                in_table = False

            i += 1

    def _scan_links(self, token) -> None:
        """收集行内链接与图片，供 MD-LINK-* 校验目标与文字。"""
        line = token.map[0] + 1 if token.map else 0
        if not line or line in self.code_lines or line in self.html_lines or line in self.example_lines:
            return
        children = token.children or []
        for idx, child in enumerate(children):
            if child.type == "link_open":
                href = (child.attrs or {}).get("href", "")
                label = ""
                for follow in children[idx + 1 :]:
                    if follow.type == "link_close":
                        break
                    if follow.type in ("text", "code_inline"):
                        label += follow.content
                    elif follow.type == "image":
                        # `[![alt](a.png)](b.md)` 的链接文字是图片，alt 就是文字；
                        # 只认 text 会把这种写法误判成空链接
                        label += follow.content or ""
                self.links.append((line, label, href, False))
            elif child.type == "image":
                attrs = child.attrs or {}
                self.links.append((line, child.content or "", attrs.get("src", ""), True))

    def _scan_inline(self, i: int) -> None:
        r"""检查行内 token 的对称性。

        不能按行数反引号：CommonMark 允许 code span 跨行，
        ``第一行 `abc`` / ``第二行 def``` 是合法的单个 code span，
        按行数会把两行都判成落单。判据改为「解析器没消化掉的标记」：
        没配对的标记会在 text 节点里原样保留，配对成功的变成 code_inline
        或 strong/em token，不再出现在 text 里。
        """
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
        # 反引号：只剩奇数个说明有一个没配上，落在它所在的那一行
        if leftover.count("`") % 2 == 1:
            for offset, raw_line in enumerate(self.raw[token.map[0] : token.map[1]]):
                if count_inline_backticks(raw_line) % 2 == 1:
                    self.unclosed_inline.append(first + offset)
                    break

        for marker in ("**", "__", "~~"):
            if leftover.count(marker) % 2 == 1:
                for offset, raw_line in enumerate(self.raw[token.map[0] : token.map[1]]):
                    if count_marker(strip_inline_code(raw_line), marker) % 2 == 1:
                        self.unclosed_emphasis.append((first + offset, marker))
                        break

        # 单个 * 与 _ 不做检查：`*.py`、`src/*.ts`、`2*3`、`**/*.md`
        # 都在用同一个字符，而它们既不是错也不是强调。区分「落单的斜体」
        # 与「通配符」需要理解语义，机械判定只会把每一处 glob 都报成错。

    def _find_duplicate_headings(self) -> None:
        """同名标题会让锚点冲突，跳转只落到第一个。

        比较时折叠大小写与空白：`## Example` 和 `## example` 生成的锚点相同。
        """
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
        """`#标题` 在 CommonMark 里不是标题，是普通段落。

        这种写法看起来像标题、实际没有语义，目录里也不出现，最容易漏。
        """
        skip = self.code_lines | self.html_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            if re.match(r"^#{1,6}[^#\s]", line):
                self.missing_heading_space.append(i)

    def _find_list_marker_space(self) -> None:
        """列表标记后缺空格时，整行按段落渲染。

        CommonMark 要求 `-`、`*`、`+`、`1.` 之后至少一个空格或行尾。
        `-项内容` 看起来是列表项，实际是普通段落，取消列表也不报错。
        判据只认「标记后紧跟非空白且整行不是合法行内语法」：
        `--flag`、`-5 度`、`*强调*` 这类不能报。
        """
        skip = self.code_lines | self.html_lines | self.example_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            if not re.match(r"^ {0,3}(?:[-*+]|\d+[.)])\S", line):
                continue
            # 排除 `---`、`***`、`-5`、`--flag`、`*强调*` 这类
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

        括号没闭合、地址里有空格、标题引号没配对时，整段退化成普通文字，
        页面上直接显示方括号与圆括号，而解析器不报错。
        判据：这一行源文本里 `](` 的出现次数多于解析出的链接数。
        按次数比而不是按「有没有」，是为了同一行同时有一好一坏两处时仍能报。
        """
        parsed_count: dict[int, int] = {}
        for token in self.tokens:
            if token.type != "inline" or not token.map:
                continue
            line = token.map[0] + 1
            for child in token.children or []:
                if child.type in ("link_open", "image"):
                    parsed_count[line] = parsed_count.get(line, 0) + 1
        skip = self.code_lines | self.html_lines | self.example_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            text = strip_inline_code(line)
            written = len(re.findall(r"!?\[[^\]\n]*\]\(", text))
            if written > parsed_count.get(i, 0):
                self.broken_links.append((i, text.strip()[:40]))

    def _find_unclosed_html(self) -> None:
        """未闭合的 `<!--` 会吞掉文件剩余部分，包括后面的标题。

        解析器把它当成一个 html_block 直到文末，不报错，但内容全不渲染。

        三类要分开看：
        - `<!--` 未闭合：内容全被吞掉。
        - `<script>`、`<style>`、`<pre>`、`<textarea>` 这类 raw-text 块
          未闭合时，解析器同样一路吃到文末，后面的标题一起消失。
        - 行内出现的 `<!--` 没有被 `-->` 收尾：这一段标签会被当纯文本，
          后面的正文照常渲染，但注释内容会显示出来。
        """
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
                # 自闭合写法 `<script />` 没有结束标签，也不该有
                head = lowered.split(">", 1)[0]
                if head.rstrip().endswith("/"):
                    continue
                if f"</{tag}>" not in lowered:
                    self.unclosed_raw_html = (start, tag)
                    return

        # 行内注释：源文本里有 `<!--` 却没有配对的 `-->`，且不在代码块里
        skip = self.code_lines | self.html_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            text = strip_inline_code(line)
            if "<!--" in text and text.count("<!--") > text.count("-->"):
                self.unclosed_html_inline.append(i)

    def _find_heading_start(self) -> None:
        """首个标题不是 h1 时，整篇的层级基线都偏低。

        从 h2 起笔的文件渲染出来没有一级标题，目录里缺少总的入口。
        """
        if self.headings and self.headings[0].level > 1:
            self.heading_starts_deep = self.headings[0]

    def _mark_examples(self) -> None:
        """示例里的路径和规则词是在演示，不是对本文档的要求。

        判据必须是「解析器真的产出了 <example> 标签」，不能用字符串包含：
        - 反引号里的 `<example>` 是讲解语法时的引用，不是示例区起点；
          把反引号剥掉再找仍会命中，因为剥掉的只是反引号，标签文字还在。
        - `<example>` 独占一行时被解析成 html_block，整段没有 inline token，
          只扫 inline 子节点会把真正的示例区整段漏掉。
        所以两处都看：html_block 的内容与 inline 里的 html_inline 子节点。
        """
        marks: list[tuple[int, bool]] = []
        for token in self.tokens:
            if not token.map:
                continue
            line = token.map[0] + 1
            if line in self.code_lines:
                continue
            found = self._example_tags(token)
            marks.extend((line + offset, opening) for offset, opening in found)
        marks.sort()

        start = None
        for line, opening in marks:
            if start is None:
                if not opening:
                    continue
                start = line
                self.example_lines.add(line)
            else:
                self.example_lines.add(line)
                if not opening:
                    start = None
        if start is not None:
            self.unclosed_example = start

    @staticmethod
    def _example_tags(token) -> list[tuple[int, bool]]:
        """按出现顺序返回 (行内偏移, 是否开始标签)。

        `<example>` 与 `</example>` 之间只要有内容，整段（含两个标签）
        会被合并成一个 html_block，块里同时出现开闭两个标签。
        按块首字符判断开/闭会在这种最常见的写法上判错：
        块首是 `<example>`，于是闭标签被当成第二个开标签。

        正确做法是扫块内容里的每个标签，按出现顺序记下来，
        再把内容里的换行换算成行内偏移。
        """
        if token.type not in ("html_block", "inline"):
            return []
        if token.type == "html_block":
            source = token.content or ""
            return [
                (source.count("\n", 0, m.start()), m.group(0) == "<example>")
                for m in re.finditer(r"</?example>", source, re.IGNORECASE)
            ]
        # 行内只认真正的 html_inline 子节点。把 inline 的全部子节点拼起来再扫
        # 会让反引号里的 `` `<example>` `` 也命中——那是讲解语法的引用，
        # 不是示例区起点。
        out: list[tuple[int, bool]] = []
        offset = 0
        for child in token.children or []:
            if child.type == "softbreak":
                offset += 1
                continue
            if child.type != "html_inline":
                continue
            for m in re.finditer(r"</?example>", child.content or "", re.IGNORECASE):
                out.append((offset, m.group(0) == "<example>"))
        return out

    @property
    def content_lines(self) -> list[tuple[int, str]]:
        """非空且不在代码块、HTML 块内的行。"""
        skip = self.code_lines | self.html_lines
        return [(i, line) for i, line in enumerate(self.raw, 1) if line.strip() and i not in skip]

    @property
    def blank_count(self) -> int:
        return sum(1 for line in self.raw if not line.strip())

    @property
    def prose_lines(self) -> list[tuple[int, str]]:
        """正文行：排除代码、HTML 块、示例区与标题。"""
        skip = self.code_lines | self.html_lines | self.example_lines
        return [
            (i, strip_inline_code(line).strip())
            for i, line in self.content_lines
            if i not in skip and not line.lstrip().startswith("#")
        ]


def rule_lines(doc: Doc) -> list[RuleLine]:
    """取正文里的列表项，作为规则行。

    不按长度过滤：`只输出结果。` 这种短规则也是规则，按长度筛掉会让
    规则计数、重复检测、基线对比三处同时漏项。相似度阈值由各检查自己把关。
    """
    rules: list[RuleLine] = []
    section = ""
    last_rule = None
    for line_no, line in doc.content_lines:
        if line_no in doc.example_lines:
            continue
        if line.lstrip().startswith("#"):
            section = line.strip().lstrip("# ").strip()
            last_rule = None
            continue
        match = LIST_MARKER_RE.match(strip_inline_code(line))
        if match:
            text = match.group(1).strip()
            if not text:
                continue
            last_rule = RuleLine(line_no, text, section)
            rules.append(last_rule)
            continue
        if last_rule is not None and line[:1] == " ":
            # 列表项的缩进续行并入规则，否则基线对比与重复检测只看首行
            last_rule.text = f"{last_rule.text} {line.strip()}".strip()
            continue
        last_rule = None
    return rules


def check_duplicates(doc: Doc) -> list[Finding]:
    rules = rule_lines(doc)
    prepared = []
    for rule in rules:
        norm = normalize_for_compare(rule.text)
        # 短到此地步的多是「同上」「见上」这类占位或单项清单，比对结果没有意义
        if len(norm) < DUP_MIN_LENGTH:
            continue
        prepared.append((rule, norm, bigrams(norm)))

    findings: list[Finding] = []
    for i in range(len(prepared)):
        rule_a, norm_a, grams_a = prepared[i]
        for j in range(i + 1, len(prepared)):
            rule_b, norm_b, grams_b = prepared[j]
            shorter, longer = sorted((len(norm_a), len(norm_b)))
            if longer == 0 or shorter / longer < 0.6:
                # 长度差一倍以上，多半是同主题不同粒度的两条规则
                continue
            if containment(grams_a, grams_b) < DUP_JACCARD and containment(grams_b, grams_a) < DUP_JACCARD:
                continue
            if SequenceMatcher(None, norm_a, norm_b).ratio() < DUP_RATIO:
                continue
            findings.append(
                Finding(
                    SUGGESTION,
                    "S9",
                    rule_b.line,
                    f"与 L{rule_a.line} 可能重复：{rule_b.text[:24]}…",
                    "两行用不同措辞讲了同一件事，改一条忘另一条时就会出现自相矛盾",
                    f"合并成一条，或删掉 L{rule_b.line} 只留 L{rule_a.line}",
                )
            )
    return findings


def looks_like_path(ref: str) -> bool:
    """判断反引号里的内容是否在指一个本地文件或目录。

    宁可多认几个文件名，也不能因为扩展名清单不全就整类放过：
    `src/main.js` 之前完全不在检查范围内，等于 S10 对前端项目失效。
    对应的代价是命令行要显式排除（带空格的整串不查）。
    """
    if not ref or any(ch.isspace() for ch in ref):
        # 带空格的整串多半是命令（`pytest -q`）或一句话，不是单个路径
        return False
    if URL_RE.match(ref) or ref.startswith("mailto:"):
        return False
    if ref.startswith(("<", "@", "$")):
        # 占位符、scope 包名、环境变量
        return False
    if any(ch in ref for ch in "*?[]"):
        # glob 通配符匹配的是一批文件，不存在「这个路径在不在」的问题。
        # `**/*.md`、`src/*.ts` 这类写法本身就不是具体文件。
        return False
    bare = ref.split("#", 1)[0].split("?", 1)[0]
    if not bare:
        return False
    if bare.endswith("/"):
        return "/" in bare or bare != "/"
    name = bare.rsplit("/", 1)[-1]
    if name in ROOT_FILE_NAMES:
        return True
    return bare.endswith(CHECKABLE_EXT)


def safe_exists(path: Path) -> bool:
    """文件系统层查存在，不让 OSError 冒到调用方。

    超长名字、名字里有 NUL、权限不足、悬空符号链接都会让 stat 抛异常，
    而调用方要的是「这个引用能不能解析」，异常一律按解析不到处理。
    """
    try:
        return path.exists()
    except (OSError, ValueError):
        return False


def resolve_reference(ref: str, base: Path) -> bool:
    """把引用解析成本地路径并查存在性。

    href 里的空格与非 ASCII 字符会被解析器百分号编码（`我 的.md`
    变成 `%E6%88%91%20%E7%9A%84.md`），先解码再查，否则中文文件名
    永远判成不存在。
    """
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
    # `~/x` 展开后是绝对路径，走到这里说明是相对路径。
    # 只沿目标文件所在目录向上找，不回退 cwd：否则同一份文档在不同目录下
    # 运行会得到不同结论，S10 就不可复核了。
    for parent in [base, *list(base.parents)[:5]]:
        if safe_exists(parent / candidate):
            return True
    return False


def reference_groups(line: str) -> list[list[str]]:
    """把一行里的路径引用按列举关系分组。

    顿号连接的多个引用是在列候选（“从 `README`、`package.json` 里读”），
    候选清单里的文件本来就可以不存在，逐个校验只会制造误报。
    其他分隔（“与”“、再”）则视为各自独立的断言，分别校验。
    """
    groups: list[list[str]] = []
    current: list[str] = []
    prev_end: int | None = None
    for match in INLINE_CODE_RE.finditer(line):
        ref = match.group(1).strip()
        if not looks_like_path(ref):
            continue
        separator = line[prev_end : match.start()] if prev_end is not None else ""
        # 只有顿号、逗号或斜杠连接，才算与上一个引用同属一个列举
        if current and separator.strip() in ("、", ",", "，", "/"):
            current.append(ref)
        else:
            if current:
                groups.append(current)
            current = [ref]
        prev_end = match.end()
    if current:
        groups.append(current)
    return groups


def github_slug(text: str) -> str:
    """按 GitHub 的规则把标题文字转成锚点。

    与常见实现一致：转小写、去掉标点、空格换连字符，保留中文字符
    （GitHub 不把中文转拼音也不丢）。`## Role and Objective` 的锚点是
    `#role-and-objective`，`## 规则 S1–S13` 是 `#规则-s1s13`。
    """
    lowered = text.strip().lower()
    kept: list[str] = []
    for ch in lowered:
        if ch.isalnum() or ch in "-_":
            kept.append(ch)
        elif ch.isspace():
            kept.append(" ")
    return "".join(kept).replace(" ", "-")


def check_anchors(doc: "Doc") -> list[Finding]:
    """校验页内锚点 `[文字](#目标)` 是否指向一个存在的标题。

    指向不存在的锚点时页面不会跳转，读者停在原地，而 Markdown 不报错。
    显式 `<a id="x">` 或 `<a name="x">` 也算有效目标。
    """
    slugs: dict[str, int] = {}
    for heading in doc.headings:
        slug = github_slug(heading.text)
        if slug:
            # 同名标题 GitHub 会加 -1、-2 后缀，这里按出现顺序补上
            if slug in slugs:
                n = 1
                while f"{slug}-{n}" in slugs:
                    n += 1
                slugs[f"{slug}-{n}"] = heading.line
            else:
                slugs[slug] = heading.line
    for i, line in enumerate(doc.raw, 1):
        for match in re.finditer(r"""<a\s+(?:id|name)\s*=\s*["']([^"']+)["']""", strip_inline_code(line)):
            slugs.setdefault(match.group(1).lower(), i)

    findings: list[Finding] = []
    skip = doc.code_lines | doc.html_lines | doc.example_lines
    for line_no, label, target, is_image in doc.links:
        if is_image or not target.startswith("#") or target in ("#", "#top"):
            continue
        if line_no in skip:
            continue
        anchor = target[1:]
        # 解析器会把锚点里的非 ASCII 百分号编码
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


def check_references(doc: Doc, base: Path) -> list[Finding]:
    findings: list[Finding] = []
    skip = doc.code_lines | doc.html_lines | doc.example_lines
    for line_no, line in enumerate(doc.raw, 1):
        if line_no in skip:
            continue
        for group in reference_groups(line):
            if len(group) > 1:
                # 列举候选，不要求每一个都存在
                continue
            ref = group[0]
            if resolve_reference(ref, base):
                continue
            findings.append(
                Finding(
                    WARNING,
                    "S10",
                    line_no,
                    f"引用的路径不存在：{ref}",
                    "指令里点名一个不存在的文件，模型会去找它、找不到后自行发挥",
                    f"改成实际路径，或删掉这处引用（基准目录 {base}）",
                )
            )
    return findings


def check_baseline(doc: Doc, baseline: Doc) -> list[Finding]:
    old_rules = rule_lines(baseline)
    new_prepared = []
    for rule in rule_lines(doc):
        norm = normalize_for_compare(rule.text)
        new_prepared.append((rule, norm, bigrams(norm)))

    findings: list[Finding] = []
    for old in old_rules:
        old_norm = normalize_for_compare(old.text)
        old_grams = bigrams(old_norm)
        if not old_grams:
            continue
        best = 0.0
        for _, new_norm, new_grams in new_prepared:
            score = containment(old_grams, new_grams)
            if score < BASE_COVERAGE:
                score = max(score, SequenceMatcher(None, old_norm, new_norm).ratio() * 0.9)
            best = max(best, score)
            if best >= BASE_COVERAGE:
                break
        if best < BASE_COVERAGE:
            findings.append(
                Finding(
                    WARNING,
                    "BASE",
                    old.line,
                    f"基线规则在新文件里找不到对应表述：{old.text[:30]}…",
                    "重写时删过头，这条约束在新文件里没有了",
                    "确认是有意删除后忽略；否则补回这条要求",
                )
            )
    return findings


def check_structure(doc: Doc, base: Path) -> list[Finding]:
    findings: list[Finding] = []

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
    for line, text in find_undefined_link_refs(doc, defined):
        findings.append(
            Finding(
                WARNING,
                "MD-LINK-REF",
                line,
                f"链接引用的标签未定义：{text}",
                "标签找不到定义时渲染器原样输出方括号，链接不成立",
                f"补一行 `[标签]: 地址`，或改成行内链接 `[文字](地址)`",
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
                f"链接定义没有被任何引用使用：{label}",
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

    if doc.unclosed_example:
        findings.append(
            Finding(
                WARNING,
                "MD-EXAMPLE-UNCLOSED",
                doc.unclosed_example,
                "<example> 没有闭合",
                "示例区一直延续到文末，后面的规则会被当成示例，不进规则计数与重复检测",
                "在示例末尾补上 </example>",
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
                f"链接语法没被解析成链接：{snippet}",
                "括号没闭合、地址含空格或标题引号没配对时整段退化成文字，页面显示方括号",
                "检查圆括号与引号是否配对；地址含空格时用尖括号包住：`[文字](<my file.md>)`",
            )
        )

    for line in find_long_blank_runs(doc):
        findings.append(
            Finding(
                WARNING,
                "S12",
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

    # 表格分隔行写错（缺列、少横线、混了非法字符）时，整张表退化成普通段落，
    # 解析器直接不产生 table token，上面那些检查一个都看不到。
    # 判据：连续两行以上以 | 开头、列数一致，却没被解析成表格。
    # table_close 的 map 是 None，只能靠 tr_open 的行号反推哪些行已进入表格
    parsed_table_lines: set[int] = set()
    for token in doc.tokens:
        if token.type == "tr_open" and token.map:
            parsed_table_lines.add(token.map[0] + 1)
    skip_table = doc.code_lines | doc.html_lines | doc.example_lines
    run: list[int] = []
    for i, raw_line in enumerate(doc.raw + [""], 1):
        # 引用块里的表格行以 `> |` 开头，先剥掉 > 前缀再判断
        stripped = strip_inline_code(strip_quote_prefix(raw_line)).strip()
        is_pipe_row = i <= len(doc.raw) and i not in skip_table and stripped.startswith("|")
        if is_pipe_row:
            run.append(i)
            continue
        # 整段竖线行里只要有一行进了 tr_open，说明表格已经成立，
        # 分隔行本身不是 tr，不能要求每行都被解析
        if len(run) >= 2 and not any(n in parsed_table_lines for n in run):
            findings.append(
                Finding(
                    WARNING,
                    "MD-TABLE-BROKEN",
                    run[0],
                    f"这 {len(run)} 行看起来是表格，但没有被解析成表格",
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
                "行内代码的反引号数量是奇数",
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
                f"强调标记 {marker} 数量是奇数",
                "未配对的标记会原样显示成符号，读者看到的是星号而不是加粗",
                f"补齐 {marker}，或用转义 \\{marker[0]} 表示字面量",
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

    # 同一段列表必须用同一种标记。解析器把 `-`、`*`、`+` 当成三个独立列表，
    # 紧邻的两个列表换了符号，渲染出的间距与后续编号都会断开。
    # 分组键含三部分：连续性、深度、是否有序。缺任何一个都会误报——
    # 有序列表的 `.` 与无序的 `-` 本就不必一致，隔了空行的两个列表也彼此独立。
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
        # 从 1 开始的有序列表才符合常规编号；从其它值起会让引用它的地方对不上
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

    # 空列表项渲染成一个小圆点，没有内容，通常是想留占位或误删了文字
    declared_items = {line for line, _ in doc.list_items}
    inline_first_lines = {
        tok.map[0] + 1 for tok in doc.tokens if tok.type == "inline" and tok.map
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

    # 同一深度出现多次时缩进必须一致，否则渲染器的归属判断会随上下文漂移。
    # 不按「比上级多 2–4 空格」判：合法缩进取决于上级标记宽度，
    # `1. ` 比 `- ` 宽，同样 6 空格对有序列表是子项、对无序列表就丢了结构。
    # 能确认的判据只有两条，其余交给「没被解析成列表项」那一项。
    indent_by_depth: dict[int, int] = {}
    prev_depth = 0
    for line, depth in doc.list_items:
        if not 0 < line <= len(doc.raw):
            continue
        raw_line = doc.raw[line - 1]
        indent = len(raw_line) - len(raw_line.lstrip())
        # 深度变浅说明上一段子树结束，更深层的基准随之作废：
        # 否则 `- a /  - b` 之后另起 `- c /   - d` 会被当成同级缩进冲突
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

    # 缩进过深时解析器把它并进上一项正文，这一行根本不会进 list_items，
    # 只能从源文本找：形如列表项、却不在解析结果里的行。
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

    line_skip = doc.code_lines | doc.html_lines | doc.example_lines
    for i, line in enumerate(doc.raw, 1):
        if i in line_skip:
            continue
        stripped_line = strip_quote_prefix(line).strip()
        if not stripped_line or stripped_line.startswith("|"):
            continue
        if "http://" in line or "https://" in line:
            continue
        if len(line) > 200:
            findings.append(
                Finding(WARNING, "MD-LINE-LEN", i, "单行超过 200 字",
                        "过长单行不利于 diff 审查与定位，窄窗口还会横向滚动",
                        "按句子拆行，每行不超过 200 字；表格、代码、URL 与 front matter 除外")
            )

    return findings


def check_rules(doc: Doc, skill_mode: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    headings = [h.text for h in doc.headings]
    joined_headings = " ".join(headings).lower()
    body = doc.prose_lines
    joined_all = "\n".join(line for _, line in body)

    def has_heading(*words: str) -> bool:
        return any(w.lower() in joined_headings for w in words)

    if not skill_mode and not has_heading("role", "角色", "objective", "目标"):
        findings.append(
            Finding(
                ERROR, "S1", None, "缺少角色/目标一节",
                "没有角色与完成定义，模型不知道负责范围，也不知道何时算做完",
                "加 `# Role and Objective` 或 `# 角色与完成定义`，一到两句写清角色、范围、完成标准",
            )
        )

    if not skill_mode and not has_heading("output format", "输出格式"):
        findings.append(
            Finding(
                ERROR, "S6", None, "缺少输出格式一节",
                "不给结构、长度、格式，模型会按自己的默认发挥，每次结果不一致",
                "加 `# Output Format` 或 `# 输出格式`，写明结构、长度、是否贴命令输出",
            )
        )

    if not skill_mode and not has_heading("instructions", "指令"):
        findings.append(
            Finding(
                WARNING, "结构", None, "缺少指令一节",
                "会调用工具或改文件的 agent 必须有正向行为要求",
                "加 `# Instructions`，下设「始终」「绝不」「不确定时」；单步纯文本任务可省",
            )
        )

    if not skill_mode and not has_heading("不确定", "fallback", "when unsure", "无法处理"):
        findings.append(
            Finding(
                WARNING, "S4", None, "缺少兜底说明",
                "请求模糊、超出范围、信息不足时没有指定动作，模型只能自行决定",
                "加「不确定时」分支，三种情况各给一个动作",
            )
        )
    elif not skill_mode and has_heading("instructions", "指令"):
        for label, words, fix in (
            ("模糊", ("模糊", "含糊", "不明确", "ambiguous"), "列出两三种理解，问用户选哪个"),
            ("超出范围", ("超出范围", "越界", "out of scope"), "说明边界，给出替代方案，不动手"),
            ("信息不足", ("信息不足", "不足", "insufficient"), "先自查代码与文档，查不到再问"),
        ):
            if not any(w in joined_all for w in words):
                findings.append(
                    Finding(WARNING, "S4", None, f"兜底未覆盖「{label}」",
                            "只覆盖部分情况，剩下的分支仍由模型自行判断",
                            f"补一条：{fix}")
                )

    for line_no, line in body:
        if PRIORITY_RE.search(line) and not REFUTE_RE.search(line):
            findings.append(
                Finding(
                    ERROR, "S5", line_no, "用编号声明优先级",
                    "同一层级的规则不因编号产生优先级，该机制不成立",
                    "删掉优先级声明，用分节表达从属关系",
                )
            )

    for a, b in CONTRAST_PAIRS:
        if a in joined_all and b in joined_all:
            findings.append(
                Finding(ERROR, "S5", None, f"同时要求「{a}」与「{b}」",
                        "两个无条件要求互相抵消，模型会任选一个执行",
                        "给其中一条加适用条件，或删掉一条")
            )

    skip = doc.code_lines | doc.html_lines
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        if line != line.rstrip():
            findings.append(
                Finding(WARNING, "S12", i, "行尾空白",
                        "Markdown 中行尾两个空格是强制换行，多余空白会意外改变渲染",
                        "删除行尾空白")
            )
        if "\t" in line:
            findings.append(
                Finding(WARNING, "S12", i, "含制表符",
                        "制表符宽度依渲染器而变，缩进会错位", "改为空格")
            )

    if not doc.text.endswith("\n"):
        findings.append(
            Finding(ERROR, "S12", len(doc.raw), "文件末尾缺少换行",
                    "POSIX 文本约定要求文件以换行结尾，否则追加内容时与末行粘连",
                    "在文件末尾补一个换行")
        )

    for i, line in enumerate(doc.raw, 1):
        if i not in skip and PLACEHOLDER_RE.match(line.strip()):
            findings.append(
                Finding(ERROR, "S12", i, "含未填的占位标记",
                        "占位行表示交付物未完成，加载后等于空规则",
                        "填入真实内容，或整行删除")
            )

    section = ""
    for line_no, line in doc.content_lines:
        stripped = strip_inline_code(line).strip()
        if stripped.startswith("#"):
            section = stripped.lstrip("# ").strip()
            continue
        body = LIST_MARKER_RE.sub(r"\1", stripped)
        match = NEGATION_RE.match(body)
        if not match:
            continue
        if any(tag in section for tag in ("红线", "绝不", "绝对不做")):
            continue
        rest = body[match.end():].lstrip()
        if not FIX_HINT_RE.search(rest):
            findings.append(
                Finding(WARNING, "S2", line_no, "疑似只禁不导",
                        "只说不做什么，模型可能换一种方式违反同一意图",
                        "补替代行为（“改成……”）或理由（“因为……”）；红线可保留禁止式但要写理由")
            )

    examples = len(re.findall(r"<example>", doc.text))
    rule_count = len(rule_lines(doc))
    if examples == 0 and rule_count >= EXAMPLE_RULE_THRESHOLD:
        findings.append(
            Finding(
                SUGGESTION, "S7", None, f"规则 {rule_count} 条但没有示例",
                "规则一多，只靠文字描述容易在边界情况上跑偏；示例能固定没写到的行为",
                "补 3–5 个示例，每个演示一条规则没写到的行为，用 `<example>` 包住",
            )
        )

    longest = max(((len(line), i) for i, line in doc.content_lines), default=(0, 0))
    if longest[0] > LONG_LINE_LIMIT:
        findings.append(
            Finding(SUGGESTION, "S11", longest[1], f"最长行 {longest[0]} 字",
                    "单行承载成段材料时，修改一处要重读整行，diff 也无法定位",
                    "拆成多条，一条一个要求")
        )

    return findings


USAGE = "用法: python3 check.py [--skill] [--strict] [--baseline <旧文件>] <目标文件>"


def parse_args(argv: list[str]):
    positional: list[str] = []
    skill_mode = False
    strict = False
    baseline: str | None = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            print(USAGE)
            raise SystemExit(0)
        if arg == "--skill":
            skill_mode = True
        elif arg == "--strict":
            strict = True
        elif arg.startswith("--baseline="):
            baseline = arg.split("=", 1)[1]
        elif arg == "--baseline":
            i += 1
            if i >= len(argv):
                print("--baseline 需要一个文件路径", file=sys.stderr)
                raise SystemExit(2)
            baseline = argv[i]
        elif arg.startswith("--"):
            print(f"未知参数: {arg}", file=sys.stderr)
            raise SystemExit(2)
        else:
            positional.append(arg)
        i += 1
    if len(positional) != 1:
        print(USAGE, file=sys.stderr)
        raise SystemExit(2)
    return positional[0], skill_mode, baseline, strict


def main() -> int:
    target, skill_mode, baseline_path, strict = parse_args(sys.argv[1:])

    path = Path(target)
    if not path.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        return 2

    baseline_file = None
    if baseline_path:
        baseline_file = Path(baseline_path)
        if not baseline_file.is_file():
            print(f"基线文件不存在: {baseline_file}", file=sys.stderr)
            return 2

    md = load_markdown_it()
    if md is None:
        return 2

    doc = Doc(path.read_text(encoding="utf-8"), md)
    findings = check_structure(doc, path.resolve().parent) + check_rules(doc, skill_mode=skill_mode)
    findings += check_anchors(doc)
    findings += check_duplicates(doc)
    findings += check_references(doc, path.resolve().parent)
    if baseline_file:
        findings += check_baseline(doc, Doc(baseline_file.read_text(encoding="utf-8"), md))

    order = {ERROR: 0, WARNING: 1, SUGGESTION: 2}
    findings.sort(key=lambda f: (order[f.level], f.line or 0))

    longest = max(((len(line), i) for i, line in doc.content_lines), default=(0, 0))

    print(
        f"文件 {path} | 行数 {len(doc.content_lines)}（不含空行与代码块，空行 {doc.blank_count}）"
        f" | 标题 {len(doc.headings)} 个 | 围栏 {len(doc.fences)} 个"
        f" | 规则 {len(rule_lines(doc))} 条"
    )
    print(f"最长行 {longest[0]} 字（L{longest[1]}）")
    if baseline_file:
        print(f"基线 {baseline_file} | 规则 {len(rule_lines(Doc(baseline_file.read_text(encoding='utf-8'), md)))} 条")
    print()

    for level in (ERROR, WARNING, SUGGESTION):
        items = [f for f in findings if f.level == level]
        print(f"[{level}] {len(items)} 项")
        for f in items:
            where = f"L{f.line}" if f.line else "全文"
            print(f"  - {where}  {f.rule}  {f.message}")
            print(f"      原因：{f.reason}")
            print(f"      建议：{f.fix}")
        print()

    errors = sum(1 for f in findings if f.level == ERROR)
    warnings = sum(1 for f in findings if f.level == WARNING)
    if strict:
        # 严格模式把警告也算失败：CI 里不给人“先放着”的余地，
        # 每一条都要修掉或改成显式豁免
        failed = errors + warnings > 0
    else:
        failed = errors > 0
    print("结果:", "失败" if failed else "通过", "（严格模式：警告也计失败）" if strict else "")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
