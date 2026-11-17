#!/usr/bin/env bash
# 全量校验：Markdown、skill 与 hook 测试、shellcheck、ruff、JSON、敏感文件、软链、三工具适配、三包清单与校验。
# 故意不加 -e：要累积全部失败项后统一非零退出，而不是首错即停。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 2

SKILL_DIR="skills/system-prompt-authoring"
failures=0
skips=0

fail() {
  printf '失败: %s\n' "$*" >&2
  failures=$((failures + 1))
}

skip() {
  skips=$((skips + 1))
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
python3 -m ruff --version >/dev/null 2>&1 || {
  echo "缺少 ruff，先运行 python3 -m pip install -r requirements-dev.txt" >&2
  exit 2
}
python3 -c 'import coverage' >/dev/null 2>&1 || {
  echo "缺少 coverage，先运行 python3 -m pip install -r requirements-dev.txt" >&2
  exit 2
}
python3 -m pip_audit --version >/dev/null 2>&1 || {
  echo "缺少 pip-audit，先运行 python3 -m pip install -r requirements-dev.txt" >&2
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
python3 -B -m unittest discover -s tests/skill -p 'test_*.py' || fail "skill 测试"

echo "== hook 测试 =="
python3 -B -m unittest discover -s tests/hooks -p 'test_*.py' || fail "hook 测试"

echo "== DSH 包测试 =="
if command -v node >/dev/null 2>&1; then
  node --test tests/dsh/provider.test.mjs || fail "DSH 包测试"
else
  skip "未安装 node"
fi

echo "== shellcheck =="
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/dist.sh scripts/check.sh || fail "shellcheck"
else
  skip "未安装 shellcheck"
fi

echo "== Python lint =="
python3 -m ruff check . || fail "ruff"

echo "== 依赖审计 =="
audit_cache="$(mktemp -d)"
python3 -m pip_audit --cache-dir "$audit_cache" -r requirements-dev.txt || fail "pip-audit"
rm -rf "$audit_cache"

echo "== 覆盖率 =="
cov_cfg="$(mktemp)"
printf '[run]\nbranch = true\nparallel = true\nsource = %s/shared/scripts,%s/skills/system-prompt-authoring/scripts\ndata_file = %s/.coverage\ndisable_warnings = no-data-collected\n' \
  "$REPO_ROOT" "$REPO_ROOT" "$REPO_ROOT" > "$cov_cfg"
COVERAGE_PROCESS_START="$cov_cfg" python3 -B -m coverage run --rcfile="$cov_cfg" -m unittest discover -s tests/skill -p 'test_*.py' || fail "覆盖率 skill 测试"
COVERAGE_PROCESS_START="$cov_cfg" python3 -B -m coverage run --rcfile="$cov_cfg" -m unittest discover -s tests/hooks -p 'test_*.py' || fail "覆盖率 hook 测试"
python3 -m coverage combine --rcfile="$cov_cfg" >/dev/null 2>&1 || fail "覆盖率合并"
python3 -m coverage report --rcfile="$cov_cfg" --fail-under=90 || fail "覆盖率低于 90%"
rm -f "$cov_cfg" .coverage .coverage.*

echo "== JSON =="
while IFS= read -r -d '' file; do
  python3 -m json.tool "$file" >/dev/null 2>&1 || fail "JSON 无效: $file"
done < <(git ls-files --cached --others --exclude-standard -z '*.json')

echo "== 敏感文件 =="
for ignored in .env .qwen/.env .qwen/settings.local.json .qwen/tmp/ .qoder/settings.local.json; do
  git check-ignore -q --no-index "$ignored" || fail "未忽略敏感路径: $ignored"
done
if git grep -n -I -E '-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----' -- \
  '*.py' '*.sh' '*.json' '*.yml' '*.yaml' >/dev/null 2>&1; then
  fail "疑似私钥内容已入库"
fi

echo "== 软链 =="
link_fs=0
while IFS= read -r link; do
  link="${link#./}"
  if git check-ignore -q --no-index "$link"; then
    continue
  fi
  link_fs=$((link_fs + 1))
  git ls-files --error-unmatch "$link" >/dev/null 2>&1 || fail "软链未纳入版本库: $link"
  target="$(readlink "$link")"
  case "$target" in
    /*)
      fail "软链使用绝对路径: $link -> $target"
      continue
      ;;
  esac
  target_path="$(dirname "$link")/$target"
  [ -L "$target_path" ] && fail "软链指向另一软链: $link -> $target"
  if ! resolved="$(readlink -f "$link")"; then
    fail "软链无法解析: $link -> $target"
    continue
  fi
  case "$resolved" in
    "$REPO_ROOT"/*) ;;
    *)
      fail "软链目标在仓库外: $link -> $resolved"
      continue
      ;;
  esac
  case "$resolved" in
    "$REPO_ROOT/.git"/*)
      fail "软链指向 .git: $link -> $resolved"
      continue
      ;;
  esac
  [ -e "$resolved" ] || fail "软链目标不存在: $link -> $target"
  rel_resolved="${resolved#"$REPO_ROOT"/}"
  if [ -d "$resolved" ]; then
    [ -n "$(git ls-files -- "$rel_resolved" | head -n 1)" ] || fail "软链指向未跟踪目录: $link"
  else
    git ls-files --error-unmatch "$rel_resolved" >/dev/null 2>&1 || fail "软链指向未跟踪文件: $link"
  fi
done < <(find . -type l -not -path './.git/*' -print)
link_git="$(git ls-files -s | awk '$1=="120000"' | wc -l)"
[ "$link_fs" -eq "$link_git" ] || fail "软链数量不一致：工作区 $link_fs，版本库 $link_git"

plugin_skill_dirs="$(find skills -mindepth 1 -maxdepth 1 -type d | wc -l)"

# 校验一个项目级 skill 入口：每项都是软链、可解析、含 SKILL.md，且 frontmatter name 与目录名一致。
check_skill_root() {
  local label="$1" root="$2" link_count=0 link name target front_name
  for link in "$root"/*; do
    [ -L "$link" ] || {
      [ -e "$link" ] && fail "$label: $link 不是软链"
      continue
    }
    link_count=$((link_count + 1))
    name="$(basename "$link")"
    if ! target="$(readlink -f "$link")"; then
      fail "$label: 无法解析 $link"
      continue
    fi
    [ -f "$target/SKILL.md" ] || {
      fail "$label: $name 缺少 SKILL.md"
      continue
    }
    front_name="$(sed -n 's/^name:[[:space:]]*//p' "$target/SKILL.md" | head -n 1 | tr -d '\r')"
    [ "$front_name" = "$name" ] || fail "$label: $name 的 frontmatter name 为 '$front_name'"
  done
  [ "$link_count" -eq "$plugin_skill_dirs" ] || fail "$label: 软链 $link_count 个，顶层 skill $plugin_skill_dirs 个"
}

echo "== DSH 适配 =="
check_skill_root "DSH" ".dsh/skills"
[ -f rules/global-user-constraints.md ] || fail "DSH: 缺少约束正文 rules/global-user-constraints.md"
[ -f CONTRIBUTING.md ] || fail "DSH: 缺少项目维护约定 CONTRIBUTING.md"
if [ -L AGENTS.md ] && [ "$(readlink -f AGENTS.md)" = "$REPO_ROOT/CONTRIBUTING.md" ]; then
  :
else
  fail "DSH: AGENTS.md 未指向项目维护约定 CONTRIBUTING.md"
fi

echo "== Qoder 适配 =="
if [ ! -d .qoder ] || [ -L .qoder ]; then
  fail "Qoder: .qoder 应为普通目录"
fi
if [ -e .qoder-cn ] || [ -L .qoder-cn ]; then
  fail "Qoder: 项目级不读 .qoder-cn，应删除"
fi
if [ -e .qoder/plugins ] || [ -L .qoder/plugins ]; then
  fail "Qoder: 项目级不扫描 .qoder/plugins，应删除"
fi
if [ -L .qoder/rules ] && [ "$(readlink -f .qoder/rules)" = "$REPO_ROOT/rules" ]; then
  :
else
  fail "Qoder: .qoder/rules 未指向 rules/"
fi
if [ ! -d .qoder/skills ] || [ -L .qoder/skills ]; then
  fail "Qoder: .qoder/skills 应为普通目录"
fi
check_skill_root "Qoder" ".qoder/skills"

echo "== Qwen 适配 =="
if [ ! -d .qwen ] || [ -L .qwen ]; then
  fail "Qwen: .qwen 应为普通目录"
fi
if [ -e .qwen/AGENTS.md ] || [ -L .qwen/AGENTS.md ]; then
  fail "Qwen: 不读取项目级 .qwen/AGENTS.md，应删除"
fi
if [ -L .qwen/rules ] && [ "$(readlink -f .qwen/rules)" = "$REPO_ROOT/rules" ]; then
  :
else
  fail "Qwen: .qwen/rules 未指向 rules/"
fi
if [ ! -f .qwen/rules/global-user-constraints.md ]; then
  fail "Qwen: .qwen/rules 下缺少约束正文"
fi
if [ ! -d .qwen/skills ] || [ -L .qwen/skills ]; then
  fail "Qwen: .qwen/skills 应为普通目录"
fi
check_skill_root "Qwen" ".qwen/skills"
if head -n 10 rules/global-user-constraints.md | grep -q '^paths:'; then
  fail "Qwen: 约束正文 front matter 含 paths，会变成条件规则"
fi

echo "== 插件清单 =="
if ! python3 - "$REPO_ROOT" <<'PY'
import json, re, sys
from pathlib import Path

root = Path(sys.argv[1])
packages = {
    "qoder": root / "plugins/qoder",
    "qwen": root / "plugins/qwen",
    "dsh": root / "plugins/dsh",
}
qoder = json.loads((packages["qoder"] / ".qoder-plugin/plugin.json").read_text(encoding="utf-8"))
qwen = json.loads((packages["qwen"] / "qwen-extension.json").read_text(encoding="utf-8"))
dsh = json.loads((root / "package.json").read_text(encoding="utf-8"))
problems = []
versions = {"qoder": qoder.get("version"), "qwen": qwen.get("version"), "dsh": dsh.get("version")}
for name, version in versions.items():
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version or "")):
        problems.append(f"{name} manifest 版本不是 SemVer")
