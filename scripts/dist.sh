#!/usr/bin/env bash
# 把用户级插件打包到仓库根目录：版本随插件提交数递增，文件名带当前 commit id。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/dist.sh [--allow-dirty] [--no-validate]

版本取自当前 HEAD：0.1.<改动插件的提交数（不含 plugin.json）>，写回
.qoder-plugin/plugin.json；迁移前的 .qoder/plugins 路径一并计入，同一 commit
重复运行版本不变。插件目录打成
<仓库根>/global-user-constraints-<commit>.zip，commit 取 HEAD 短 id。

默认要求工作区干净；仅当显式给出 --allow-dirty 时允许从脏工作区打包，文件名追加
-dirty。浅克隆无法推导稳定版本，直接拒绝。
包内会下载入仓库根的双许可证文件（LICENSE、LICENSE-CC-BY-4.0.txt、
LICENSE-MIT.txt）；插件目录内的 rules/ 软链会解引用为真实文件，约束正文随包分发。
排除 .DS_Store、__pycache__ 与 .pyc；打包前归一文件时间戳并按名称排序，
用 zip -X 去除额外属性，因此同一 commit 的产物字节可复现。
打包后校验 zip 结构并输出 <zip>.sha256 校验和，默认还用 qoderclicn
plugins validate 校验插件目录；qoderclicn 缺失时默认失败，可用 --no-validate 跳过。
所有校验通过后才写回 manifest 并落盘制品；此前失败不会留下半成品。
校验通过后删除较旧制品，只保留最近三个 zip 及其校验和。
EOF
}

VALIDATE=1
ALLOW_DIRTY=0
for arg in "$@"; do
  case "$arg" in
    --no-validate) VALIDATE=0 ;;
    --allow-dirty) ALLOW_DIRTY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_REL="plugins/global-user-constraints"
PLUGIN_LEGACY_REL=".qoder/plugins/global-user-constraints"
PLUGIN_DIR="$REPO_ROOT/$PLUGIN_REL"
MANIFEST_REL="$PLUGIN_REL/.qoder-plugin/plugin.json"

for tool in git python3 zip; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "缺少命令: $tool" >&2
    exit 1
  }
done

if ! COMMIT="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null)"; then
  echo "无法读取 commit id：$REPO_ROOT 不是 git 仓库或尚无提交" >&2
  exit 1
fi
if [ "$(git -C "$REPO_ROOT" rev-parse --is-shallow-repository 2>/dev/null || echo false)" = "true" ]; then
  echo "浅克隆无法稳定推导版本：请先 git fetch --unshallow" >&2
  exit 1
fi

# 插件曾位于 .qoder/plugins/ 下，迁移前的提交一并计入，避免版本回退
COUNT="$(git -C "$REPO_ROOT" rev-list --count HEAD -- "$PLUGIN_REL" "$PLUGIN_LEGACY_REL" \
  ":!$PLUGIN_REL/.qoder-plugin/plugin.json" ":!$PLUGIN_LEGACY_REL/.qoder-plugin/plugin.json")"
VERSION="0.1.$COUNT"

DIRTY="$(git -C "$REPO_ROOT" status --porcelain --untracked-files=normal | grep -v " $MANIFEST_REL\$" || true)"
if [ -n "$DIRTY" ]; then
  if [ "$ALLOW_DIRTY" -ne 1 ]; then
    echo "工作区有未提交改动：先提交，或显式使用 --allow-dirty 打包" >&2
    exit 1
  fi
  COMMIT="$COMMIT-dirty"
  echo "工作区有未提交改动，文件名标记 -dirty" >&2
fi
OUT="$REPO_ROOT/global-user-constraints-$COMMIT.zip"
SUMS="$REPO_ROOT/global-user-constraints-$COMMIT.sha256"

STAGE="$(mktemp -d)"
BUILD="$(mktemp -d)"
ZIPTMP="$BUILD/out.zip"
trap 'rm -rf "$STAGE" "$BUILD"' EXIT

# 插件目录内的 rules 是指向仓库根级 rules/ 的软链；解引用后进包，包里是真实文件
cp -aL "$PLUGIN_DIR/." "$STAGE/"
# 双许可证随包分发，使用者拿到 zip 即可确认授权范围
cp "$REPO_ROOT/LICENSE" "$REPO_ROOT/LICENSE-CC-BY-4.0.txt" "$REPO_ROOT/LICENSE-MIT.txt" "$STAGE/"

# 版本先写入暂存区副本，仓库 manifest 等全部校验通过后再更新
python3 - "$STAGE/.qoder-plugin/plugin.json" "$VERSION" <<'PY'
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

# 归一 mtime 并按名称排序，配合 zip -X 让同一 commit 的产物字节可复现
find "$STAGE" -exec touch -t 198001010000 {} +
(
  cd "$STAGE"
  find . -mindepth 1 \
    ! -name '.DS_Store' ! -path '*/__pycache__/*' ! -name '*.pyc' \
    -printf '%P\n' | LC_ALL=C sort | zip -X -q "$ZIPTMP" -@
)

python3 - "$ZIPTMP" <<'PY'
import sys, zipfile

path = sys.argv[1]
with zipfile.ZipFile(path) as zf:
    names = zf.namelist()

problems = []
for required in (
    ".qoder-plugin/plugin.json",
    "rules/global-user-constraints.md",
    "LICENSE",
    "LICENSE-CC-BY-4.0.txt",
    "LICENSE-MIT.txt",
):
    if required not in names:
        problems.append(f"缺少 {required}")
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
  if ! command -v qoderclicn >/dev/null 2>&1; then
    echo "插件校验失败: 未找到 qoderclicn；安装后重试，或显式使用 --no-validate 跳过" >&2
    exit 1
  fi
  qoderclicn plugins validate "$STAGE"
fi

# 全部校验通过：写回仓库 manifest，原子落盘 zip 与校验和
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

mv "$ZIPTMP" "$OUT"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$OUT" > "$SUMS"
else
  shasum -a 256 "$OUT" > "$SUMS"
fi
echo "已生成校验和: $(basename "$SUMS")"

# 保留本次与最近两个旧制品，其余删除，避免历史制品无限堆积
mapfile -t zips < <(ls -1t "$REPO_ROOT"/global-user-constraints-*.zip 2>/dev/null || true)
if [ "${#zips[@]}" -gt 3 ]; then
  for old in "${zips[@]:3}"; do
    rm -f "$old" "${old%.zip}.sha256"
    echo "已删除较旧制品: $(basename "$old")" >&2
  done
fi

echo "插件版本 $VERSION；已生成 $OUT"
