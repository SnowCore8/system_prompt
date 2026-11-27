# 贡献与维护约定

本文件是人类贡献者与维护者的约定。每一次变更都按微项目处理：先过受理门，再计划、实施、验证、提交与发布，
每一步留下可核验证据。本文件不进入模型上下文；智能体项目指令见 [AGENTS.md](AGENTS.md)，两者分离，不互相复制。

约束正文为 `rules/global-user-constraints.md`，随插件分发：Qwen Code 通过 `.qwen/rules/` 读取项目级规则，
Qoder 通过 `.qoder/rules` 读取；用户级安装插件后，由插件包提供同一份约束。约束正文不定义本仓库的贡献流程；
在本仓库贡献仍须遵守已加载的全局用户约束。

阅读时机：修改约束、skill、插件或脚本之前。维护者：SnowCore8（仓库所有者）。角色分工、审查与发布授权见
[GOVERNANCE.md](GOVERNANCE.md)。

## 范围与优先级

- 本文件仅约束本仓库的维护工作；与已加载的全局用户约束冲突时，以全局用户约束为准。
- 只修改被请求的内容；仓库为唯一真源，不另建副本。
- 代码注释与文档注释使用中文；第三方引入代码保留其原文注释。
- 开发入口由 `scripts/assemble.sh` 生成到 `.dsh`、`.qoder`、`.qwen`；生成目录不提交，不依赖 Windows
  `core.symlinks`。
- 说明性文档只写当前事实：来源清单、取证日期、版本基线、历史沿革、迁移说明与新旧对照写入
  [CHANGELOG.md](CHANGELOG.md)、提交消息或 PR。

## 真源与组装

| 内容 | 真源 | 生成物 |
|---|---|---|
| 约束正文 | `rules/global-user-constraints.md` | 三端 `rules/` 入口与包内 `rules/`、`constraints/` |
| skill | `skills/<name>/SKILL.md` 与 `references/` | `.dsh/skills`、`.qoder/skills`、`.qwen/skills`、包内 `skills/` |
| 命令与注入脚本 | `shared/commands/`、`shared/scripts/` | Qoder 包的 `commands/`、`scripts/` |
| 包清单与 hook | `plugins/qoder`、`plugins/qwen`；DSH 为根 `package.json` 与 `plugins/dsh` | 由 `scripts/materialize.sh` 组装的安装包 |
| zip npm 包 | `npm/qoder/package.json`、`npm/qwen/package.json` | 只承载 zip 与校验和 |

约束正文以 UTF-8 字节计硬上限 64 KiB（65,536 字节）；超限时按主题把规则提取到对应 skill 的 `references/`，
正文只保留摘要与加载指引。`scripts/check.sh` 校验该上限。

## 变更即微项目

| 步骤 | 阶段与门禁 | 本仓库动作 | 证据 |
|---|---|---|---|
| 受理 | S0 / G0 | 复述变更对象与预期结果，确认授权、风险级别与停止条件 | 变更说明、风险依据 |
| 分级 | S0 / G0 | 按 R0/R1/R2 判断门禁强度；级别不明取高 | 分级结论与理由 |
| 计划 | S2 / G2 | 固定范围与不做事项，写明验收标准、受影响的 skill 与文档、回滚方式 | 计划或任务清单、验收句 |
| 实施 | S3 / G3 | 只改真源，小步提交；生成目录由脚本重建 | 源文件 diff、组装结果 |
| 验证 | S4 / G4 | 运行相关用例，再跑 `scripts/check.sh`，人工核对规则语义 | 校验输出、退出码、核对结论 |
| 提交 | S3 / G3 | 按事项拆分提交，粘贴真实输出；涉及规范语义时写明动机、影响与回滚 | 提交消息、PR 记录 |
| 发布 | S5 / G5 | 按 `docs/release.md` 走发布门；发布后核对制品与附件 | 发布记录、校验和 |

- 不得以“改动很小”跳过 G0 或 G4；R0 可以合并记录，但仍须执行验证。
- 交付时先给结论与状态，再给证据；未运行的验证写“未运行”，不得粘贴未曾见到的输出。
- 同一问题连续两次返工未解决时升级：重新评估范围、方案或目标，不得在旧方案上叠加补丁。

## 本仓库的风险分级

