# AI 编码代理 system prompt

本仓库维护用户全局约束、十八个通用规范 skill，以及面向 Qoder、Qwen Code、DeepSeek Harness（DSH）的三个包。
`rules/`、`skills/`、`shared/` 是唯一真源；开发入口与安装包由组装脚本生成，不复制第二份。

维护者：SnowCore8。职责见 [GOVERNANCE.md](GOVERNANCE.md)，代理指令见 [AGENTS.md](AGENTS.md)，人类贡献与发布约定见
[CONTRIBUTING.md](CONTRIBUTING.md)。

## 快速开始

```bash
python3 -m pip install -r requirements-dev.txt
scripts/assemble.sh dev      # 生成 .dsh/.qoder/.qwen 开发入口（不提交）
scripts/check.sh             # 全量校验
```

`assemble.sh dev` 生成项目级入口；`materialize.sh` 组装自包含包；`dist.sh` 出包；发布流程见
[docs/release.md](docs/release.md)。

## 目录

| 路径 | 作用 |
|---|---|
| `rules/`、`skills/`、`shared/` | 唯一真源：约束、十八个 skill、命令与注入脚本 |
| `plugins/qoder/`、`plugins/qwen/`、`plugins/dsh/` | 三包清单、hooks 与说明 |
| `scripts/` | `assemble.sh` 生成开发入口、`materialize.sh` 组装包、`check.sh` 校验、`dist.sh` 出包 |
| `docs/` | 加载调研、时间设计、校验规则、分类台账与发布手册 |
| `tests/`、`.github/` | 测试与 CI/Release 工作流 |
| `AGENTS.md`、`CONTRIBUTING.md` | 代理项目指令与人类贡献约定（分离，不互相复制） |
| `.dsh/`、`.qoder/`、`.qwen/` | `assemble.sh` 生成的开发入口，被 `.gitignore` 忽略 |
| `package.json`、`plugins/marketplace.json` | DSH bundle 清单与 Qoder 本地市场描述；后者使用前运行 `scripts/assemble.sh qoder` |
| 根文档与许可证 | 治理、安全、术语、变更日志、双许可证与第三方声明 |

## 编辑与组装

- 改约束：编辑 `rules/global-user-constraints.md`（唯一权威来源）；正文 UTF-8 上限 32 KiB，超限时把细节提取到
  对应 skill 的 `references/`。
- 改 skill：编辑 `skills/<name>/`，不复制第二份；改后运行 `scripts/assemble.sh` 刷新开发入口。
- 改命令或注入脚本：编辑 `shared/commands/` 或 `shared/scripts/`。
- 改包清单或 hook：编辑 `plugins/<包>/`，同步三包版本，并运行 `scripts/materialize.sh` 验证组装。
- Qoder 本地市场：先运行 `scripts/assemble.sh qoder` 填充 `plugins/qoder`，再交给 Qoder 的 marketplace；生成目录不提交。
- 提交前运行 `scripts/check.sh`；零跟踪软链、开发组装与组装后的包由该脚本校验。

## 三个包

| 包 | 安装 |
|---|---|
| Qoder | `qoderclicn plugins install global-user-constraints-qoder-VERSION.zip --scope user` |
| Qwen Code | `qwen extensions install global-user-constraints-qwen-VERSION.zip` |
| DSH | `pnpm dsh plugin --profile PROFILE add @snowcore8/dsh-global-user-constraints@VERSION` |

安装与行为细节见 [Qoder](plugins/qoder/README.md)、[Qwen Code](plugins/qwen/README.md) 与 [DSH](plugins/dsh/README.md)。

三包共用 SemVer 版本号，由 `scripts/check.sh`、`scripts/dist.sh` 与 release 工作流校验。各端差异：

- Qoder/Qwen 通过 hooks 注入；DSH 以 skill 提供者与 `systemPrompt.section()` 注入，不注册 `constraints-check` 命令。
- Qwen 不读取 `.qwen/AGENTS.md`；Qoder 项目级不提供 `.qoder-cn` 与 `.qoder/plugins`。
- 时间由 Qoder/Qwen hook 注入；DSH 使用自身时间注入。

## 验证

```bash
scripts/check.sh
```

`check.sh` 覆盖约束体积、Markdown、skill/hook/DSH 测试、shellcheck、ruff、依赖审计、覆盖率、JSON、敏感文件、
零跟踪软链、开发组装、三包清单与组装后的 Qoder 插件校验。缺少 `shellcheck`、`node` 或 `qoderclicn` 时会跳过
对应项并在结尾计数。

Qoder 本地安装冒烟：

```bash
scripts/materialize.sh qoder /tmp/qoder-package
qoderclicn --cwd /tmp plugins install --scope local /tmp/qoder-package
```

## 发布与 CI

- 发布：版本、tag、回滚与检查单见 [docs/release.md](docs/release.md)；`scripts/dist.sh` 生成可复现 zip 与 SHA256。
- CI：`check` 运行 `scripts/check.sh` 并做历史机密扫描；`release` 在推送 `v*` tag 时构建三包、SBOM 与 Release
  附件。

## 安全、许可与变更

- 漏洞报告与支持版本见 [SECURITY.md](SECURITY.md)；仓库不保存密钥或个人数据。
- 文档与规范正文采用 [CC BY 4.0](LICENSE-CC-BY-4.0.txt)，代码与配置采用 [MIT](LICENSE-MIT.txt)；范围见
  [LICENSE](LICENSE)。
- 可观察变更按版本记录在 [CHANGELOG.md](CHANGELOG.md)。
