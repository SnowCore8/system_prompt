#!/usr/bin/env bash
# 分别打包 Qoder、Qwen Code、DeepSeek Harness 三个包；版本取各包清单并强制一致。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/dist.sh [--allow-dirty] [--no-validate] [--require-tag]

三个包分别是 plugins/qoder、plugins/qwen 与 plugins/dsh，版本以各自清单为准：
`.qoder-plugin/plugin.json`、`qwen-extension.json`、`package.json` 的 version 必须一致
（SemVer），输出 global-user-constraints-<包名>-<版本>.zip 与对应 .sha256。

仓库里三个包用相对软链引用共享的 skills/、rules/ 与 shared/；打包时通过
scripts/materialize.sh 物化成自包含目录，Qoder 的 plugins validate 也会拒绝包外路径。

默认要求工作区干净；--allow-dirty 放行并在文件名加 -dirty。浅克隆直接拒绝。
--require-tag 要求 HEAD 正好带有 v<version> 注释 tag，发布流水线用它出包。
每个包会附上双许可证、归一 mtime 与权限、按名称排序并用 zip -X 构建，产物可复现；
默认还用 qoderclicn 校验物化后的 Qoder 包，缺失时失败，可用 --no-validate 跳过
（CI 发布流水线没有 qoderclicn，用跳过换取可重复构建，发布前须在本地校验）。
每个包保留最近三个制品。
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
cd "$REPO_ROOT"

for tool in git python3 zip; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "缺少命令: $tool" >&2
    exit 1
  }
done

COMMIT="$(git rev-parse --short HEAD 2>/dev/null)" || {
  echo "无法读取 commit id：不是 git 仓库或尚无提交" >&2
  exit 1
}
if [ "$(git rev-parse --is-shallow-repository 2>/dev/null || echo false)" = "true" ]; then
  echo "浅克隆无法可靠引用 tag：请先 git fetch --unshallow" >&2
  exit 1
fi

VERSION="$(python3 - "$REPO_ROOT" <<'PY'
import json, re, sys
from pathlib import Path

root = Path(sys.argv[1])
paths = {
    "qoder": root / "plugins/qoder/.qoder-plugin/plugin.json",
    "qwen": root / "plugins/qwen/qwen-extension.json",
    "dsh": root / "package.json",
}
versions = {name: json.loads(path.read_text(encoding="utf-8")).get("version") for name, path in paths.items()}
for name, version in versions.items():
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version or "")):
        sys.exit(f"{name} 的 version 不是 SemVer: {version!r}")
if len(set(versions.values())) != 1:
    sys.exit(f"三包版本不一致: {versions}")
print(versions["qoder"])
PY
)"

if [ "$REQUIRE_TAG" -eq 1 ]; then
  TAG="$(git describe --exact-match --tags HEAD 2>/dev/null || true)"
  if [ "$TAG" != "v$VERSION" ]; then
    echo "--require-tag: HEAD 的 tag 为 '${TAG:-无}'，期望 v$VERSION" >&2
    exit 1
  fi
fi

DIRTY="$(git status --porcelain --untracked-files=normal || true)"
SUFFIX=""
if [ -n "$DIRTY" ]; then
  if [ "$ALLOW_DIRTY" -ne 1 ]; then
    echo "工作区有未提交改动：先提交，或显式使用 --allow-dirty 打包" >&2
    exit 1
  fi
  SUFFIX="-dirty"
  echo "工作区有未提交改动，文件名标记 -dirty" >&2
fi

