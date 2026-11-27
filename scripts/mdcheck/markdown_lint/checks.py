"""格式校验主流程：汇总全部规则检测结果。"""

from __future__ import annotations

import re
from pathlib import Path

from markdown_lint.blocks import (
    find_blocks_without_blank_after,
    find_blocks_without_blank_before,
    find_emphasis_style_mismatch,
    find_fence_style_mismatch,
    find_headings_with_extra_space,
    find_hr_style_mismatch,
    find_indented_headings,
    find_long_blank_runs,
    find_quote_marker_space,
)
from markdown_lint.constants import (
    BLOCK_START_RE,
    ERROR,
    LONG_LINE_LIMIT,
    SUGGESTION,
    WARNING,
)
from markdown_lint.links import (
    check_anchors,
    find_empty_link_definitions,
    find_link_definitions,
    find_unclosed_inline_html,
    find_undefined_link_refs,
    find_used_link_labels,
    is_external_link,
)
from markdown_lint.model import Doc, Finding, Heading
from markdown_lint.paths import resolve_reference
from markdown_lint.text import strip_inline_code, strip_quote_prefix

__all__ = ["check_anchors", "check_format"]


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
