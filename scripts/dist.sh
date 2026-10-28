#!/usr/bin/env bash
# 把用户级插件打包到仓库根目录，文件名带当前 commit id。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/dist.sh [--no-validate]

把插件目录打成 <仓库根>/global-user-constraints-<commit>.zip，
commit 取当前 HEAD 的短 id；工作区有未提交改动时追加 -dirty。
打包后检查 zip 结构，默认还会运行 Qoder 插件离线校验；
校验器不存在时跳过并提示。
EOF
}

VALIDATE=1
case "${1:-}" in
  "") ;;
  --no-validate) VALIDATE=0 ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/.qoder/plugins/global-user-constraints"
VALIDATOR="$HOME/.qoder/plugins/cache/qoder-bundler/qoder-create-plugin/skills/create-plugin/scripts/validate_qoder_plugin.py"

if ! COMMIT="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null)"; then
  echo "无法读取 commit id：$REPO_ROOT 不是 git 仓库或尚无提交" >&2
  exit 1
fi
if [ -n "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=normal)" ]; then
  COMMIT="$COMMIT-dirty"
  echo "工作区有未提交改动，文件名标记 -dirty" >&2
fi
OUT="$REPO_ROOT/global-user-constraints-$COMMIT.zip"

rm -f "$OUT"
(
  cd "$PLUGIN_DIR"
  zip -qr "$OUT" . \
    -x "**/.DS_Store" "__MACOSX/*" "**/__pycache__/*" "**/*.pyc" ".qoder/settings.local.json" ".qoder/**"
)

python3 - "$OUT" <<'PY'
import sys, zipfile

path = sys.argv[1]
with zipfile.ZipFile(path) as zf:
    names = zf.namelist()

problems = []
if ".qoder-plugin/plugin.json" not in names:
    problems.append("缺少 .qoder-plugin/plugin.json")
for name in names:
    if name.startswith("/") or ".." in name.split("/"):
        problems.append(f"非法路径: {name}")
if any(name.endswith(".pyc") or "__pycache__" in name for name in names):
    problems.append("包含 Python 缓存")
if problems:
    sys.exit("zip 结构校验失败:\n- " + "\n- ".join(problems))

print(f"zip 结构校验通过: {len(names)} 个条目")
PY

if [ "$VALIDATE" -eq 1 ]; then
  if [ -f "$VALIDATOR" ]; then
    python3 "$VALIDATOR" "$OUT"
  else
    echo "跳过离线校验: 未找到 $VALIDATOR" >&2
  fi
fi

echo "已生成 $OUT"
