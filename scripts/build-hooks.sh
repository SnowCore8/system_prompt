#!/usr/bin/env bash
# 编译 hook 二进制：POSIX 用本机 gcc，Windows 用 mingw-w64 交叉编译。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/.qoder/plugins/global-user-constraints/scripts/inject-time.c"
OUT_DIR="$REPO_ROOT/.qoder/plugins/global-user-constraints/scripts/bin"
POSIX_CC="${CC:-gcc}"
WINDOWS_CC="x86_64-w64-mingw32-gcc"

FLAGS=(-O2 -std=c11 -Wall -Wextra -finput-charset=UTF-8 -fexec-charset=UTF-8)

mkdir -p "$OUT_DIR"

if ! command -v "$POSIX_CC" >/dev/null 2>&1; then
  echo "缺少 POSIX C 编译器: $POSIX_CC" >&2
  exit 1
fi
"$POSIX_CC" "${FLAGS[@]}" -o "$OUT_DIR/inject-time" "$SRC"

if ! command -v "$WINDOWS_CC" >/dev/null 2>&1; then
  echo "缺少 Windows 交叉编译器: $WINDOWS_CC（Ubuntu: apt install mingw-w64）" >&2
  rm -f "$OUT_DIR/inject-time"
  exit 1
fi
"$WINDOWS_CC" "${FLAGS[@]}" -static -static-libgcc \
  -o "$OUT_DIR/inject-time.exe" "$SRC"

echo "已生成: $OUT_DIR/inject-time, $OUT_DIR/inject-time.exe"