if len(set(versions.values())) != 1:
    problems.append(f"三包版本不一致: {versions}")
if not (packages["qwen"] / str(qwen.get("hooks", ""))).is_file():
    problems.append("Qwen extension 的 hooks 路径不存在")
for key in ("skills", "commands"):
    if not (packages["qwen"] / str(qwen.get(key, ""))).is_dir():
        problems.append(f"Qwen extension 的 {key} 路径不存在")
if not (packages["qoder"] / str(qoder.get("hooks", ""))).is_file():
    problems.append("Qoder 插件的 hooks 路径不存在")
if not (packages["qoder"] / str(qoder.get("skills", ""))).is_dir():
    problems.append("Qoder 插件的 skills 路径不存在")
for command_name, command in (qoder.get("commands") or {}).items():
    source = command.get("source") if isinstance(command, dict) else None
    if not source or not (packages["qoder"] / str(source)).is_file():
        problems.append(f"Qoder 命令 {command_name} 的 source 路径不存在")
bundle = (dsh.get("dsh") or {}).get("bundle") or {}
patch_path = bundle.get("patch")
if not patch_path or not (root / patch_path).is_file():
    problems.append("DSH bundle 的 patch 路径不存在")
if not (root / str(dsh.get("main", ""))).is_file():
    problems.append("DSH bundle 的 main 入口不存在")
