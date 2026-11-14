# AI 编码代理 system prompt

本仓库维护用户全局约束、十一个通用规范 skill，以及分别面向 Qoder、Qwen Code 与
DeepSeek Harness（DSH）的三个插件包。`rules/`、`skills/` 与 `shared/` 是唯一真源，
三个包用相对软链引用它们，打包时物化成自包含目录。

维护者：SnowCore8，职责与决策规则见 [GOVERNANCE.md](GOVERNANCE.md)。
项目维护约定见 [CONTRIBUTING.md](CONTRIBUTING.md)（根 `AGENTS.md` 是它的软链入口）。

## 目录

| 路径 | 作用 |
|---|---|
| `rules/global-user-constraints.md` | 用户全局约束正文（唯一权威来源） |
| `skills/` | 十一个 skill 的真源 |
| `shared/commands/` | 手动审查命令 |
| `shared/scripts/` | 约束注入、时间注入脚本及其测试 |
| `plugins/qoder/` | Qoder 插件包（`.qoder-plugin/plugin.json`） |
| `plugins/qwen/` | Qwen Code 扩展包（`qwen-extension.json`） |
| `plugins/dsh/` | DSH bundle（`package.json` + `dsh.bundle.patch`） |
| `plugins/marketplace.json` | Qoder 本地市场描述，指向 `plugins/qoder` |
| `.qwen/rules`、`.qwen/skills/` | Qwen Code 项目级入口，软链到顶层真源 |
| `.qoder/rules`、`.qoder/skills/` | Qoder 项目级入口，软链到顶层真源 |
| `.dsh/skills/` | DSH 项目级 skill 入口，软链到顶层真源 |
| `AGENTS.md` | 项目维护约定入口，软链指向 `CONTRIBUTING.md` |
| `docs/agent-tooling-loading.md` | 三工具 rules/skills/plugins 加载规则调研 |
| `docs/time-awareness.md` | Qoder/Qwen 时间注入设计 |
| `docs/release.md` | 版本规则、tag 发布流程与回滚 |
| `scripts/` | `check.sh` 全量校验、`dist.sh` 出包、`materialize.sh` 物化 |
| `GLOSSARY.md` | 术语与写法约定 |
| `CHANGELOG.md` | 按版本记录的可观察变更 |
| `GOVERNANCE.md` | 维护者、决策、审查与发布规则 |
| `THIRD-PARTY-NOTICES.md` | 开发依赖与第三方许可声明 |
| `LICENSE`、`LICENSE-CC-BY-4.0.txt`、`LICENSE-MIT.txt` | 双许可证：文档 CC BY 4.0，代码 MIT |
| `SECURITY.md` | 支持的版本与私下漏洞报告渠道 |
| `.github/` | CI 与 Release 工作流、Dependabot、CODEOWNERS 与 PR 模板 |

## 编辑

1. 改约束：编辑 `rules/global-user-constraints.md`（唯一权威来源）。
2. 改 skill：编辑 `skills/` 下对应的 skill；三个包自动引用，不复制第二份。
3. 改命令或注入脚本：编辑 `shared/commands/` 或 `shared/scripts/`。
4. 改某一端的清单或 hook：编辑 `plugins/<包>/` 下对应文件，并同步三包版本。
5. 新增入口时按「软链约定」执行，改完运行 `scripts/check.sh`。

## 软链约定

- 软链只做入口，不承载内容：目标必须在仓库内、用相对路径、指向真实文件或目录，且不指向另一软链。
- 每个入口只指向唯一真源（`rules/`、`skills/` 或 `shared/`），不复制第二份文件。
- 三个包内部的 `skills/`、`rules/`、`commands/`、`scripts/` 都是指向顶层真源的软链；
  Qoder 的 `plugins validate` 会拒绝解析到包外的路径，所以安装或校验前用
  `scripts/materialize.sh` 物化，或直接用 Release 里的 zip。
- `scripts/check.sh` 的「软链」「插件清单」段校验未入库、缺失、绝对路径、目标出仓、指向 `.git`、
  链式软链、目标不存在或未跟踪，以及三个包的软链是否指向正确真源。
- Windows 检出需启用 `core.symlinks`；否则软链会落成普通文本文件。

## 三个包

| 包 | 清单 | hook 形式 | 安装 |
|---|---|---|---|
| `plugins/qoder` | `.qoder-plugin/plugin.json` | `command` + `args`，`${QODER_PLUGIN_ROOT}` | `qoderclicn plugins install <zip> --scope user` |
| `plugins/qwen` | `qwen-extension.json` | 单条 `command` 字符串，`${CLAUDE_PLUGIN_ROOT}` | `qwen extensions install <zip>` |
| `plugins/dsh` | `package.json` 的 `dsh.bundle.patch` | 无 hook；注册 skill 提供者 | `dsh plugin --profile <名> add <目录>` |

三包共用版本号，发布时一起出包；清单版本不一致会被 `scripts/check.sh`、`scripts/dist.sh`
与 release 工作流拒绝。

## DeepSeek Harness 适配

