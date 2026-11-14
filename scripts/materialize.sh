#!/usr/bin/env bash
# 把带软链的包目录物化成自包含目录：解引用共享内容并附上双许可证。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/materialize.sh <qoder|qwen|dsh> <目标目录>

仓库里的三个包都用相对软链引用共享的 skills/、rules/ 与 shared/，这样真源只有一份。
Qoder 的 plugins validate 会拒绝解析到包外的路径，所以本地安装或校验前先物化：
目标目录必须是新路径，脚本会解引用所有软链并把 LICENSE* 复制进去。
EOF
}

case "${1:-}" in
  qoder|qwen|dsh) ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac
[ -n "${2:-}" ] || { usage >&2; exit 2; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE="$REPO_ROOT/plugins/$1"
TARGET="$2"

[ -d "$PACKAGE" ] || { echo "包不存在: $PACKAGE" >&2; exit 1; }
[ ! -e "$TARGET" ] || { echo "目标已存在: $TARGET" >&2; exit 1; }

mkdir -p "$TARGET"
if [ "$1" = "dsh" ]; then
  # DSH bundle 的清单在仓库根，源码与 patch 在 plugins/dsh，skill/规则在根级目录
  mkdir -p "$TARGET/plugins/dsh"
  cp "$REPO_ROOT/package.json" "$TARGET/package.json"
  cp -a "$REPO_ROOT/plugins/dsh/src" "$TARGET/plugins/dsh/src"
  cp "$REPO_ROOT/plugins/dsh/cordis.patch.yml" "$REPO_ROOT/plugins/dsh/README.md" "$TARGET/plugins/dsh/"
  cp -a "$REPO_ROOT/skills" "$TARGET/skills"
  cp -a "$REPO_ROOT/rules" "$TARGET/rules"
  cp "$REPO_ROOT/plugins/dsh/README.md" "$TARGET/README.md"
else
  cp -aL "$PACKAGE/." "$TARGET/"
fi
cp "$REPO_ROOT/LICENSE" "$REPO_ROOT/LICENSE-CC-BY-4.0.txt" "$REPO_ROOT/LICENSE-MIT.txt" "$REPO_ROOT/THIRD-PARTY-NOTICES.md" "$TARGET/"
echo "已物化: $1 -> $TARGET"
