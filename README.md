# AI 编码代理 system prompt

本仓库维护用户全局约束与十一个 skill（`system-prompt-authoring`，以及命名、注释、文档、代码风格、接口与数据、测试与质量、版本控制与协作、发布与运维、安全与合规、仓库治理十项通用规范），以及打包它们的用户级 Qoder 插件。约束正文与插件源是唯一真源，不另建副本。
改约束、skill 或插件前先读本文件。维护者：仓库所有者。
插件的使用者文档（规则激活、hook、边界）见插件 [README](plugins/global-user-constraints/README.md)。
DSH 从仓库根 `AGENTS.md` 加载本约束；Qoder 按插件 README 的「规则激活」加载。

## 目录

| 路径 | 作用 |
|---|---|
| `plugins/global-user-constraints/` | 用户级 Qoder 插件包 |
| `plugins/marketplace.json` | 市场描述文件，承载 `category`/`tags` 等市场字段 |
| `rules/global-user-constraints.md` | 用户全局约束正文 |
| `rules/global-user-constraints.zh-CN.md` | 用户全局约束中文译本（英文原文为准） |
| `AGENTS.md` | DSH 工作区指令入口，软链指向 `rules/global-user-constraints.md` |
| `.qoder/` | 统一入口；`rules`、`plugins` 软链指向根级同名目录 |
| `.qwen` / `.qoder-cn` | 指向 `.qoder` 的软链 |
| `scripts/` | `dist.sh` 打包；`check.sh` 全量校验 |
| `GLOSSARY.md` | 术语与写法约定 |

## 编辑

1. 改约束：编辑 `rules/global-user-constraints.md`；中文译本 `rules/global-user-constraints.zh-CN.md` 同步更新。
2. 改 skill：编辑 `plugins/global-user-constraints/skills/` 下对应的 skill。
3. 只改软链目标，不另建副本。

## 验证

```bash
python3 -m pip install -r requirements-dev.txt
scripts/check.sh
```

`scripts/check.sh` 校验全部未忽略的 Markdown，并运行 skill 与 hook 测试、shellcheck 与 JSON 解析；`qoderclicn` 存在时再跑插件校验。

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