if not dsh.get("engines", {}).get("dsh"):
    problems.append("DSH bundle 缺少 engines.dsh")
if (dsh.get("publishConfig") or {}).get("access") != "public":
    problems.append("DSH bundle 缺少 npm 公开包 publishConfig")
if not (packages["qwen"] / "constraints/global-user-constraints.md").is_file():
    problems.append("Qwen 包缺少 constraints/global-user-constraints.md")
if (packages["qwen"] / "rules").exists():
    problems.append("Qwen 包不应包含 rules/（Qwen 会按条件规则扫描）")
if not (packages["qoder"] / "rules/global-user-constraints.md").is_file():
    problems.append("Qoder 包缺少 rules/global-user-constraints.md")
for package_name in ("qoder", "qwen"):
    for test_file in (packages[package_name] / "scripts").glob("test_*"):
        problems.append(f"{package_name} 包含开发测试: {test_file.name}")
for required_dir in ("skills", "rules"):
    if not (root / required_dir).is_dir():
        problems.append(f"缺少 {required_dir}/")
expected_links = {
    "qoder": {"skills": "skills", "rules": "rules", "commands": "shared/commands", "scripts": "shared/scripts"},
    "qwen": {"skills": "skills", "constraints": "rules", "commands": "shared/commands", "scripts": "shared/scripts"},
}
for name, links in expected_links.items():
    for link, target in links.items():
        path = packages[name] / link
        if not path.is_symlink():
            problems.append(f"{name} 的 {link} 应为软链")
        elif path.resolve() != (root / target).resolve():
            problems.append(f"{name} 的 {link} 未指向 {target}")
if problems:
    sys.exit("; ".join(problems))
PY
then
  fail "插件清单"
fi

echo "== 插件校验 =="
if command -v qoderclicn >/dev/null 2>&1; then
  staged="$(mktemp -d)"
  trap 'rm -rf "$staged"' EXIT
  bash scripts/materialize.sh qoder "$staged/package" >/dev/null || fail "物化 Qoder 包"
  qoderclicn plugins validate "$staged/package" || fail "插件校验"
else
  skip "未安装 qoderclicn"
fi

if [ "$failures" -ne 0 ]; then
  echo "校验失败: $failures 项（跳过 $skips 项）" >&2
  exit 1
fi
if [ "$skips" -ne 0 ]; then
  echo "全部通过（跳过 $skips 项，见上方提示）"
else
  echo "全部通过"
fi
