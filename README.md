# AI 编码代理 system prompt

本仓库维护用户全局约束与十一个 skill（`system-prompt-authoring`，以及命名、注释、文档、代码风格、接口与数据、测试与质量、版本控制与协作、发布与运维、安全与合规、仓库治理十项通用规范），以及打包它们的用户级 Qoder 插件。约束正文与插件源是唯一真源，不另建副本；规范正文只有中文一份。
改约束、skill 或插件前先读本文件。维护者：SnowCore8，职责与决策规则见 [GOVERNANCE.md](GOVERNANCE.md)。
插件的使用者文档（规则激活、hook、边界）见插件 [README](plugins/global-user-constraints/README.md)。
DSH 从仓库根 `AGENTS.md` 加载本仓库维护约定；Qwen Code 从 `.qwen/rules/`（软链到 `rules/`）加载约束正文；Qoder 项目级从 `.qoder/rules/` 读取规则，用户级按插件 README 的「规则激活」安装。DSH 另从 `.dsh/skills/` 发现 skill。

## 目录

| 路径 | 作用 |
|---|---|
| `plugins/global-user-constraints/` | 用户级 Qoder 插件包 |
| `plugins/marketplace.json` | 市场描述文件，承载 `category`/`tags` 等市场字段 |
| `rules/global-user-constraints.md` | 用户全局约束正文（唯一权威来源） |
| `AGENTS.md` | 项目维护约定入口，软链指向 `CONTRIBUTING.md` |
| `CONTRIBUTING.md` | 本仓库项目维护约定 |
| `.qwen/rules` | Qwen Code 项目级规则目录，软链指向根级 `rules/`；规则无 `paths:`，首请求生效 |
| `.qwen/skills/` | Qwen Code 项目级 skill 入口，软链到插件内十一个 skill |
| `.qoder/` | Qoder 项目级配置目录；`rules` 软链指向根级 `rules/` |
| `.qoder/skills/` | Qoder 项目级 skill 入口，软链到插件内十一个 skill |
| `.dsh/skills/` | DSH 项目级 skill 入口，软链到插件内十一个 skill |
| `docs/agent-tooling-loading.md` | 三工具 rules/skills/plugins 加载规则调研 |
| `docs/release.md` | 版本规则、tag 发布流程与回滚 |
| `scripts/` | `dist.sh` 打包；`check.sh` 全量校验 |
| `GLOSSARY.md` | 术语与写法约定 |
| `CHANGELOG.md` | 按日期记录的可观察变更 |
| `GOVERNANCE.md` | 维护者、决策、审查与发布规则 |
| `THIRD-PARTY-NOTICES.md` | 开发依赖与第三方许可声明 |
| `LICENSE`、`LICENSE-CC-BY-4.0.txt`、`LICENSE-MIT.txt` | 双许可证：文档 CC BY 4.0，代码 MIT |
| `SECURITY.md` | 支持的版本与私下漏洞报告渠道 |
| `.github/` | CI 与 Release 工作流、Dependabot、CODEOWNERS 与 PR 模板 |

## 编辑

1. 改约束：编辑 `rules/global-user-constraints.md`（唯一权威来源）。
2. 改 skill：编辑 `plugins/global-user-constraints/skills/` 下对应的 skill。
3. 只改软链目标，不另建副本。
4. 根 `AGENTS.md` 是项目维护约定入口（软链 `CONTRIBUTING.md`）；Qwen 的约束入口是 `.qwen/rules/`（软链 `rules/`）。

## 软链约定

- 软链只做入口，不承载内容：目标必须在仓库内，用相对路径书写，指向真实文件或目录，且不指向另一软链。
- 每个入口只指向唯一真源（`rules/`、`plugins/` 或插件内 skill 目录），不复制第二份文件。
- 新增或调整入口前先确认目标路径稳定；`scripts/check.sh` 的「软链」段校验未入库、缺失、绝对路径、目标出仓、指向 `.git`、链式软链、目标不存在或未跟踪等情况。
- Windows 检出需启用 `core.symlinks`；否则软链会落成普通文本文件。

## DeepSeek Harness 适配

- 指令：DSH 的 `dsh-agent-instructions` 自动加载根 `AGENTS.md`，内容是本仓库维护约定（软链 `CONTRIBUTING.md`）。
- skill：DSH 的 `dsh-skill-filesystem` 扫描项目根 `.dsh/skills`；该目录用相对软链指向插件内十一个 skill，不复制第二份源。文件变更由 watcher 自动生效，无需重启。
- 校验：`scripts/check.sh` 的「DSH 适配」段校验软链可解析、`SKILL.md` 存在且 frontmatter `name` 与目录名一致。

## Qwen Code 适配

- 入口：Qwen Code 的项目级规则目录是 `.qwen/rules/`，用相对软链指向根级 `rules/`；其中的
  `global-user-constraints.md` 没有 `paths:`，属 baseline，首个请求即进入 system prompt。
