# AI 编码代理 system prompt

本仓库维护用户全局约束与十一个 skill（`system-prompt-authoring`，以及命名、注释、文档、代码风格、接口与数据、测试与质量、版本控制与协作、发布与运维、安全与合规、仓库治理十项通用规范），以及打包它们的用户级 Qoder 插件。约束正文与插件源是唯一真源，不另建副本；规范正文只有中文一份。
改约束、skill 或插件前先读本文件。维护者：仓库所有者。
插件的使用者文档（规则激活、hook、边界）见插件 [README](plugins/global-user-constraints/README.md)。
DSH 从仓库根 `AGENTS.md` 加载本仓库维护约定；Qwen Code 从 `.qwen/AGENTS.md` 加载约束正文；Qoder 按插件 README 的「规则激活」加载。DSH 另从 `.dsh/skills/` 发现 skill。

## 目录

| 路径 | 作用 |
|---|---|
| `plugins/global-user-constraints/` | 用户级 Qoder 插件包 |
| `plugins/marketplace.json` | 市场描述文件，承载 `category`/`tags` 等市场字段 |
| `rules/global-user-constraints.md` | 用户全局约束正文（唯一规范源） |
| `AGENTS.md` | 项目维护约定入口，软链指向 `CONTRIBUTING.md` |
| `CONTRIBUTING.md` | 本仓库项目维护约定 |
| `.qwen/AGENTS.md` | Qwen Code 约束正文入口，软链指向 `rules/global-user-constraints.md` |
| `.dsh/skills/` | DSH 项目级 skill 入口，软链到插件内十一个 skill |
| `.qoder/` | 统一入口；`rules`、`plugins` 软链指向根级同名目录 |
| `.qoder-cn` | 指向 `.qoder` 的软链 |
| `scripts/` | `dist.sh` 打包；`check.sh` 全量校验 |
| `GLOSSARY.md` | 术语与写法约定 |

## 编辑

1. 改约束：编辑 `rules/global-user-constraints.md`（唯一规范源）。
2. 改 skill：编辑 `plugins/global-user-constraints/skills/` 下对应的 skill。
3. 只改软链目标，不另建副本。
4. 根 `AGENTS.md` 是项目维护约定入口（软链 `CONTRIBUTING.md`）；Qwen 的约束入口是 `.qwen/AGENTS.md`。

## 软链约定

- 软链只做入口，不承载内容：目标必须在仓库内，用相对路径书写，指向真实文件或目录，且不指向另一软链。
- 每个入口只指向唯一真源（`rules/`、`plugins/` 或插件内 skill 目录），不复制第二份文件。
- 新增或调整入口前先确认目标路径稳定；`scripts/check.sh` 的「软链」段校验未入库、缺失、绝对路径、目标出仓、指向 `.git`、链式软链、目标不存在或未跟踪等情况。
- Windows 检出需启用 `core.symlinks`；否则软链会落成普通文本文件。

## DeepSeek Harness 适配

- 指令：DSH 的 `dsh-agent-instructions` 自动加载根 `AGENTS.md`，内容是本仓库维护约定（软链 `CONTRIBUTING.md`）。
- skill：DSH 的 `dsh-skill-filesystem` 扫描项目根 `.dsh/skills`；该目录用相对软链指向插件内十一个 skill，不复制第二份源。文件变更由 watcher 自动生效，无需重启。
- 校验：`scripts/check.sh` 的「DSH 适配」段检查软链可解析、`SKILL.md` 存在且 frontmatter `name` 与目录名一致。

## Qwen Code 适配

- 入口：Qwen Code 只读 `.qwen/AGENTS.md`；该文件用相对软链指向 `rules/global-user-constraints.md`。
- 不提供 `.qwen/rules`：Qwen 不支持规则目录；`.qwen` 是普通目录，只放该软链。
- 校验：`scripts/check.sh` 的「Qwen 适配」段检查 `.qwen` 为普通目录、`.qwen/AGENTS.md` 指向约束正文。

## 验证

```bash
python3 -m pip install -r requirements-dev.txt
scripts/check.sh
```

`scripts/check.sh` 校验全部未忽略的 Markdown，并运行 skill 与 hook 测试、shellcheck、JSON 解析与 DSH 适配检查；`qoderclicn` 存在时再跑插件校验。

Markdown 校验只覆盖格式；各 skill 的内容规则按各自 `SKILL.md` 的人工核对清单检查，`MD-*` 规则只覆盖 `check.py` 的格式项。
插件校验用 `qoderclicn` 而非入口脚本 `qodercn`：后者把首参当路径判断，仓库根有 `plugins/` 目录，会被当成 IDE 目标。

本地安装 smoke test 用临时目录，避免污染当前项目；在仓库根目录运行：

```bash
TMP="$(mktemp -d)"
qoderclicn --cwd "$TMP" plugins install --scope local "$PWD/plugins/global-user-constraints"
qoderclicn --cwd "$TMP" plugins list --json
```

## 打包

在仓库根目录运行 `scripts/dist.sh`，版本推导、软链解引用、排除项、结构校验与旧包清理见脚本 `--help`；脚本写回的 `.qoder-plugin/plugin.json` 版本随代码提交，zip 产物被 `.gitignore` 忽略。
