# AI 编码智能体 system prompt

本仓库维护全局用户约束、二十个通用规范 skill，以及面向 Qoder、Qwen Code、DeepSeek Harness（DSH）的三个包。
`rules/`、`skills/`、`shared/` 是唯一真源；开发入口与安装包由组装脚本生成，不复制第二份。

维护者：SnowCore8。职责见 [GOVERNANCE.md](GOVERNANCE.md)，智能体指令见 [AGENTS.md](AGENTS.md)，人类贡献与发布约定见
[CONTRIBUTING.md](CONTRIBUTING.md)。

## 快速开始

开发与校验需要 `python3`、`node` 与 `git`（CI 使用 Python 3.12 与 Node 20）。

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
| `rules/`、`skills/`、`shared/` | 唯一真源：约束、二十个 skill、命令与注入脚本 |
| `plugins/qoder/`、`plugins/qwen/`、`plugins/dsh/` | 三包清单、hooks 与说明 |
| `npm/qoder/`、`npm/qwen/` | 平台 npm 安装包清单：承载同版本 zip 与校验和 |
| `scripts/` | `assemble.sh` 生成开发入口、`materialize.sh` 组装包、`check.sh` 校验、`dist.sh` 出包 |
| `docs/` | 加载调研、hook 与注入、时间设计、校验规则、分类台账与发布手册 |
| `tests/`、`.github/` | 测试与 CI/Release 工作流 |
| `AGENTS.md`、`CONTRIBUTING.md` | 智能体项目指令与人类贡献约定（分离，不互相复制） |
| `.dsh/`、`.qoder/`、`.qwen/` | `assemble.sh` 生成的开发入口，被 `.gitignore` 忽略 |
| `package.json`、`plugins/marketplace.json` | DSH bundle 清单与 Qoder 本地市场描述；后者使用前运行 `scripts/assemble.sh qoder` |
| 根文档与许可证 | 治理、安全、术语、变更日志、双许可证与第三方声明 |

内容层级、20 个 skill 的主责与边界见 [docs/content-map.md](docs/content-map.md)；三端 hook 事件、注入时序与压缩后行为见
[docs/hooks-and-injection.md](docs/hooks-and-injection.md)。

## 编辑与组装

- 改约束：编辑 `rules/global-user-constraints.md`（唯一权威来源）；正文 UTF-8 上限 40 KiB，超限时把细节提取到
  对应 skill 的 `references/`。
- 改 skill：编辑 `skills/<name>/`，不复制第二份；改后运行 `scripts/assemble.sh` 刷新开发入口。
- 改命令或注入脚本：编辑 `shared/commands/` 或 `shared/scripts/`。
- 改包清单或 hook：编辑 `plugins/<包>/`，同步三包与 `npm/qoder`、`npm/qwen` 版本，并运行 `scripts/materialize.sh` 验证组装。
- Qoder 本地市场：先运行 `scripts/assemble.sh qoder` 填充 `plugins/qoder`，并用
  `qoderclicn plugins validate plugins/qoder` 确认组件齐全，再添加目录 `plugins/`：
  `qoderclicn plugins marketplace add <仓库>/plugins`。不要只添加 `plugins/marketplace.json`，
  其缓存不带同级插件目录，安装会报 ENOENT；生成目录不提交。
- 提交前运行 `scripts/check.sh`；零跟踪软链、开发组装与组装后的包由该脚本校验。

## 三个包

| 包 | 安装 |
|---|---|
| Qoder | `qoderclicn plugins install <npm zip URL> --scope user`；或解压 zip 后按目录安装 |
| Qwen Code | 下载 zip 后 `qwen extensions install global-user-constraints-qwen-VERSION.zip` |
| DSH | `pnpm dsh plugin --profile PROFILE add @snowcore8/dsh-global-user-constraints@VERSION` |

Qoder 的 npm zip 直链（URL 必须以 `.zip` 结尾）：

```bash
qoderclicn plugins install \
  https://cdn.jsdelivr.net/npm/@snowcore8/qoder-global-user-constraints@VERSION/global-user-constraints-qoder-VERSION.zip \
  --scope user
```

Qwen 的 zip 从同前缀 npm 包下载后安装：

```bash
curl -fLO https://cdn.jsdelivr.net/npm/@snowcore8/qwen-global-user-constraints@VERSION/global-user-constraints-qwen-VERSION.zip
qwen extensions install global-user-constraints-qwen-VERSION.zip
```

三个平台包各有一个同前缀 npm 包（`@snowcore8/{qoder,qwen,dsh}-global-user-constraints`）：Qoder、Qwen 只承载
zip 与 `.sha256`，DSH 为 bundle。

安装与行为细节见 [Qoder](plugins/qoder/README.md)、[Qwen Code](plugins/qwen/README.md) 与 [DSH](plugins/dsh/README.md)。

三包与 Qoder、Qwen 两个 zip npm 包共用 SemVer 版本号，校验细节见 [docs/release.md](docs/release.md)。各端差异：

- Qoder 与 Qwen 由插件包提供约束（细节见各自 README）；DSH 以 skill 提供者与 `systemPrompt.section()`
  注入，不注册 `constraints-check` 命令。
- Qwen 不读取 `.qwen/AGENTS.md`；Qoder 项目级不提供 `.qoder-cn` 与 `.qoder/plugins`。
- 时间由 Qoder/Qwen hook 注入；DSH 使用自身时间注入。

## 验证

```bash
scripts/check.sh
```

覆盖范围、跳过条件与单独运行测试的命令见 [CONTRIBUTING.md](CONTRIBUTING.md)。

Qoder 本地安装冒烟：

```bash
scripts/materialize.sh qoder /tmp/qoder-package
qoderclicn --cwd /tmp plugins install --scope local /tmp/qoder-package
```

## 发布与 CI

- 发布：版本、tag、出包、回滚与检查单见 [docs/release.md](docs/release.md)；`scripts/dist.sh` 生成 zip 与 SHA256。
- CI：`check` 运行 `scripts/check.sh` 并做历史机密扫描；`release` 在推送 `v*` tag 时构建三包、发布
  DSH bundle 与 Qoder、Qwen 两个 zip 包、生成 SBOM 与 Release 附件。

## 安全、许可与变更

- 漏洞报告与支持版本见 [SECURITY.md](SECURITY.md)；仓库不保存密钥或个人数据。
- 文档与规范正文采用 [CC BY 4.0](LICENSE-CC-BY-4.0.txt)，代码与配置采用 [MIT](LICENSE-MIT.txt)；范围见
  [LICENSE](LICENSE)。
- 可观察变更按版本记录在 [CHANGELOG.md](CHANGELOG.md)。
