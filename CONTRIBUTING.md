# 贡献与维护约定

本文件是人类贡献者与维护者的约定。每一次变更都按微项目处理：先过受理门，再计划、实施、验证、提交与发布，
每一步留下可核验证据。本文件不进入模型上下文；智能体项目指令见 [AGENTS.md](AGENTS.md)，两者分离。

维护者：SnowCore8（仓库所有者）。角色分工、审查与发布授权见 [GOVERNANCE.md](GOVERNANCE.md)。

## 范围与优先级

- 本文件仅约束本仓库的维护工作；与全局治理章程冲突时，以章程为准。
- 只修改被请求的内容；仓库为唯一真源，不另建副本；`old/` 只读归档。
- 代码注释与文档注释使用中文；第三方引入代码保留其原文注释。
- 开发入口由 `scripts/assemble.sh` 生成到 `.dsh`、`.qoder`、`.qwen`；生成目录不提交，不依赖软链。

## 真源与组装

| 内容 | 真源 | 生成物 |
|---|---|---|
| 章程 | `rules/global-user-constraints.md` | 三端 `rules/` 入口与包内 `rules/`、`constraints/` |
| skill | `skills/<name>/SKILL.md` 与 `references/` | `.dsh/skills`、`.qoder/skills`、`.qwen/skills`、包内 `skills/` |
| MCP | `mcp/` | DSH bundle 内置；`@snowcore8/se-mcp` 独立发布 |
| hooks | `shared/scripts/` | Qoder/Qwen 包的 `scripts/` |
| 包清单 | `plugins/{qoder,qwen,dsh}`、`npm/{qoder,qwen}` | 由 `scripts/materialize.sh` 组装的安装包 |

## 变更即微项目

| 步骤 | 阶段与门禁 | 本仓库动作 | 证据 |
|---|---|---|---|
| 受理 | S0 / G0 | 复述变更对象与预期结果，确认授权、风险级别与停止条件 | 变更说明、风险依据 |
| 分级 | S0 / G0 | 按 R0/R1/R2 判断门禁强度；级别不明取高 | 分级结论与理由 |
| 计划 | S2 / G2 | 固定范围与不做事项，写明验收标准、受影响的 skill 与文档、回滚方式 | 计划或任务清单、验收句 |
| 实施 | S3 / G3 | 只改真源，小步提交；生成目录由脚本重建 | 源文件 diff、组装结果 |
| 验证 | S4 / G4 | 运行相关用例，再跑 `scripts/check.sh`，人工核对规则语义 | 校验输出、退出码、核对结论 |
| 提交 | S3 / G3 | 按事项拆分提交，粘贴真实输出；涉及规范语义时写明动机、影响与回滚 | 提交消息、PR 记录 |
| 发布 | S5 / G5 | 按 [docs/release.md](docs/release.md) 走发布门 | 发布记录、校验和 |

- 不得以“改动很小”跳过 G0 或 G4；R0 可以合并记录，但仍须执行验证。
- 交付时先给结论与状态，再给证据；未运行的验证写“未运行”，不得粘贴未曾见到的输出。
- 同一问题连续两次返工未解决时升级：重新评估范围、方案或目标。

## 本仓库的风险分级

| 级别 | 本仓库的典型变更 | 门禁要求 |
|---|---|---|
| R0 | 错别字、断链、文档措辞、只读核对 | 自检加 `scripts/check.sh`；可合并受理与计划记录 |
| R1 | 单 skill 内容调整、文档结构重写、测试或脚本的非语义修复 | G0–G5 轻量执行；G4 至少一名非作者审查 |
| R2 | 授权、保密、不可逆条款的语义变更；插件清单、CI 与发布脚本；版本与发布决定 | G0–G7 全阶段记录；G4 与 G5 不得合并；人工批准 |

范围、影响或授权变化时重新分级，并在提交说明中记录新级别与依据。

## 新增或改名 skill

1. 在 `skills/<name>/` 建立 `SKILL.md` 与 `references/`；frontmatter 的 `name` 必须与目录名一致。
2. 按 [AGENTS.md](AGENTS.md) 的结构契约组织：五个二级标题按序、阶段职责表与门禁证据表、维度索引与
   references 编号节一致、正文 ≤ 250 行、无逐字重复、无历史措辞。
3. 在 `references/lifecycle.md` 写阶段契约：S0–S7 的输入、活动、输出与门禁，证据形态、交接、升级与裁剪。
4. 更新生命周期映射：`project-lifecycle` 的跨 skill 映射、[docs/content-map.md](docs/content-map.md)、
   [docs/prompt-inventory.md](docs/prompt-inventory.md) 与 README 分组表。
5. 同步计数：`scripts/dist.sh` 与 `tests/dsh/provider.test.mjs` 的数量断言（当前 24）。
6. 运行 `scripts/assemble.sh dev` 刷新三端开发入口；运行 `scripts/materialize.sh <包> <目录>` 验证安装包。
7. 运行 `scripts/check.sh`；涉及分发时按 [docs/release.md](docs/release.md) 出包并核对 zip 内容。

## 文档变更

- 根文档与包 README 属于分发材料：安装命令、包名、路径与平台差异必须与实际清单一致，不得虚构命令或行为。
- 文档提到的 skill 数量保持 24；章程上限保持 64 KiB（65,536 字节）。
- 相对链接必须指向存在的文件；行宽不超过 200 字符，不使用制表符，文件以单个换行结尾。

## 校验与打包

- 环境：`python3`、`node`、`npm` 与 `git`；CI 在 Python 3.12/3.14 与 Node 22/24 的组合上运行校验。
- 依赖安装：`python3 -m pip install --require-hashes -r requirements-dev.txt`；`requirements-dev.txt` 由
  `pip-compile --generate-hashes --allow-unsafe` 从 `requirements-dev.in` 生成，用最低支持的 Python 3.12
  重新生成。JS 工具链用 `npm ci` 安装。
- 全量校验：`scripts/check.sh`，覆盖章程体积（≤64 KiB）、Markdown、24 skill 结构契约、校验器/hooks/MCP
  测试、JS lint 与覆盖率、shellcheck、ruff、依赖审计、Python 覆盖率、JSON、敏感文件、零软链、组装与
  三包一致性。缺少 `shellcheck` 或 `qoderclicn` 时对应段打印「跳过」；缺少必要工具时脚本直接退出 2。
- 单文件 Markdown 校验：`python3 scripts/mdcheck/check.py --strict <文件>`。
- 单独运行测试：`python3 -B -m unittest discover -s tests/mdcheck -p 'test_*.py'`、
  `python3 -B -m unittest discover -s tests/skill -p 'test_*.py'`、`npm run --silent check:js`、
  `npm run --silent coverage:js`。
- 性能预算：`npm run --silent bench:hooks`（hook 冷启动 p95 < 500ms）。
- 发布、版本、tag 与出包流程见 [docs/release.md](docs/release.md)。

## 分支与审查

- 分支模型为 trunk-based：单人维护，直接提交 `master`，不强制 PR。
- `.github/CODEOWNERS` 将全部路径指派给仓库所有者；PR 模板要求粘贴 `scripts/check.sh` 的真实输出与退出码。
- 分支保护、必需校验与 R2 审查要求见 [GOVERNANCE.md](GOVERNANCE.md)。
