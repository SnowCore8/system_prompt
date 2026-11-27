#!/usr/bin/env bash
# 全量校验：Markdown、skill 与 hook 测试、shellcheck、ruff、JSON、敏感文件、零软链与组装、三包清单与校验。
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
command -v node >/dev/null 2>&1 || {
  echo "未找到 node" >&2
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

echo "== 常驻约束体积 =="
constraints_file="rules/global-user-constraints.md"
constraints_limit=40960
if [ ! -f "$constraints_file" ]; then
  fail "缺少常驻约束正文: $constraints_file"
else
  constraints_bytes="$(wc -c < "$constraints_file" | tr -d '[:space:]')"
  if [ -z "$constraints_bytes" ]; then
    fail "无法统计常驻约束正文大小: $constraints_file"
  elif [ "$constraints_bytes" -gt "$constraints_limit" ]; then
    fail "$constraints_file: ${constraints_bytes} 字节，超过 40 KiB 硬上限，按主题提取到对应 skill 的 references"
  else
    echo "$constraints_file: ${constraints_bytes} 字节"
  fi
fi

echo "== Markdown 格式 =="
while IFS= read -r -d '' file; do
  if ! output="$(python3 "$SKILL_DIR/scripts/check.py" --strict "$file" 2>&1)"; then
    printf '%s\n' "$output"
    fail "$file"
  fi
done < <(git ls-files --cached --others --exclude-standard -z '*.md')

echo "== skill 测试 =="
python3 -B -m unittest discover -s tests/skill -p 'test_*.py' || fail "skill 测试"

echo "== hook 测试（JavaScript） =="
node --test tests/hooks/*.test.js || fail "hook 测试"

echo "== DSH 包测试 =="
node --test tests/dsh/provider.test.mjs || fail "DSH 包测试"

echo "== shellcheck =="
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/dist.sh scripts/check.sh scripts/assemble.sh scripts/materialize.sh || fail "shellcheck"
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
printf '[run]\nbranch = true\nparallel = true\nsource = %s/skills/system-prompt-authoring/scripts\ndata_file = %s/.coverage\ndisable_warnings = no-data-collected\n' \
  "$REPO_ROOT" "$REPO_ROOT" > "$cov_cfg"
COVERAGE_PROCESS_START="$cov_cfg" python3 -B -m coverage run --rcfile="$cov_cfg" -m unittest discover -s tests/skill -p 'test_*.py' || fail "覆盖率 skill 测试"
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
tracked_links="$(git ls-files -s | awk '$1=="120000"{print $4}')"
if [ -n "$tracked_links" ]; then
  printf '%s\n' "$tracked_links" >&2
  fail "版本库仍跟踪软链；入口应由 scripts/assemble.sh 与 scripts/materialize.sh 组装"
fi

echo "== 组装 =="
bash scripts/assemble.sh --check || fail "开发组装校验"
[ -f rules/global-user-constraints.md ] || fail "缺少约束正文 rules/global-user-constraints.md"
[ -s AGENTS.md ] || fail "缺少智能体项目指令 AGENTS.md"
if [ -L AGENTS.md ]; then
  fail "AGENTS.md 应为真实文件，不得软链"
fi
[ -f CONTRIBUTING.md ] || fail "缺少人类贡献约定 CONTRIBUTING.md"
echo "== 插件清单 =="
staged="$(mktemp -d)"
trap 'rm -rf "$staged"' EXIT
if ! bash scripts/materialize.sh qoder "$staged/qoder" >/dev/null; then
  fail "组装 Qoder 包"
fi
if ! bash scripts/materialize.sh qwen "$staged/qwen" >/dev/null; then
  fail "组装 Qwen 包"
fi
if ! python3 - "$REPO_ROOT" "$staged/qoder" "$staged/qwen" <<'PY'
import json, re, sys
from pathlib import Path

root = Path(sys.argv[1])
qdir = Path(sys.argv[2])
wdir = Path(sys.argv[3])
problems = []
qoder = json.loads((qdir / ".qoder-plugin/plugin.json").read_text(encoding="utf-8"))
qwen = json.loads((wdir / "qwen-extension.json").read_text(encoding="utf-8"))
dsh = json.loads((root / "package.json").read_text(encoding="utf-8"))
versions = {"qoder": qoder.get("version"), "qwen": qwen.get("version"), "dsh": dsh.get("version")}
for name, version in versions.items():
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version or "")):
        problems.append(f"{name} manifest 版本不是 SemVer")
if len(set(versions.values())) != 1:
    problems.append(f"三包版本不一致: {versions}")
for label, pkg in (("Qoder", qdir), ("Qwen", wdir)):
    for path in pkg.rglob("*"):
        if path.is_symlink():
            problems.append(f"{label} 包包含软链: {path.relative_to(pkg)}")
if not (qdir / str(qoder.get("hooks", ""))).is_file():
    problems.append("Qoder 插件的 hooks 路径不存在")
if not (qdir / str(qoder.get("skills", ""))).is_dir():
    problems.append("Qoder 插件的 skills 路径不存在")
if not (qdir / "rules" / "global-user-constraints.md").is_file():
    problems.append("Qoder 包缺少 rules/global-user-constraints.md")


def hook_commands(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("command", "args"):
                items = value if isinstance(value, list) else [value]
                for item in items:
                    if isinstance(item, str):
                        yield item
            else:
                yield from hook_commands(value)
    elif isinstance(node, list):
        for item in node:
            yield from hook_commands(item)


hooks_path = qdir / str(qoder.get("hooks", ""))
if hooks_path.is_file():
    try:
        hooks_data = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        hooks_data = None
    refs = {
        ref
        for command in hook_commands(hooks_data)
        for ref in re.findall(r'\$\{QODER_PLUGIN_ROOT\}/([^"\s]+)', command)
    }
    for ref in sorted(refs):
        if ".." in ref.split("/") or not (qdir / ref).is_file():
            problems.append(f"Qoder 钩子引用的文件不存在: {ref}")
for command_name, command in (qoder.get("commands") or {}).items():
    source = command.get("source") if isinstance(command, dict) else None
    if not source or not (qdir / str(source)).is_file():
        problems.append(f"Qoder 命令 {command_name} 的 source 路径不存在")
if not (qdir / "scripts").is_dir():
    problems.append("Qoder 包缺少 scripts/")
if list((qdir / "scripts").glob("test_*")):
    problems.append("Qoder 包包含开发测试")
if not (wdir / str(qwen.get("hooks", ""))).is_file():
    problems.append("Qwen 扩展的 hooks 路径不存在")
for key in ("skills", "commands"):
    if not (wdir / str(qwen.get(key, ""))).is_dir():
        problems.append(f"Qwen 扩展的 {key} 路径不存在")
if not (wdir / "constraints/global-user-constraints.md").is_file():
    problems.append("Qwen 包缺少 constraints/global-user-constraints.md")
if (wdir / "rules").exists():
    problems.append("Qwen 包不应包含 rules/")
if not (wdir / "scripts").is_dir():
    problems.append("Qwen 包缺少 scripts/")
if list((wdir / "scripts").glob("test_*")):
    problems.append("Qwen 包包含开发测试")
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
if problems:
    sys.exit("; ".join(problems))
PY
then
  fail "插件清单"
fi
echo "== 插件校验 =="
if command -v qoderclicn >/dev/null 2>&1; then
  qoderclicn plugins validate "$staged/qoder" || fail "插件校验"
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