verify_zip() {
  local name="$1" path="$2"
  python3 - "$name" "$path" "$VERSION" <<'PY'
import json, sys, zipfile

name, path, version = sys.argv[1], sys.argv[2], sys.argv[3]
required = {
    "qoder": [".qoder-plugin/plugin.json", "hooks/hooks.json", "rules/global-user-constraints.md"],
    "qwen": ["qwen-extension.json", "hooks/qwen-hooks.json", "constraints/global-user-constraints.md"],
    "dsh": ["package.json", "plugins/dsh/cordis.patch.yml", "plugins/dsh/src/index.js",
            "rules/global-user-constraints.md"],
}[name] + ["LICENSE", "LICENSE-CC-BY-4.0.txt", "LICENSE-MIT.txt", "THIRD-PARTY-NOTICES.md"]

with zipfile.ZipFile(path) as zf:
    infos = zf.infolist()
    names = zf.namelist()
    manifest = {
        "qoder": ".qoder-plugin/plugin.json",
        "qwen": "qwen-extension.json",
        "dsh": "package.json",
    }[name]
    embedded_version = json.loads(zf.read(manifest)).get("version") if manifest in names else None

problems = []
for item in required:
    if item not in names:
        problems.append(f"缺少 {item}")
if embedded_version != version:
    problems.append(f"包内版本 {embedded_version!r} 与 {version} 不一致")
skills = [entry for entry in names if entry.count("/") == 2 and entry.endswith("/SKILL.md")]
if len(skills) != 18:
    problems.append(f"skill 数量为 {len(skills)}，期望 18")
for info in infos:
    mode = (info.external_attr >> 16) & 0o170000
    if mode == 0o120000:
        problems.append(f"包含未解引用的软链: {info.filename}")
    if info.filename.endswith(".pyc") or "__pycache__" in info.filename:
        problems.append(f"包含 Python 缓存: {info.filename}")

allowed = {
    "qoder": (".qoder-plugin/", "hooks/", "rules/", "skills/", "commands/", "scripts/", "README.md", "LICENSE", "THIRD-PARTY-NOTICES.md"),
    "qwen": ("qwen-extension.json", "hooks/", "constraints/", "skills/", "commands/", "scripts/", "README.md", "LICENSE", "THIRD-PARTY-NOTICES.md"),
    "dsh": ("package.json", "plugins/dsh/", "skills/", "rules/", "README.md", "LICENSE", "THIRD-PARTY-NOTICES.md"),
}[name]
for entry in names:
    permitted = any(entry == prefix or entry.startswith(prefix) for prefix in allowed)
    if not permitted and entry.endswith("/"):
        permitted = any(prefix.startswith(entry) for prefix in allowed)
    if not permitted:
        problems.append(f"不属于该包的内容: {entry}")
    if "/test_" in entry or entry.endswith(".test.mjs") or "__pycache__" in entry:
        problems.append(f"包含开发测试: {entry}")
if problems:
    sys.exit("zip 结构校验失败:\n- " + "\n- ".join(problems))
print(f"{name}: zip 结构校验通过（{len(names)} 个条目）")
PY
}

retain() {
  local name="$1" old
  mapfile -t zips < <(ls -1t "$REPO_ROOT"/global-user-constraints-"$name"-*.zip 2>/dev/null || true)
  if [ "${#zips[@]}" -gt 3 ]; then
    for old in "${zips[@]:3}"; do
      rm -f "$old" "${old%.zip}.sha256"
      echo "已删除较旧制品: $(basename "$old")" >&2
    done
  fi
}

# 自检失败时 EXIT trap 不在函数作用域内运行，局部变量那时已消失；用全局变量承载临时目录。
STAGE_DIR=""
BUILD_DIR=""

cleanup_dirs() {
  rm -rf "${STAGE_DIR:-}" "${BUILD_DIR:-}"
}

trap cleanup_dirs EXIT

build_one() {
  local name="$1" zip out sums
  STAGE_DIR="$(mktemp -d)"
  BUILD_DIR="$(mktemp -d)"

  bash scripts/materialize.sh "$name" "$STAGE_DIR/pkg" >/dev/null

  zip="$BUILD_DIR/out.zip"
  find "$STAGE_DIR/pkg" -type d -exec chmod 755 {} +
  find "$STAGE_DIR/pkg" -type f -exec chmod 644 {} +
  find "$STAGE_DIR/pkg" -exec touch -t 198001010000 {} +
  (
    cd "$STAGE_DIR/pkg"
    find . -mindepth 1 \
      ! -name '.DS_Store' ! -path '*/__pycache__/*' ! -name '*.pyc' \
      -printf '%P\n' | LC_ALL=C sort | zip -X -q "$zip" -@
  )

  verify_zip "$name" "$zip"

  if [ "$VALIDATE" -eq 1 ] && [ "$name" = "qoder" ]; then
    if ! command -v qoderclicn >/dev/null 2>&1; then
      echo "插件校验失败: 未找到 qoderclicn；安装后重试，或显式使用 --no-validate 跳过" >&2
      exit 1
    fi
    qoderclicn plugins validate "$STAGE_DIR/pkg"
  fi

  out="$REPO_ROOT/global-user-constraints-$name-$VERSION$SUFFIX.zip"
  sums="${out%.zip}.sha256"
  mv "$zip" "$out"
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$REPO_ROOT" && sha256sum "$(basename "$out")") > "$sums"
  else
    (cd "$REPO_ROOT" && shasum -a 256 "$(basename "$out")") > "$sums"
  fi
  echo "已生成 $(basename "$out") 与 $(basename "$sums")"

  rm -rf "$STAGE_DIR" "$BUILD_DIR"
  STAGE_DIR=""
  BUILD_DIR=""
  retain "$name"
}

for package in qoder qwen dsh; do
  build_one "$package"
done

echo "版本 $VERSION（commit $COMMIT）；三个包已生成于 $REPO_ROOT"
