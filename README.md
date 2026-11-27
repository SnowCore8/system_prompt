# 全局用户约束：生命周期操作系统

一句话定位：本仓库把 Stage-Gate 的阶段门禁与 Agile 的迭代交付合并成一条生命周期，让每个请求先过 G0 受理，
再按 S0–S6 推进，由可核验证据而不是计划决定能否进入下一阶段。

生命周期包含七个阶段与七个门禁：S0 受理、S1 探索、S2 计划、S3 构建、S4 验证、S5 发布、S6 收尾；出口门相应为
G0–G6。风险分 R0 轻量、R1 标准、R2 关键三级，决定门禁裁剪、工件厚度与批准权限；门禁决定只有 Go、
Conditional Go、Hold、Recycle 与 No-Go，组合层另用 Defer。智能体任务、软件交付与组织级项目管理共用这套
阶段编号、决定与证据标准。

维护者：SnowCore8。职责与决策权见 [GOVERNANCE.md](GOVERNANCE.md)，智能体指令见 [AGENTS.md](AGENTS.md)，
人类贡献与发布约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 三层内容

| 层 | 回答的问题 | 载体 | 何时进入上下文 |
|---|---|---|---|
| 规则层 | 每个请求不可跳过的判定：授权、保密、不可逆、诚实、意图、门禁与交付 | `rules/global-user-constraints.md` | 常驻，随插件注入 |
| 生命周期层 | 何时做、需要什么证据、谁批准、如何复盘 | `skills/project-lifecycle-governance/` | 受理与阶段评审时加载 |
| 专业 skill 层 | 各阶段的具体规则、矩阵与检查表 | 其余 20 个 skill | 按阶段与任务加载 |

规则层以 UTF-8 字节计硬上限 64 KiB（65,536 字节）。超过上限时按主题把细节提取到对应 skill 的
`references/`，正文只保留摘要与加载指引；`scripts/check.sh` 校验该上限。

## 门禁速览

| 门禁 | 要回答的问题 | 最低证据 |
|---|---|---|
| G0 受理 | 请求、授权与风险是否清楚？ | 请求复述、授权依据、风险级别、停止条件 |
| G1 立项 | 问题是否真实、是否值得做？ | 用户与问题、结果指标、收益基线、选项比较 |
| G2 计划 | 范围、设计、验收与回滚是否成立？ | 范围与验收、设计或 ADR、测试策略、风险、回滚 |
| G3 构建 | 增量是否可验证？ | 可运行增量、测试、评审、DoD 检查 |
| G4 验证 | 是否满足验收与质量要求？ | 测试输出、安全与性能结论、验收结论 |
| G5 发布 | 能否安全上线并回滚？ | 版本与制品、CI/CD 记录、回滚演练、可观测性 |
| G6 收尾 | 是否产生价值、是否留下证据？ | 收益对照、偏差、复盘行动、归档与交接 |

阶段活动、裁剪方式与门禁判据见 `project-lifecycle-governance` 的 `references/stages.md`、`gates.md`、
`agile.md`、`roles.md`、`metrics.md`、`portfolio.md` 与 `templates.md`。

## 快速开始

开发与校验需要 `python3`、`node` 与 `git`（CI 使用 Python 3.12 与 Node 20）。

```bash
python3 -m pip install -r requirements-dev.txt
scripts/assemble.sh dev      # 生成 .dsh/.qoder/.qwen 开发入口（不提交）
scripts/check.sh             # 全量校验
```

`assemble.sh dev` 生成项目级开发入口；`materialize.sh` 组装自包含包；`dist.sh` 出包。发布流程见
[docs/release.md](docs/release.md)。

## 目录

| 路径 | 作用 |
|---|---|
| `rules/`、`skills/`、`shared/` | 唯一真源：约束正文、21 个 skill、命令与注入脚本 |
| `plugins/qoder/`、`plugins/qwen/`、`plugins/dsh/` | 三包清单、hooks 与说明；DSH 另含 `src/` 提供者代码 |
| `npm/qoder/`、`npm/qwen/` | 平台 npm 安装包清单：承载同版本 zip 与校验和 |
| `scripts/` | `assemble.sh` 生成开发入口、`materialize.sh` 组装包、`check.sh` 校验、`dist.sh` 出包 |
| `docs/` | 内容地图、提示词台账、三工具加载、hook 与注入、时间、Markdown 校验规则与发布手册 |
| `tests/`、`.github/` | 测试与 CI/Release 工作流 |
| `AGENTS.md`、`CONTRIBUTING.md` | 智能体项目指令与人类贡献约定，分离且不互相复制 |
| `.dsh/`、`.qoder/`、`.qwen/` | `assemble.sh` 生成的开发入口，被 `.gitignore` 忽略 |
| `package.json`、`plugins/marketplace.json` | DSH bundle 清单与 Qoder 本地市场描述；后者使用前运行 `scripts/assemble.sh qoder` |
| 根文档与许可证 | 治理、安全、术语、变更日志、双许可证与第三方声明 |

