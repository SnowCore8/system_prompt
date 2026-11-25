# AI 编码代理 system prompt

本仓库维护用户全局约束、十八个通用规范 skill，以及分别面向 Qoder、Qwen Code 与
DeepSeek Harness（DSH）的三个插件包。`rules/`、`skills/` 与 `shared/` 是唯一真源。
Qoder/Qwen 包只放清单与 hook；三包都由 `scripts/materialize.sh` 从顶层真源组装成自包含目录，
不依赖、也不提交软链。

维护者：SnowCore8，职责与决策规则见 [GOVERNANCE.md](GOVERNANCE.md)。
代理项目指令见 [AGENTS.md](AGENTS.md)；人类贡献、校验与发布约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 目录

| 路径 | 作用 |
|---|---|
| `rules/global-user-constraints.md` | 用户全局约束正文（唯一权威来源） |
| `skills/` | 十八个 skill 的真源 |
| `shared/commands/` | 手动审查命令 |
| `shared/scripts/` | 约束注入、时间注入脚本 |
| `tests/` | 开发测试：skill、hook 与 DSH provider |
| `plugins/qoder/` | Qoder 插件包（`.qoder-plugin/plugin.json`） |
| `plugins/qwen/` | Qwen Code 扩展包（`qwen-extension.json`） |
| `package.json`（仓库根） | DSH bundle 清单（npm 包与 git 源安装入口） |
| `plugins/dsh/` | DSH bundle 的插件源码、patch 与说明 |
| `plugins/marketplace.json` | Qoder 本地市场描述，指向 `plugins/qoder` |
| `.qwen/rules`、`.qwen/skills/` | Qwen Code 项目级入口，由 `scripts/assemble.sh` 生成（不提交） |
| `.qoder/rules`、`.qoder/skills/` | Qoder 项目级入口，由 `scripts/assemble.sh` 生成（不提交） |
| `.dsh/skills/` | DSH 项目级 skill 入口，由 `scripts/assemble.sh` 生成（不提交） |
| `AGENTS.md` | 代理项目指令（真实文件，进入模型上下文） |
| `CONTRIBUTING.md` | 人类贡献、校验与发布约定（不进入模型上下文） |
| `docs/agent-tooling-loading.md` | 三工具 rules/skills/plugins 加载规则调研 |
| `docs/time-awareness.md` | Qoder/Qwen 时间注入设计 |
| `docs/markdown-check-rules.md` | Markdown 校验脚本的规则表与输出级别 |
| `docs/release.md` | 版本规则、tag 发布流程与回滚 |
| `docs/prompt-inventory.md` | 提示词与纯规则分类台账及迁移批次 |
| `scripts/` | `assemble.sh` 生成开发入口、`materialize.sh` 组装包、`check.sh` 校验、`dist.sh` 出包 |
| `GLOSSARY.md` | 术语与写法约定 |
| `CHANGELOG.md` | 按版本记录的可观察变更 |
| `GOVERNANCE.md` | 维护者、决策、审查与发布规则 |
| `THIRD-PARTY-NOTICES.md` | 开发依赖与第三方许可声明 |
| `LICENSE`、`LICENSE-CC-BY-4.0.txt`、`LICENSE-MIT.txt` | 双许可证：文档 CC BY 4.0，代码 MIT |
| `SECURITY.md` | 支持的版本与私下漏洞报告渠道 |
| `.github/` | CI 与 Release 工作流、Dependabot、CODEOWNERS 与 PR 模板 |

## 编辑

1. 改约束：编辑 `rules/global-user-constraints.md`（唯一权威来源）；正文以 UTF-8 字节计硬上限 32 KiB，超限时按主题把规则提取到对应 skill 的 `references/`，正文只保留摘要与加载指引。
2. 改 skill：编辑 `skills/` 下对应的 skill；三个包自动引用，不复制第二份。
3. 改命令或注入脚本：编辑 `shared/commands/` 或 `shared/scripts/`。
4. 改某一端的清单或 hook：编辑 `plugins/<包>/` 下对应文件，并同步三包版本。
5. 新增或修改入口后按「组装约定」执行，改完运行 `scripts/check.sh`。

## 组装约定

- `skills/`、`rules/`、`shared/` 是唯一真源；不复制第二份。
- `scripts/assemble.sh` 生成 `.dsh/skills`、`.qoder/rules`、`.qoder/skills`、`.qwen/rules`、`.qwen/skills`，
  供本地工具发现；这些目录被 `.gitignore` 忽略，修改真源后重新运行。
- `scripts/materialize.sh` 从顶层真源组装 Qoder/Qwen/DSH 包；`scripts/dist.sh` 只打包组装结果；
  三者都不含软链。Qoder 的 `plugins validate` 针对组装后的目录运行。
- `scripts/check.sh` 校验零跟踪软链、开发组装、组装后的包清单与 Qoder 插件校验；不再要求 Windows `core.symlinks`。

## 三个包

以下三个包的描述只说明用途、安装与行为，不构成规范；规范以 `rules/` 与 `skills/` 为准。

