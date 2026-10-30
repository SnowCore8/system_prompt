#!/usr/bin/env bash
# 把用户级插件打包到仓库根目录：版本随插件提交数递增，文件名带当前 commit id。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/dist.sh [--no-validate]

版本取自当前 HEAD：0.1.<改动插件的提交数（不含 plugin.json）>，写回
.qoder-plugin/plugin.json；同一 commit 重复运行版本不变。插件目录打成
<仓库根>/global-user-constraints-<commit>.zip，commit 取 HEAD 短 id。
除 manifest 版本写回外，工作区有未提交改动时文件名追加 -dirty。
打包后检查 zip 结构，默认还会运行 Qoder 插件离线校验；校验器不存在
时跳过并提示。
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
PLUGIN_REL=".qoder/plugins/global-user-constraints"
PLUGIN_DIR="$REPO_ROOT/$PLUGIN_REL"
MANIFEST_REL="$PLUGIN_REL/.qoder-plugin/plugin.json"
VALIDATOR="$HOME/.qoder/plugins/cache/qoder-bundler/qoder-create-plugin/skills/create-plugin/scripts/validate_qoder_plugin.py"

if ! COMMIT="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null)"; then
  echo "无法读取 commit id：$REPO_ROOT 不是 git 仓库或尚无提交" >&2
  exit 1
fi

COUNT="$(git -C "$REPO_ROOT" rev-list --count HEAD -- "$PLUGIN_REL" ":!$PLUGIN_REL/.qoder-plugin/plugin.json")"
VERSION="0.1.$COUNT"

python3 - "$REPO_ROOT/$MANIFEST_REL" "$VERSION" <<'PY'
import json, sys

path, version = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
if data.get("version") != version:
    data["version"] = version
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
PY

DIRTY="$(git -C "$REPO_ROOT" status --porcelain --untracked-files=normal | grep -v " $MANIFEST_REL\$" || true)"
if [ -n "$DIRTY" ]; then
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

echo "插件版本 $VERSION；已生成 $OUT"
