"""行级文本工具：引用前缀、行内代码、单元格与标记计数。"""


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
