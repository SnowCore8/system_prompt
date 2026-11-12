#!/usr/bin/env bash
# 全量校验：Markdown 格式、两份测试、shellcheck、JSON。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 2

SKILL_DIR="plugins/global-user-constraints/skills/system-prompt-authoring"
PLUGIN_DIR="plugins/global-user-constraints"
failures=0

fail() {
  printf '失败: %s\n' "$*" >&2
  failures=$((failures + 1))
}

skip() {
  printf '跳过: %s\n' "$*" >&2
}

command -v python3 >/dev/null 2>&1 || {
  echo "未找到 python3" >&2
  exit 2
}
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "需要在 git 仓库内运行" >&2
  exit 2
}
python3 -c 'import markdown_it' >/dev/null 2>&1 || {
  echo "缺少 markdown-it-py，先运行 python3 -m pip install -r requirements-dev.txt" >&2
  exit 2
}

echo "== Markdown 格式 =="
while IFS= read -r -d '' file; do
  if ! output="$(python3 "$SKILL_DIR/scripts/check.py" --strict "$file" 2>&1)"; then
    printf '%s\n' "$output"
    fail "$file"
  fi
done < <(git ls-files --cached --others --exclude-standard -z '*.md')

echo "== skill 测试 =="
python3 -B -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py' || fail "skill 测试"

echo "== hook 测试 =="
(cd "$PLUGIN_DIR" && python3 -B -m unittest discover -s scripts -p 'test_*.py') || fail "hook 测试"

echo "== shellcheck =="
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/dist.sh scripts/check.sh || fail "shellcheck"
else
  skip "未安装 shellcheck"
fi

echo "== JSON =="
while IFS= read -r -d '' file; do
  python3 -m json.tool "$file" >/dev/null 2>&1 || fail "JSON 无效: $file"
done < <(git ls-files --cached --others --exclude-standard -z '*.json')

echo "== 插件校验 =="
if command -v qoderclicn >/dev/null 2>&1; then
  qoderclicn plugins validate "$PLUGIN_DIR" || fail "插件校验"
else
  skip "未安装 qoderclicn"
fi

if [ "$failures" -ne 0 ]; then
  echo "校验失败: $failures 项" >&2
  exit 1
fi
echo "全部通过"
