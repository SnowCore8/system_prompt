#!/usr/bin/env bash
# 把用户级插件打包到仓库根目录：版本取插件 manifest 的 SemVer，文件名带版本号。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/dist.sh [--allow-dirty] [--no-validate] [--require-tag]

插件版本以 plugins/global-user-constraints/.qoder-plugin/plugin.json 的 version
为准，发布流程要求它是 SemVer（如 0.2.0）。脚本不再推导或改写版本：
升级版本时手动修改 manifest，单独提交后打 tag，再用本脚本出包。

默认要求工作区干净；仅当显式给出 --allow-dirty 时允许从脏工作区打包，文件名追加
-dirty。浅克隆直接拒绝。--require-tag 要求 HEAD 正好带有 v<version> 注释 tag，
发布流水线用它在 tag 上出包。

包内会下载入仓库根的双许可证文件（LICENSE、LICENSE-CC-BY-4.0.txt、
LICENSE-MIT.txt）；插件目录内的 rules/ 软链会解引用为真实文件，约束正文随包分发。
排除 .DS_Store、__pycache__ 与 .pyc；打包前归一文件时间戳并按名称排序，
用 zip -X 去除额外属性，因此同一版本、同一 tag 的产物字节可复现。
打包后校验 zip 结构并输出 <zip>.sha256 校验和，默认还用 qoderclicn
plugins validate 校验插件目录；qoderclicn 缺失时默认失败，可用 --no-validate 跳过
（CI 发布流水线没有 qoderclicn，用跳过换取可重复构建，发布前须在本地校验）。
所有校验通过后才落盘制品；失败不会留下半成品。
校验通过后删除较旧制品，只保留最近三个 zip 及其校验和。
EOF
}

VALIDATE=1
ALLOW_DIRTY=0
REQUIRE_TAG=0
for arg in "$@"; do
  case "$arg" in
    --no-validate) VALIDATE=0 ;;
    --allow-dirty) ALLOW_DIRTY=1 ;;
    --require-tag) REQUIRE_TAG=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_REL="plugins/global-user-constraints"
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
  echo "浅克隆无法可靠引用 tag：请先 git fetch --unshallow" >&2
  exit 1
fi

VERSION="$(python3 - "$REPO_ROOT/$MANIFEST_REL" <<'PY'
import json, re, sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    version = json.load(f).get("version", "")
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    sys.exit(f"manifest 的 version 不是 SemVer: {version!r}")
print(version)
PY
)"

if [ "$REQUIRE_TAG" -eq 1 ]; then
  TAG="$(git -C "$REPO_ROOT" describe --exact-match --tags HEAD 2>/dev/null || true)"
  if [ "$TAG" != "v$VERSION" ]; then
    echo "--require-tag: HEAD 的 tag 为 '${TAG:-无}'，期望 v$VERSION" >&2
    exit 1
  fi
fi

DIRTY="$(git -C "$REPO_ROOT" status --porcelain --untracked-files=normal || true)"
SUFFIX=""
if [ -n "$DIRTY" ]; then
  if [ "$ALLOW_DIRTY" -ne 1 ]; then
    echo "工作区有未提交改动：先提交，或显式使用 --allow-dirty 打包" >&2
    exit 1
  fi
  SUFFIX="-dirty"
  echo "工作区有未提交改动，文件名标记 -dirty" >&2
fi
OUT="$REPO_ROOT/global-user-constraints-$VERSION$SUFFIX.zip"
SUMS="$REPO_ROOT/global-user-constraints-$VERSION$SUFFIX.sha256"

STAGE="$(mktemp -d)"
BUILD="$(mktemp -d)"
ZIPTMP="$BUILD/out.zip"
trap 'rm -rf "$STAGE" "$BUILD"' EXIT

# 插件目录内的 rules 是指向仓库根级 rules/ 的软链；解引用后进包，包里是真实文件
cp -aL "$PLUGIN_DIR/." "$STAGE/"
# 双许可证随包分发，使用者拿到 zip 即可确认授权范围
cp "$REPO_ROOT/LICENSE" "$REPO_ROOT/LICENSE-CC-BY-4.0.txt" "$REPO_ROOT/LICENSE-MIT.txt" "$STAGE/"

# 归一权限与 mtime，并按名称排序，配合 zip -X 让同一版本、同一 tag 的产物字节可复现
find "$STAGE" -type d -exec chmod 755 {} +
find "$STAGE" -type f -exec chmod 644 {} +
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

mv "$ZIPTMP" "$OUT"
if command -v sha256sum >/dev/null 2>&1; then
  (cd "$REPO_ROOT" && sha256sum "$(basename "$OUT")") > "$SUMS"
else
  (cd "$REPO_ROOT" && shasum -a 256 "$(basename "$OUT")") > "$SUMS"
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

echo "插件版本 $VERSION（commit $COMMIT）；已生成 $OUT"