| 包 | 清单 | hook 形式 | 安装 |
|---|---|---|---|
| `plugins/qoder` | `.qoder-plugin/plugin.json` | `command` + `args`，`${QODER_PLUGIN_ROOT}` | `qoderclicn plugins install <zip> --scope user` |
| `plugins/qwen` | `qwen-extension.json` | 单条 `command` 字符串，`${CLAUDE_PLUGIN_ROOT}` | `qwen extensions install <zip>` |
| `plugins/dsh` | 仓库根 `package.json` 的 `dsh.bundle.patch` | 无 hook；注册 skill 提供者 | `pnpm dsh plugin --profile <名> add @snowcore8/dsh-global-user-constraints@<版本>` |

三包共用版本号，发布时一起出包；清单版本不一致会被 `scripts/check.sh`、`scripts/dist.sh`
与 release 工作流拒绝。

## DeepSeek Harness 适配

- 项目级：`.dsh/skills/` 是 rank 100 的 skill 扫描根，由 `scripts/assemble.sh` 从顶层 `skills/` 生成；
  根 `AGENTS.md` 由 `dsh-agent-instructions` 作为指令链加载。
- bundle：仓库根 `package.json` 声明 `dsh.bundle.patch`，`plugins/dsh/src/index.js` 注册
  `ctx.skills.registerProvider` 提供十八个 skill，并注册 `ctx.systemPrompt.section()` 注入约束全文。
- 安装：发布流水线把根包发到 npm 公共 registry，直接
  `pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@<版本>`，
  插件页能检测到更新。GitHub Packages 上的旧包已删除，0.8.0 起只发 npm。也可以从 GitHub 源安装（tag 方式不会检测更新）：
  `pnpm dsh plugin --profile web add "github:SnowCore8/system_prompt#v<版本>"`。
  细节见 [plugins/dsh/README.md](plugins/dsh/README.md)。
- 约束：装完即自动注入，无需手动复制；若 `~/.dsh/AGENTS.md` 已加载同内容则按 sha256 去重跳过。
  时间由 DSH 自身注入，不需要额外 hook。
- 命令：DSH 不注册 `constraints-check`；该命令仅由 Qoder/Qwen 包提供，DSH 中直接按规则与 skill 审查。

## Qwen Code 适配

- 项目级：`.qwen/rules/` 由 `scripts/assemble.sh` 从 `rules/` 生成（无 `paths:`，baseline，首请求生效）；
  `.qwen/skills/` 从十八个 skill 生成；`.qwen/AGENTS.md` 不被 Qwen 读取，仓库不提供。
- 扩展：`plugins/qwen` 的 `qwen-extension.json` 指向 `hooks/qwen-hooks.json`，安装后
  `SessionStart` 注入约束全文与时间，`UserPromptSubmit` 刷新时间；已有同内容规则或
  `AGENTS.md` 时跳过。
- 时间：Qwen 没有内建时间感知，注入格式与设计见 [docs/time-awareness.md](docs/time-awareness.md)。

## Qoder 适配

- 项目级：`.qoder/rules` 由 `scripts/assemble.sh` 从 `rules/` 生成，Qoder 从当前目录向上查到 `.git` 逐层读取；
  `.qoder/skills/` 从十八个 skill 生成。
- 插件：`plugins/qoder` 安装后 `SessionStart` 注入约束全文与时间，`UserPromptSubmit` 刷新时间；
  去重路径覆盖 `~/.qoder-cn/rules/`（国际版 `~/.qoder/rules/`）、`AGENTS.md`、`.qoder/rules/`。
- 项目级不提供 `.qoder-cn` 与 `.qoder/plugins`：它们在项目级没有加载语义。

## 验证

```bash
python3 -m pip install -r requirements-dev.txt   # 建议用虚拟环境
scripts/check.sh
```

`scripts/check.sh` 覆盖常驻约束体积（≤32 KiB）、Markdown、skill 与 hook 测试、DSH bundle 的 `node --test`、
shellcheck、ruff、依赖审计（pip-audit）、覆盖率（`--fail-under=90`）、JSON、敏感文件、零跟踪软链、开发
组装、三包清单一致性与组装后的 Qoder 插件校验。缺 `shellcheck`、`node` 或 `qoderclicn` 时会打印「跳过」并在
结尾计数。

本地安装 smoke test：

```bash
scripts/materialize.sh qoder /tmp/qoder-package
qoderclicn --cwd /tmp plugins install --scope local /tmp/qoder-package
qoderclicn --cwd /tmp plugins list --json
```

## 打包

版本、tag 与发布步骤以 [docs/release.md](docs/release.md) 为唯一 runbook。本地出包运行
`scripts/dist.sh`；它要求干净工作区、可用 `--require-tag` 校验 tag，生成可复现 zip 与 SHA256。
zip 与 `*.sha256` 不纳入版本库。

## CI

- `check`：push 到 `master` 与 pull request 时运行 `scripts/check.sh`，最小 `contents: read` 权限，
  并先确认 runner 自带 `shellcheck`；另跑 gitleaks 历史机密扫描。
- `release`：推送 `v*` tag 时核对三包版本与 tag，构建三个 zip 与 SHA256、生成 SBOM 并挂到 Release；
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