| 级别 | 本仓库的典型变更 | 门禁要求 |
|---|---|---|
| R0 | 错别字、断链、文档措辞、只读核对 | 自检加 `scripts/check.sh`；可合并受理与计划记录 |
| R1 | 单 skill 内容调整、文档结构重写、测试或脚本的非语义修复 | G0–G5 轻量执行；G4 至少一名非作者审查，无法取得时按 `GOVERNANCE.md` 登记例外 |
| R2 | 授权、保密、不可逆或完成判定条款的语义变更；插件清单、CI 与发布脚本；版本与发布决定 | G0–G6 全阶段记录；G4 与 G5 不得合并；人工批准；独立结论无法取得时 Hold，不得以例外放行 |

范围、影响或授权变化时重新分级，并在提交说明中记录新级别与依据。

## 新增或改名 skill

1. 在 `skills/<name>/` 建立 `SKILL.md`、`references/` 与可选 `scripts/`；frontmatter 的 `name` 必须与目录名一致。
2. 在 `SKILL.md` 中写入生命周期结构：首节为 `## 适用范围与优先级`，其后为 `## 生命周期定位`（阶段职责、上下游
   交接、升级与停止）与 `## 门禁与证据`（各门禁的证据与不满足时的处理），末节为 `## 参考资料`。
3. 在 `references/lifecycle.md` 写该 skill 的阶段契约：S0–S6 的输入、活动、输出与门禁，门禁证据形态与不可接受
   的证据，交接、升级、裁剪与度量。阶段与门禁编号由 `project-lifecycle-governance` 裁定，本文件只落地，不重述定义。
4. 更新生命周期映射：`skills/project-lifecycle-governance/references/mappings.md` 的 skill 归属、阶段覆盖与工件
   归属，以及 [docs/content-map.md](docs/content-map.md) 的主责表与 references 列表。
5. 同步计数与文档：README 的分组表、[docs/prompt-inventory.md](docs/prompt-inventory.md)、`scripts/dist.sh` 的
   数量断言、`tests/dsh/provider.test.mjs` 的数量断言，以及三包 README 与清单中的 skill 计数。
6. 运行 `scripts/assemble.sh dev` 刷新三端开发入口；运行 `scripts/materialize.sh <包> <目标目录>` 验证安装包；
   不复制正文、不提交软链。
7. 运行 `scripts/check.sh`；涉及分发时按 [docs/release.md](docs/release.md) 出包并核对 zip 内的 skill 数量。

改名按“先新增、后删除”处理：新目录满足上述要求后，删除旧目录并清理全部引用，包括
`rules/global-user-constraints.md` 的 skill 索引、各 skill 的交接说明与 docs 中的链接。

## 文档变更

- 根文档与包 README 属于分发材料：安装命令、包名、路径与平台差异必须与实际清单一致，不得虚构命令或行为。
- 文档提到的 skill 数量保持 21；约束正文上限保持 64 KiB（65,536 字节）。
- 相对链接必须指向存在的文件；行宽不超过 200 字符，不使用制表符，文件以单个换行结尾。
- 文档中的流程描述与当前 skill 结构一致：卡片式罗列不算流程，每节要说明阶段、门禁与证据。

## 校验与打包

- 环境：`python3`、`node` 与 `git`（CI 使用 Python 3.12 与 Node 20）。
- 依赖安装：`python3 -m pip install -r requirements-dev.txt`。
- 全量校验：`scripts/check.sh`，覆盖常驻约束体积（≤64 KiB）、Markdown、skill 与 hook 测试、DSH bundle 的
  `node --test`、shellcheck、ruff、依赖审计（pip-audit）、覆盖率（`--fail-under=90`）、JSON、敏感文件、
  零软链与组装、发布包清单一致性。缺少 `shellcheck` 或 `qoderclicn` 时对应段打印「跳过」；缺少 `python3`、
  `node`、`git` 或任一 Python 校验依赖时，脚本直接退出 2。交付时说明缺口。
- 单文件 Markdown 校验：
  `python3 skills/system-prompt-authoring/scripts/check.py --strict <文件>`，退出码 0 表示无错误。
- 单独运行测试：skill 测试使用
  `python3 -B -m unittest discover -s tests/skill -p 'test_*.py'`；hook 测试使用
  `node --test tests/hooks/*.test.js`；DSH 包测试使用 `node --test tests/dsh/provider.test.mjs`。
- 发布、版本、tag 与出包流程见 [docs/release.md](docs/release.md)；本地出包使用 `scripts/dist.sh`。

## 分支与审查

- 分支模型为 trunk-based：单人维护，直接提交 `master`，不强制 PR。
- `.github/CODEOWNERS` 将全部路径指派给仓库所有者；PR 模板要求粘贴 `scripts/check.sh` 的真实输出与退出码。
- 分支保护、必需校验与 R2 审查要求见 [GOVERNANCE.md](GOVERNANCE.md)。