- skill：Qwen Code 从 `.qwen/skills/` 发现项目级 skill，只扫一层；该目录用相对软链指向插件内十一个 skill。
- 不提供 `.qwen/AGENTS.md`：Qwen 只在每级目录查找 `QWEN.md`/`AGENTS.md` 文件名，不进入 `.qwen/` 子目录再找，
  项目级 `.qwen/AGENTS.md` 不会被读取。
- 校验：`scripts/check.sh` 的「Qwen 适配」段校验 `.qwen`、`.qwen/rules`、`.qwen/skills` 的形态与软链目标，
  `.qwen/AGENTS.md` 不存在，且约束正文 front matter 不含 `paths:`。

## Qoder 适配

- 项目级：`.qoder/rules` 软链指向根级 `rules/`；Qoder 从当前目录向上查到 `.git`，逐层读取 `.qoder/rules/**/*.md`。
- skill：Qoder 从 `.qoder/skills/` 发现项目级 skill；该目录用相对软链指向插件内十一个 skill，
  安装插件时另提供带插件前缀的同一批 skill。
- 用户级：CN 把规则复制到 `~/.qoder-cn/rules/`；插件包内的 `rules/` 当前不被宿主加载，安装后按插件 README 的
  「规则激活」复制一次。
- 不提供两个入口：`.qoder-cn`（CN 的这个名字只用于用户级配置根）与 `.qoder/plugins`（插件包体安装在用户配置根），
  项目级都没有加载语义。
- 校验：`scripts/check.sh` 的「Qoder 适配」段校验 `.qoder` 为普通目录、`.qoder/rules` 指向 `rules/`、
  `.qoder/skills` 的十一条软链，且 `.qoder-cn` 与 `.qoder/plugins` 不存在。

## 验证

```bash
python3 -m pip install -r requirements-dev.txt
scripts/check.sh
```

`scripts/check.sh` 校验全部未忽略的 Markdown，并运行 skill 与 hook 测试、shellcheck、JSON 解析、
敏感文件回归与 DSH/Qwen/Qoder 适配校验；`qoderclicn` 存在时再跑插件校验。

Markdown 校验只覆盖格式；各 skill 的内容规则按各自 `SKILL.md` 的人工核对清单检查，`MD-*` 规则只覆盖 `check.py` 的格式项。
插件校验用 `qoderclicn` 而非入口脚本 `qodercn`：后者把首参当路径判断，仓库根有 `plugins/` 目录，会被当成 IDE 目标。

本地安装 smoke test 用临时目录，避免污染当前项目；在仓库根目录运行：

```bash
TMP="$(mktemp -d)"
qoderclicn --cwd "$TMP" plugins install --scope local "$PWD/plugins/global-user-constraints"
qoderclicn --cwd "$TMP" plugins list --json
```

## 打包

版本采用 SemVer，`plugins/global-user-constraints/.qoder-plugin/plugin.json` 的 `version` 是唯一来源；
发布流程是「改版本与 CHANGELOG → 提交 → 打 `v<version>` 注释 tag → 推送」，由 release 工作流出包，
详见 [docs/release.md](docs/release.md)。

本地出包运行 `scripts/dist.sh`：默认要求工作区干净（`--allow-dirty` 放行，文件名加 `-dirty`），
浅克隆直接拒绝，`--require-tag` 要求 HEAD 正好带有 `v<version>` tag。包内复制双许可证，归一 mtime
并按名称排序后输出可复现 zip 与 SHA256，保留最近三个制品。zip 制品与 `*.sha256` 被 `.gitignore` 忽略，
不提交。

## CI

- `check`：push 到 `master` 与 pull request 时运行 `scripts/check.sh`，使用最小 `contents: read` 权限，
  并先确认 runner 自带 `shellcheck` 可用。
- `release`：推送 `v*` tag 时重跑校验、核对 tag 与 manifest 版本，构建 zip 与 SHA256 并挂到 Release；
  该工作流没有 `qoderclicn`，用 `--no-validate` 换取可重复构建，插件校验在本地发布前完成。
- 依赖更新由 Dependabot 每周检查 pip 与 GitHub Actions。
- CI 与本地跑的是同一套校验，差异只在 `qoderclicn` 缺失时跳过插件校验；分支保护与 `.github/CODEOWNERS`
  在接入 GitHub 远端后启用，保护项见 [GOVERNANCE.md](GOVERNANCE.md)。

## 安全

漏洞报告走 GitHub 私下漏洞报告，不接受公开 issue 披露；支持版本、处理流程与范围见
[SECURITY.md](SECURITY.md)。仓库不保存任何密钥或个人数据，`~/.qwen/settings.json` 等本机配置不在版本库内。

## 许可证

双许可证：文档与规范正文（`rules/`、skill 正文、`docs/`、说明类 Markdown）采用
[CC BY 4.0](LICENSE-CC-BY-4.0.txt)，代码、脚本与配置（`scripts/`、`hooks/`、`.github/`）采用
[MIT](LICENSE-MIT.txt)。范围划分见 [LICENSE](LICENSE)。

## 变更日志

可观察变更按日期记录在 [CHANGELOG.md](CHANGELOG.md)，版本号由插件提交数推导，不构成发布边界。