- 项目级：`.dsh/skills/` 是 rank 100 的 skill 扫描根，软链到顶层 `skills/`；根 `AGENTS.md`
  由 `dsh-agent-instructions` 作为指令链加载。
- bundle：`plugins/dsh` 注册 `ctx.skills.registerProvider`，把包内十一个 skill 提供给任意 profile；
  安装方法与版本准入见 [plugins/dsh/README.md](plugins/dsh/README.md)。
- 约束：DSH 的用户级指令链读取 `~/.dsh/AGENTS.md`，把 `rules/global-user-constraints.md`
  复制到该位置即可；时间由 DSH 自身注入，不需要额外 hook。

## Qwen Code 适配

- 项目级：`.qwen/rules/` 软链到 `rules/`（无 `paths:`，baseline，首请求生效）；`.qwen/skills/`
  软链到十一个 skill；`.qwen/AGENTS.md` 不被 Qwen 读取，仓库不提供。
- 扩展：`plugins/qwen` 的 `qwen-extension.json` 指向 `hooks/qwen-hooks.json`，安装后
  `SessionStart` 注入约束全文与时间，`UserPromptSubmit` 刷新时间；已有同内容规则或
  `AGENTS.md` 时跳过。
- 时间：Qwen 没有内建时间感知，注入格式与设计见 [docs/time-awareness.md](docs/time-awareness.md)。

## Qoder 适配

- 项目级：`.qoder/rules` 软链到 `rules/`，Qoder 从当前目录向上查到 `.git` 逐层读取；
  `.qoder/skills/` 软链到十一个 skill。
- 插件：`plugins/qoder` 安装后 `SessionStart` 注入约束全文与时间，`UserPromptSubmit` 刷新时间；
  去重路径覆盖 `~/.qoder-cn/rules/`（国际版 `~/.qoder/rules/`）、`AGENTS.md`、`.qoder/rules/`。
- 项目级不提供 `.qoder-cn` 与 `.qoder/plugins`：它们在项目级没有加载语义。

## 验证

```bash
python3 -m pip install -r requirements-dev.txt   # 建议用虚拟环境
scripts/check.sh
```

`scripts/check.sh` 覆盖 Markdown、skill 与 hook 测试、DSH bundle 的 `node --test`、shellcheck、
ruff、JSON、敏感文件、软链、三工具项目级适配、三包清单一致性与物化后的 Qoder 插件校验。
缺 `shellcheck`、`node` 或 `qoderclicn` 时会打印「跳过」并在结尾计数。

本地安装 smoke test：

```bash
scripts/materialize.sh qoder /tmp/qoder-package
qoderclicn --cwd /tmp plugins install --scope local /tmp/qoder-package
qoderclicn --cwd /tmp plugins list --json
```

## 打包

版本采用 SemVer，三个清单的 `version` 必须一致；发布流程是「改三包版本与 CHANGELOG → 提交 →
打 `v<version>` 注释 tag → 推送」，由 release 工作流分别构建三个 zip，详见 [docs/release.md](docs/release.md)。

本地出包运行 `scripts/dist.sh`：默认要求工作区干净（`--allow-dirty` 放行），浅克隆直接拒绝，
`--require-tag` 要求 HEAD 正好带有 `v<version>` tag。每个包物化后归一 mtime 与权限、按名称排序、
用 `zip -X` 构建，输出可复现 zip 与 SHA256，各保留最近三个制品。zip 与 `*.sha256` 被 `.gitignore`
忽略，不提交。

## CI

- `check`：push 到 `master` 与 pull request 时运行 `scripts/check.sh`，最小 `contents: read` 权限，
  并先确认 runner 自带 `shellcheck`。
- `release`：推送 `v*` tag 时核对三包版本与 tag，构建三个 zip 与 SHA256 并挂到 Release；
  该工作流没有 `qoderclicn`，用 `--no-validate` 换取可重复构建，插件校验在本地发布前完成。
- 依赖更新由 Dependabot 每周检查 pip 与 GitHub Actions。
- 分支保护在私有仓库免费计划下不可用（需 GitHub Pro），升级后按 GOVERNANCE 的保护项启用。

## 安全

漏洞报告首选 GitHub 私下漏洞报告，入口不可用时邮件联系维护者，不接受公开 issue 披露；支持版本、
处理流程、范围与渠道可用性见 [SECURITY.md](SECURITY.md)。仓库不保存任何密钥或个人数据。

## 许可证

双许可证：文档与规范正文（`rules/`、skill 正文、`docs/`、说明类 Markdown）采用
[CC BY 4.0](LICENSE-CC-BY-4.0.txt)，代码、脚本与配置（`scripts/`、`shared/`、`plugins/*/hooks/`、
`.github/`）采用 [MIT](LICENSE-MIT.txt)。范围划分见 [LICENSE](LICENSE)。

## 变更日志

可观察变更按版本记录在 [CHANGELOG.md](CHANGELOG.md)；版本采用 SemVer，发布点为 tag `v<version>`，
对应的 zip 与 SHA256 挂在 GitHub Release。
