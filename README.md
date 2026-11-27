# se-governance：软件工程治理套件

面向编码智能体的完整治理套件：一份治理章程 + 24 个 skill + MCP 工具服务器 + hooks + 工程脚本与 CI，
覆盖软件产品的全生命周期——从提出需求，经设计、构建、验证、发布、运维，到收尾退役。

维护者：SnowCore8。治理与发布见 [GOVERNANCE.md](GOVERNANCE.md) 与 [docs/release.md](docs/release.md)。

## 组成

| 组件 | 内容 | 载体 |
|---|---|---|
| 治理章程 | 8 阶段（S0–S7）与 8 门禁（G0–G7）、风险三级（R0/R1/R2）、十大规则域（SEC/AUT/IRR/HON/INT/GAT/EXE/CHG/UNC/OUT） | `rules/global-user-constraints.md`（≤64 KiB，随插件注入） |
| skill | 24 个，覆盖生命周期主链、编码维度与智能体工程 | `skills/<name>/` |
| MCP | 8 个工具：条款审查、风险分级、门禁记录、skill 索引、阶段建议、变更评估、发布检查单、复盘模板 | `mcp/`（`@snowcore8/se-mcp`，stdio） |
| hooks | 会话启动注入章程、提示提交提醒、压缩后恢复、时间注入 | `shared/scripts/` |
| scripts | 组装、出包、全量门禁、版本同步、性能基准、Markdown 校验器 | `scripts/` |
| workflows | 版本矩阵、Windows、可复现构建、性能预算、CodeQL、provenance 发布 | `.github/workflows/` |

## 生命周期模型

| 阶段 | 目的 | 出口门 |
|---|---|---|
| S0 受理 | 确认请求、授权、风险与停止条件 | G0 受理门 |
| S1 需求 | 确认需求真实、值得做、成功标准清楚 | G1 立项门 |
| S2 设计 | 固定范围、方案、验收、依赖与回滚 | G2 计划门 |
| S3 构建 | 以可运行增量实现并持续验证 | G3 构建门 |
| S4 验证 | 证明满足验收、质量与合规要求 | G4 验证门 |
| S5 发布 | 安全上线并具备回滚与观测能力 | G5 发布门 |
| S6 运维 | 维持服务可用并持续改进 | G6 运维门 |
| S7 收尾 | 对照收益、处理偏差、留下教训并退役 | G7 收尾门 |

门禁决定只有六种：Go、Conditional Go、Hold、Recycle、No-Go，组合层另用 Defer。阶段与门禁的判据、证据
标准与模板见 `project-lifecycle` 的 `references/`。

## 24 个 skill

| 分组 | skill |
|---|---|
| 生命周期主链 | `project-lifecycle`、`requirements-engineering`、`architecture-design`、`planning-estimation`、`implementation-practices`、`testing-quality`、`release-operations`、`maintenance-retirement` |
| 编码维度 | `code-style`、`naming`、`comments`、`refactoring`、`code-review`、`concurrency`、`performance`、`debugging`、`api-data`、`security-compliance`、`documentation`、`project-structure`、`vcs-collaboration` |
| 智能体工程 | `prompt-engineering`、`system-prompt-engineering`、`mcp-engineering` |

每个 skill 的主责阶段、门禁证据与交接见 [docs/content-map.md](docs/content-map.md)。

## MCP

`@snowcore8/se-mcp` 提供 8 个工具，注册方式见 [docs/mcp-usage.md](docs/mcp-usage.md)：

| 工具 | 用途 |
|---|---|
| `constraints_check` | 对请求/方案/命令做章程条款级静态审查（启发式，不构成人工审查结论） |
| `risk_classify` | 按文件数、共享、生产与不可逆性判定 R0/R1/R2 |
| `gate_record` | 生成 G0–G7 门禁记录模板 |
| `list_skills` | 列出 24 个 skill 与触发描述 |
| `lifecycle_stage` | 按请求类型建议阶段、门禁与最低证据 |
| `change_assessment` | 基线变更请求与影响评估模板 |
| `release_checklist` | G5 发布检查单 |
| `retrospective` | G7 复盘模板 |

## 安装

| 平台 | 方式 |
|---|---|
| Qoder | `qoderclicn plugins install <zip URL> --scope user`，或解压后按目录安装 |
| Qwen Code | 下载 zip 后 `qwen extensions install se-governance-qwen-<version>.zip` |
| DSH | `pnpm dsh plugin --profile PROFILE add @snowcore8/se-dsh@<version>` |

Qoder 的 npm zip 直链（URL 必须以 `.zip` 结尾）：

```bash
qoderclicn plugins install \
  https://cdn.jsdelivr.net/npm/@snowcore8/se-qoder@<version>/se-governance-qoder-<version>.zip \
  --scope user
```

Qwen 的 zip 从同前缀 npm 包下载后安装：

```bash
curl -fLO https://cdn.jsdelivr.net/npm/@snowcore8/se-qwen@<version>/se-governance-qwen-<version>.zip
qwen extensions install se-governance-qwen-<version>.zip
```

旧包（`@snowcore8/{qoder,qwen,dsh}-global-user-constraints`）已弃用，保留在 npm 但不再更新。

## 开发与验证

开发与校验需要 `python3`、`node`、`npm` 与 `git`；CI 在 Python 3.12/3.14 与 Node 22/24 的组合上运行校验。

```bash
python3 -m pip install --require-hashes -r requirements-dev.txt
npm ci                       # 安装 Biome、c8 与 MCP SDK
scripts/assemble.sh dev      # 生成三端开发入口（不提交）
scripts/check.sh             # 全量校验
```

`scripts/check.sh` 覆盖：章程体积（≤64 KiB）、Markdown 严格校验、24 skill 结构契约、hooks/MCP/校验器
测试、JS lint 与格式（Biome）、JS 覆盖率、shellcheck、ruff、依赖审计、Python 覆盖率、JSON、敏感文件、
零软链、组装与三包一致性。CI 另含 Windows 验证、跨时区可复现构建、hook 冷启动预算与 CodeQL；发布流程
带 npm provenance 与构建来源证明，见 [docs/release.md](docs/release.md)。

## 目录

| 路径 | 作用 |
|---|---|
| `rules/`、`skills/`、`mcp/`、`shared/` | 唯一真源：章程、24 个 skill、MCP 服务器、hooks |
| `plugins/{qoder,qwen,dsh}` | 三端清单、hooks 与 DSH 提供者 |
| `npm/{qoder,qwen}` | 平台 zip 承载包清单 |
| `scripts/` | 组装、出包、门禁、版本同步、基准与 Markdown 校验器 |
| `docs/` | 内容地图、MCP 用法、hook 与注入、威胁模型、发布手册 |
| `tests/`、`.github/` | 测试与 CI/Release 工作流 |
| `AGENTS.md`、`CONTRIBUTING.md` | 智能体项目指令与人类贡献约定 |
| `old/` | 旧代内容归档（仅参考，不参与构建与分发） |

## 安全、许可与变更

- 漏洞报告与安全责任见 [SECURITY.md](SECURITY.md)；威胁模型见 [docs/threat-model.md](docs/threat-model.md)。
- 文档与规范正文采用 [CC BY 4.0](LICENSE-CC-BY-4.0.txt)，代码与配置采用 [MIT](LICENSE-MIT.txt)。
- 可观察变更记录在 [CHANGELOG.md](CHANGELOG.md)。
