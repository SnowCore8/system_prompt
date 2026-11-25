#!/usr/bin/env bash
# 从顶层真源组装自包含包：不依赖包内软链，复制 skills/rules/shared 内容并附双许可证。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/materialize.sh <qoder|qwen|dsh> <目标目录>

Qoder/Qwen 从 plugins/<包> 的清单与 hooks，加上顶层 skills/、rules/、shared/ 组装；
DSH 从仓库根清单与 plugins/dsh，加上顶层 skills/、rules/ 组装。
目标目录必须是新路径；产物自包含、无软链，供本地校验或打包使用。
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
case "$1" in
  dsh)
    # DSH bundle 的清单在仓库根，源码与 patch 在 plugins/dsh，skill/规则在根级目录
    mkdir -p "$TARGET/plugins/dsh"
    cp "$REPO_ROOT/package.json" "$TARGET/package.json"
    cp -a "$REPO_ROOT/plugins/dsh/src" "$TARGET/plugins/dsh/src"
    cp "$REPO_ROOT/plugins/dsh/cordis.patch.yml" "$REPO_ROOT/plugins/dsh/README.md" "$TARGET/plugins/dsh/"
    cp -a "$REPO_ROOT/skills" "$TARGET/skills"
    cp -a "$REPO_ROOT/rules" "$TARGET/rules"
    cp "$REPO_ROOT/plugins/dsh/README.md" "$TARGET/README.md"
    ;;
  qoder)
    cp -a "$PACKAGE/.qoder-plugin" "$PACKAGE/hooks" "$PACKAGE/README.md" "$TARGET/"
    cp -a "$REPO_ROOT/skills" "$TARGET/skills"
    cp -a "$REPO_ROOT/rules" "$TARGET/rules"
    cp -a "$REPO_ROOT/shared/commands" "$TARGET/commands"
    cp -a "$REPO_ROOT/shared/scripts" "$TARGET/scripts"
    ;;
  qwen)
    cp -a "$PACKAGE/qwen-extension.json" "$PACKAGE/hooks" "$PACKAGE/README.md" "$TARGET/"
    cp -a "$REPO_ROOT/skills" "$TARGET/skills"
    cp -a "$REPO_ROOT/rules" "$TARGET/constraints"
    cp -a "$REPO_ROOT/shared/commands" "$TARGET/commands"
    cp -a "$REPO_ROOT/shared/scripts" "$TARGET/scripts"
    ;;
esac
cp "$REPO_ROOT/LICENSE" "$REPO_ROOT/LICENSE-CC-BY-4.0.txt" "$REPO_ROOT/LICENSE-MIT.txt" "$REPO_ROOT/THIRD-PARTY-NOTICES.md" "$TARGET/"
echo "已组装: $1 -> $TARGET"