内容层级、21 个 skill 的主责与 references 类型见 [docs/content-map.md](docs/content-map.md)；三端 hook 事件、
注入时序与压缩后行为见 [docs/hooks-and-injection.md](docs/hooks-and-injection.md)。

## 21 个 skill 的分组与生命周期定位

`project-lifecycle-governance` 是生命周期主持者：它在 S0 固定请求与风险，在 S1/S2 组织承诺，在 S3/S4 检查
证据，在 S5/S6 组织发布与收益复盘，并裁定阶段、门禁与风险分级的归属争议。其余 20 个 skill 在各自主责阶段
提供规则与证据。

### 生命周期治理

| skill | 主责阶段 | 门禁 | 生命周期职责 |
|---|---|---|---|
| `project-lifecycle-governance` | S0–S6 | G0–G6 | 阶段、门禁、风险分级、裁剪、角色、工件、度量与组合 |

### 编写与文档

| skill | 主责阶段 | 门禁 | 生命周期职责 |
|---|---|---|---|
| `skill-authoring` | S1/S2/S4 | G1/G2/G4 | skill 包结构、触发、渐进披露与 references 组织 |
| `prompt-authoring` | S1/S2/S4 | G1/G2/G4 | 运行时提示词、输出契约、评测集与回归 |
| `system-prompt-authoring` | S1/S2/S4 | G1/G2/G4 | 常驻指令文件的内容规则与格式校验 |
| `documentation-conventions` | S1–S6 | G1/G4/G5/G6 | 章程、设计文档、指南、运行手册、变更记录与收尾报告 |

### 设计与代码

| skill | 主责阶段 | 门禁 | 生命周期职责 |
|---|---|---|---|
| `architecture-and-design-conventions` | S1–S4 | G1/G2/G3/G4 | 边界、分层、依赖方向、接缝与 ADR |
| `project-structure-conventions` | S2–S4 | G2/G3/G4 | 目录、包与工作区边界、导入与构建图、公开入口 |
| `api-and-data-conventions` | S2–S5 | G2/G3/G4/G5 | API 契约、幂等、授权边界、schema 迁移与保留 |
| `code-style-conventions` | S2–S4 | G2/G3/G4 | 格式、模块内布局、依赖版本、配置、错误与日志 |
| `naming-conventions` | S2–S5 | G2/G3/G4/G5 | 文件、代码、接口、数据、配置、提交、分支与标签名称 |
| `comment-conventions` | S2–S5 | G2/G3/G4/G5 | 行内注释、文档注释、标记、弃用与工具指令 |
| `refactoring-conventions` | S2–S5 | G2/G3/G4/G5 | 重构与修复判定、安全手法、小步提交与异味处理 |

### 运行正确性

| skill | 主责阶段 | 门禁 | 生命周期职责 |
|---|---|---|---|
| `concurrency-conventions` | S2–S4/S6 | G2/G3/G4/G6 | 共享状态、同步原语、死锁、异步模型与并发测试 |
| `performance-conventions` | S1–S6 | G1/G2/G4/G6 | 目标与预算、基准、剖析、缓存与索引取舍 |
| `debugging-conventions` | S0/S2–S6 | G0/G3/G4/G6 | 复现、二分、根因与最小修复验证 |
| `testing-and-quality-conventions` | S0–S5 | G1/G2/G3/G4/G5 | 测试层级、质量门禁、静态分析与本地/CI 对齐 |

### 交付与治理

