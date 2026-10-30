#!/usr/bin/env bash
# 把用户级插件按平台打包到仓库根目录：版本随插件提交数递增，文件名带 commit id。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/dist.sh [--no-validate]

先运行 scripts/build-hooks.sh 编译 hook 二进制，再按平台各打一个包：
global-user-constraints-<commit>-linux-x64.zip（内为 inject-time）
global-user-constraints-<commit>-windows-x64.zip（内为 inject-time.exe）。
版本取自当前 HEAD：0.1.<改动插件的提交数（不含 plugin.json）>，写回
.qoder-plugin/plugin.json；同一 commit 重复运行版本不变。除 manifest 版本
写回外，工作区有未提交改动时文件名追加 -dirty。打包后检查 zip 结构，默认
还会运行 Qoder 插件离线校验；校验器不存在时跳过并提示。
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

"$REPO_ROOT/scripts/build-hooks.sh"

STAGE_ROOT="$(mktemp -d)"
trap 'rm -rf "$STAGE_ROOT"' EXIT

package() {
  local target="$1" binary="$2" other="$3"
  local stage="$STAGE_ROOT/$target"
  local out="$REPO_ROOT/global-user-constraints-$COMMIT-$target.zip"

  mkdir -p "$stage"
  (cd "$PLUGIN_DIR" && tar -cf - --exclude='__pycache__' --exclude='*.pyc' .) \
    | (cd "$stage" && tar -xf -)
  rm -f "$stage/scripts/bin/$other"
  cp "$PLUGIN_DIR/scripts/bin/$binary" "$stage/scripts/bin/$binary"
  chmod +x "$stage/scripts/bin/$binary"

  python3 - "$stage/hooks/hooks.json" "$binary" <<'PY'
import json, sys

path, binary = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
for groups in data["hooks"].values():
    for group in groups:
        for handler in group["hooks"]:
            if handler.get("type") == "command":
                handler["command"] = "${QODER_PLUGIN_ROOT}/scripts/bin/" + binary
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY

  rm -f "$out"
  (cd "$stage" && zip -qr "$out" . \
    -x "**/.DS_Store" "__MACOSX/*" "**/__pycache__/*" "**/*.pyc")

  python3 - "$out" "$binary" "$other" <<'PY'
import json, sys, zipfile

path, binary, other = sys.argv[1], sys.argv[2], sys.argv[3]
with zipfile.ZipFile(path) as zf:
    names = zf.namelist()
    hooks = json.loads(zf.read("hooks/hooks.json"))

problems = []
if ".qoder-plugin/plugin.json" not in names:
    problems.append("缺少 .qoder-plugin/plugin.json")
if f"scripts/bin/{binary}" not in names:
    problems.append(f"缺少 scripts/bin/{binary}")
if f"scripts/bin/{other}" in names:
    problems.append(f"混入其他平台二进制 scripts/bin/{other}")
if any(name.startswith("scripts/") and name.endswith(".py") for name in names):
    problems.append("scripts/ 下残留 Python 脚本")
for name in names:
    if name.startswith("/") or ".." in name.split("/"):
        problems.append(f"非法路径: {name}")
if any(name.endswith(".pyc") or "__pycache__" in name for name in names):
    problems.append("包含 Python 缓存")
for event, groups in hooks["hooks"].items():
    for group in groups:
        for handler in group["hooks"]:
            expected = "${QODER_PLUGIN_ROOT}/scripts/bin/" + binary
            if handler.get("command") != expected:
                problems.append(f"{event} 的 command 不是 {expected}")
if problems:
    sys.exit("zip 结构校验失败:\n- " + "\n- ".join(problems))

print(f"zip 结构校验通过: {len(names)} 个条目")
PY

  if [ "$VALIDATE" -eq 1 ]; then
    if [ -f "$VALIDATOR" ]; then
      python3 "$VALIDATOR" "$out"
    else
      echo "跳过离线校验: 未找到 $VALIDATOR" >&2
    fi
  fi
}

package linux-x64 inject-time inject-time.exe
package windows-x64 inject-time.exe inject-time

echo "插件版本 $VERSION；已生成 $REPO_ROOT/global-user-constraints-$COMMIT-{linux-x64,windows-x64}.zip"
