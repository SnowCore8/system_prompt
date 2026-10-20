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
EMPTY_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
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
    """
    skip = doc.code_lines | doc.html_lines | doc.example_lines
    defined: dict[str, int] = {}
    duplicates: list[tuple[int, str]] = []
    for i, line in enumerate(doc.raw, 1):
        if i in skip:
            continue
        match = LINK_DEF_RE.match(line)
        if not match:
            continue
        label = collapse_label(match.group(1))
        if not label:
            continue
        if label in defined:
            duplicates.append((i, match.group(1)))
        else:
            defined[label] = i
    return defined, duplicates


def collapse_label(label: str) -> str:
    return " ".join(label.split()).casefold()


def find_undefined_link_refs(doc: "Doc", defined: dict[str, int]) -> list[tuple[int, str]]:
    """找出标签未定义的 `[文字][标签]`。未定义时它会原样显示成字面量。"""
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


class Doc:
    """基于 markdown-it token 流的结构视图。"""

    def __init__(self, text: str, md) -> None:
        self.text = text
        # BOM 会让首行的 `# 标题` 变成段落：\ufeff 不是合法空白，
        # 解析器看不到标题标记。整体剔除 0xFEFF，行号不受影响。
        self.raw = [line.replace("\ufeff", "") for line in text.splitlines()]
        self.front_matter = self._detect_front_matter()
        self.tokens = md.parse("\n".join(self.raw))
        self.headings: list[Heading] = []
        self.fences: list[tuple[int, int, str]] = []
        # front matter 不是正文：并进 code_lines 后，所有按行扫描的检查
        # （规则计数、占位、行尾空白、S2、S10）自动跳过它，无需逐处再加条件
        self.code_lines: set[int] = set(self.front_matter)
        self.html_lines: set[int] = set()
        self.example_lines: set[int] = set()
        self.tables: list[Table] = []
        self.list_items: list[tuple[int, int]] = []
        self.unclosed: tuple[int, str, str] | None = None
        self.unclosed_inline: list[int] = []
        self.unclosed_html: int | None = None
        self.unclosed_emphasis: list[tuple[int, str]] = []
        self.empty_links: list[tuple[int, str]] = []
        self.missing_heading_space: list[int] = []
        self.heading_starts_deep: Heading | None = None
        self.duplicate_headings: list[tuple[int, str]] = []
        self._table_start = 0
        self._walk()
        self._mark_examples()
        self._find_duplicate_headings()
        self._find_missing_heading_space()
        self._find_unclosed_html()
        self._find_empty_links()
        self._find_heading_start()

    def _detect_front_matter(self) -> set[int]:
        """识别文件开头的 YAML front matter，返回其行号集合。

        CommonMark 把 `---` 下的行按 setext 标题解析：一段 `name: x` 后面
        跟一行 `---` 会变成一个巨大的 h2，真正的首个标题反而排在它后面。
        跳过这段才不会把 front matter 当成正文结构。
        """
        if not self.raw or self.raw[0].strip() != "---":
            return set()
        for i in range(1, min(len(self.raw), 200)):
            if self.raw[i].strip() in ("---", "..."):
                return set(range(1, i + 2))
        return set()

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

        for marker in ("**", "__"):
            if leftover.count(marker) % 2 == 1:
                for offset, raw_line in enumerate(self.raw[token.map[0] : token.map[1]]):
                    if count_marker(strip_inline_code(raw_line), marker) % 2 == 1:
                        self.unclosed_emphasis.append((first + offset, marker))
                        break

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

    def _find_unclosed_html(self) -> None:
        """未闭合的 `<!--` 会吞掉文件剩余部分，包括后面的标题。

        解析器把它当成一个 html_block 直到文末，不报错，但内容全不渲染。
        """
        for token in self.tokens:
            if token.type != "html_block" or not token.map:
                continue
            content = token.content or ""
            if content.lstrip().startswith("<!--") and "-->" not in content:
                self.unclosed_html = token.map[0] + 1
                return

    def _find_empty_links(self) -> None:
        """`[文字]()` 与 `[](地址)` 渲染出来是空链接，点击无处可去。"""
        skip = self.code_lines | self.html_lines | self.example_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            for match in EMPTY_LINK_RE.finditer(strip_inline_code(line)):
                label, url = match.group(1), match.group(2)
                if not label.strip() or not url.strip():
                    self.empty_links.append((i, match.group(0)))

    def _find_heading_start(self) -> None:
        """首个标题不是 h1 时，整篇的层级基线都偏低。

        从 h2 起笔的文件渲染出来没有一级标题，目录里缺少总的入口。
        """
        if self.headings and self.headings[0].level > 1:
            self.heading_starts_deep = self.headings[0]

    def _mark_examples(self) -> None:
        """示例里的路径和规则词是在演示，不是对本文档的要求。

        必须跳过代码块：模板里字面写出的 `<example>` 只是示例，不是示例区的开始。
        """
        start = None
        skip = self.code_lines | self.html_lines
        for i, line in enumerate(self.raw, 1):
            if i in skip:
                continue
            lowered = line.lower()
            if start is None and "<example>" in lowered:
                start = i
            elif start is not None:
                self.example_lines.add(i)
                if "</example>" in lowered:
                    start = None

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
    for line_no, line in doc.content_lines:
        if line_no in doc.example_lines:
            continue
        if line.lstrip().startswith("#"):
            section = line.strip().lstrip("# ").strip()
            continue
        match = LIST_MARKER_RE.match(strip_inline_code(line))
        if not match:
            continue
        text = match.group(1).strip()
        if not text:
            continue
        rules.append(RuleLine(line_no, text, section))
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
    bare = ref.split("#", 1)[0].split("?", 1)[0]
    if not bare:
        return False
    if bare.endswith("/"):
        return "/" in bare or bare != "/"
    name = bare.rsplit("/", 1)[-1]
    if name in ROOT_FILE_NAMES:
        return True
    return bare.endswith(CHECKABLE_EXT)


def resolve_reference(ref: str, base: Path) -> bool:
    target = ref.split("#", 1)[0].split("?", 1)[0].strip()
    if not target:
        return True
    candidate = Path(target).expanduser()
    if candidate.is_absolute():
        return candidate.exists()
    # `~/x` 展开后是绝对路径，走到这里说明是相对路径。
    # 只沿目标文件所在目录向上找，不回退 cwd：否则同一份文档在不同目录下
    # 运行会得到不同结论，S10 就不可复核了。
    for parent in [base, *list(base.parents)[:5]]:
        if (parent / candidate).exists():
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


def check_structure(doc: Doc) -> list[Finding]:
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

    for line, text in doc.empty_links:
        findings.append(
            Finding(
                WARNING,
                "MD-LINK-EMPTY",
                line,
                f"链接缺少文字或地址：{text}",
                "空链接在页面上可见却无处可去，读者点击后没有任何反应",
                "补上链接文字与地址，或去掉链接语法只留文字",
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
    findings = check_structure(doc) + check_rules(doc, skill_mode=skill_mode)
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