| skill | 主责阶段 | 门禁 | 生命周期职责 |
|---|---|---|---|
| `repository-governance-conventions` | S0–S2/S5/S6 | G0/G1/G2/G5/G6 | 仓库必需文件、卫生、打包、角色与审批路由 |
| `release-operations-conventions` | S2/S5/S6 | G2/G5/G6 | 版本、CI/CD、可观测性、事故响应与备份恢复 |
| `vcs-collaboration-conventions` | S2–S5 | G2/G3/G4/G5 | 分支模型、PR/MR、审查深度、保护与所有权 |
| `worktree-collaboration-conventions` | S2/S3/S6 | G2/G3/G6 | 工作树分配、单写者、集成、恢复与清理 |
| `security-compliance-conventions` | S0–S6 | G0/G2/G4/G5 | 威胁、凭据、供应链、SBOM、许可证、PII 与披露 |

## 三个包

| 包 | 安装 |
|---|---|
| Qoder | `qoderclicn plugins install <npm zip URL> --scope user`；或解压 zip 后按目录安装 |
| Qwen Code | 下载 zip 后 `qwen extensions install global-user-constraints-qwen-<version>.zip` |
| DSH | `pnpm dsh plugin --profile PROFILE add @snowcore8/dsh-global-user-constraints@<version>` |

Qoder 的 npm zip 直链（URL 必须以 `.zip` 结尾）：

```bash
qoderclicn plugins install \
  https://cdn.jsdelivr.net/npm/@snowcore8/qoder-global-user-constraints@<version>/global-user-constraints-qoder-<version>.zip \
  --scope user
```

Qwen 的 zip 从同前缀 npm 包下载后安装：

```bash
curl -fLO https://cdn.jsdelivr.net/npm/@snowcore8/qwen-global-user-constraints@<version>/global-user-constraints-qwen-<version>.zip
qwen extensions install global-user-constraints-qwen-<version>.zip
```

三个平台包各有一个同前缀 npm 包（`@snowcore8/{qoder,qwen,dsh}-global-user-constraints`）：Qoder、Qwen 只承载
zip 与 `.sha256`，DSH 为 bundle。安装命令、hook 事件与边界见 [Qoder](plugins/qoder/README.md)、
[Qwen Code](plugins/qwen/README.md) 与 [DSH](plugins/dsh/README.md)。

三包与 Qoder、Qwen 两个 zip npm 包共用 SemVer 版本号，校验细节见 [docs/release.md](docs/release.md)。各端差异：

- Qoder 与 Qwen 由插件包提供约束；DSH 以 skill 提供者与 `systemPrompt.section()` 注入，不注册
  `constraints-check` 命令。
- Qwen 不读取 `.qwen/AGENTS.md`；Qoder 项目级不提供 `.qoder-cn` 与 `.qoder/plugins`。
- 时间由 Qoder/Qwen hook 注入；DSH 使用自身的 `dsh-time-context`。

## 验证

`scripts/check.sh` 是仓库附加门禁，覆盖常驻约束体积（≤64 KiB）、Markdown 严格校验、skill 与 hook 测试、
DSH 包测试、shellcheck、ruff、依赖审计、覆盖率（`--fail-under=90`）、JSON、敏感文件、零软链、组装与三包
清单一致性。覆盖范围、跳过条件与单独运行测试的命令见 [CONTRIBUTING.md](CONTRIBUTING.md)。

Qoder 本地安装冒烟：

```bash
scripts/materialize.sh qoder /tmp/qoder-package
qoderclicn --cwd /tmp plugins install --scope local /tmp/qoder-package
```

## 发布与 CI

- 发布是 G5 发布门与 G6 收尾门的一部分：版本、tag、出包、回滚、观测与通告见
  [docs/release.md](docs/release.md)；`scripts/dist.sh` 生成 zip 与 SHA256。
- CI：`check` 运行 `scripts/check.sh`，并对仓库历史做 gitleaks 机密扫描；`release` 在推送 `v*` tag 时构建三包，
  发布 DSH bundle 与 Qoder、Qwen 两个 zip 包，生成 SBOM 并挂载 Release 附件。

## 安全、许可与变更

- 漏洞报告渠道、支持版本与安全在生命周期各阶段的责任见 [SECURITY.md](SECURITY.md)；仓库不保存密钥或个人数据。
- 文档与规范正文采用 [CC BY 4.0](LICENSE-CC-BY-4.0.txt)，代码与配置采用 [MIT](LICENSE-MIT.txt)；范围见
  [LICENSE](LICENSE)。
- 可观察变更按版本记录在 [CHANGELOG.md](CHANGELOG.md)。
