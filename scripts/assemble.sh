#!/usr/bin/env bash
# 从顶层真源组装三端项目级入口；开发目录不提交，避免软链与复制漂移。
set -euo pipefail

usage() {
  cat <<'EOF'
用法: scripts/assemble.sh [dev|qoder|--check]

dev     生成 .dsh/skills、.qoder/rules、.qoder/skills、.qwen/rules、.qwen/skills；
        这些目录被 .gitignore 忽略，不提交。
qoder   生成 plugins/qoder 的 skills/rules/commands/scripts，供 Qoder 本地市场使用；
        生成目录被 .gitignore 忽略，不提交。
--check 在临时目录组装并校验 19 个 skill、两个 rules 入口与零软链，不改工作区。
EOF
}

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-dev}"

assemble_into() {
  local root="$1"
  rm -rf "$root/.dsh/skills" "$root/.qoder/rules" "$root/.qoder/skills" \
    "$root/.qwen/rules" "$root/.qwen/skills"
  mkdir -p "$root/.dsh/skills" "$root/.qoder/rules" "$root/.qoder/skills" \
    "$root/.qwen/rules" "$root/.qwen/skills"
  cp -a "$REPO_ROOT/skills/." "$root/.dsh/skills/"
  cp -a "$REPO_ROOT/skills/." "$root/.qoder/skills/"
  cp -a "$REPO_ROOT/skills/." "$root/.qwen/skills/"
  cp -a "$REPO_ROOT/rules/." "$root/.qoder/rules/"
  cp -a "$REPO_ROOT/rules/." "$root/.qwen/rules/"
}

assemble_qoder_local() {
  local pkg="$REPO_ROOT/plugins/qoder"
  rm -rf "$pkg/skills" "$pkg/rules" "$pkg/commands" "$pkg/scripts"
  cp -a "$REPO_ROOT/skills" "$pkg/skills"
  cp -a "$REPO_ROOT/rules" "$pkg/rules"
  cp -a "$REPO_ROOT/shared/commands" "$pkg/commands"
  cp -a "$REPO_ROOT/shared/scripts" "$pkg/scripts"
}

check_assembly() {
  local root="$1" expected actual dir name front
  expected="$(find "$REPO_ROOT/skills" -mindepth 1 -maxdepth 1 -type d | wc -l)"
  actual="$(find "$root/.dsh/skills" -mindepth 1 -maxdepth 1 -type d | wc -l)"
  [ "$actual" -eq "$expected" ] || { echo "组装后 skill 数量 $actual，期望 $expected" >&2; exit 1; }
  if [ -n "$(find "$root/.dsh" "$root/.qoder" "$root/.qwen" -type l -print -quit)" ]; then
    echo "组装结果包含软链" >&2
    exit 1
  fi
  for dir in "$root/.dsh/skills"/*; do
    [ -d "$dir" ] || continue
    name="$(basename "$dir")"
    [ -f "$dir/SKILL.md" ] || { echo "缺少 $name/SKILL.md" >&2; exit 1; }
    front="$(sed -n 's/^name:[[:space:]]*//p' "$dir/SKILL.md" | head -n 1 | tr -d '\r')"
    [ "$front" = "$name" ] || { echo "$name 的 frontmatter name 为 '$front'" >&2; exit 1; }
  done
  [ -f "$root/.qoder/rules/global-user-constraints.md" ] || { echo "Qoder rules 缺失" >&2; exit 1; }
  [ -f "$root/.qwen/rules/global-user-constraints.md" ] || { echo "Qwen rules 缺失" >&2; exit 1; }
  echo "组装校验通过：$actual 个 skill，0 个软链"
}

case "$MODE" in
  dev)
    assemble_into "$REPO_ROOT"
    check_assembly "$REPO_ROOT"
    ;;
  qoder)
    assemble_qoder_local
    echo "Qoder 本地市场包已生成：plugins/qoder（生成目录不提交）"
    ;;
  --check)
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    assemble_into "$tmp"
    check_assembly "$tmp"
    ;;
  -h|--help) usage ;;
  *) usage >&2; exit 2 ;;
esac
