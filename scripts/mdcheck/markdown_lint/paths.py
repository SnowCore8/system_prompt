"""本地文件路径解析：引用目标是否存在。"""

from pathlib import Path
from urllib.parse import unquote


def safe_exists(path: Path) -> bool:
    """文件系统层查存在，OSError 一律按不存在处理。"""
    try:
        return path.exists()
    except (OSError, ValueError):
        return False


def resolve_reference(ref: str, base: Path) -> bool:
    """把引用解析成本地路径并查存在性。"""
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
    for parent in [base, *list(base.parents)[:5]]:
        if safe_exists(parent / candidate):
            return True
    return False
