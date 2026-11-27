"""命令行入口：参数解析、输出与退出码。"""

from __future__ import annotations

import sys
from pathlib import Path

from markdown_lint.checks import check_anchors, check_format
from markdown_lint.constants import ERROR, SUGGESTION, WARNING
from markdown_lint.loader import load_markdown_it
from markdown_lint.model import Doc

USAGE = "用法: python3 check.py [--strict] <目标文件>"


def parse_args(argv: list[str]) -> tuple[str, bool]:
    positional: list[str] = []
    strict = False
    for arg in argv:
        if arg in ("-h", "--help"):
            print(USAGE)
            raise SystemExit(0)
        if arg == "--strict":
            strict = True
        elif arg.startswith("--"):
            print(f"未知参数: {arg}", file=sys.stderr)
            raise SystemExit(2)
        else:
            positional.append(arg)
    if len(positional) != 1:
        print(USAGE, file=sys.stderr)
        raise SystemExit(2)
    return positional[0], strict


def main() -> int:
    target, strict = parse_args(sys.argv[1:])
    path = Path(target)
    if not path.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        return 2

    md = load_markdown_it()
    if md is None:
        return 2

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"读取失败: {path}: {exc}", file=sys.stderr)
        return 2

    doc = Doc(text, md)
    findings = check_format(doc, path.resolve().parent) + check_anchors(doc)
    order = {ERROR: 0, WARNING: 1, SUGGESTION: 2}
    findings.sort(key=lambda f: (order[f.level], f.line or 0))

    longest = max(
        ((len(line), i) for i, line in doc.content_lines), default=(0, 0)
    )
    print(
        f"文件 {path} | 行数 {len(doc.content_lines)}"
        f"（不含空行、代码块、HTML 块与 front matter，空行 {doc.blank_count}）"
        f" | 标题 {len(doc.headings)} 个 | 围栏 {len(doc.fences)} 个"
        f" | 表格 {len(doc.tables)} 个 | 链接 {len(doc.links)} 个"
    )
    print(f"最长行 {longest[0]} 字（{'L' + str(longest[1]) if longest[1] else '无'}）")
    print()

    for level in (ERROR, WARNING, SUGGESTION):
        items = [finding for finding in findings if finding.level == level]
        print(f"[{level}] {len(items)} 项")
        for finding in items:
            where = f"L{finding.line}" if finding.line else "全文"
            print(f"  - {where}  {finding.rule}  {finding.message}")
            print(f"      原因：{finding.reason}")
            print(f"      建议：{finding.fix}")
        print()

    errors = sum(1 for finding in findings if finding.level == ERROR)
    warnings = sum(1 for finding in findings if finding.level == WARNING)
    failed = errors + warnings > 0 if strict else errors > 0
    print(
        "结果:",
        "失败" if failed else "通过",
        "（严格模式：警告也计失败）" if strict else "",
    )
    return 1 if failed else 0
