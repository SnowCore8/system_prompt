# 智能体项目指令

本文件是智能体在本仓库的项目指令。全局治理章程由宿主加载，两者冲突时以章程为准。本文件只说明仓库的
设计目标、仓库事实与本仓库的执行要求；人类贡献、治理与发布流程见 [CONTRIBUTING.md](CONTRIBUTING.md)、
[GOVERNANCE.md](GOVERNANCE.md) 与 [docs/release.md](docs/release.md)。

## 设计目标

- 本仓库的目标是打造软件工程领域最强大、最全面的治理插件包 **se-governance**：skills + MCP + rules +
  hooks + scripts + workflows 一套真源，覆盖从提出需求到发布、运维、退役的产品全生命周期（S0 受理–S7 收尾）。
- 治理先行：全局章程是唯一真源与最高准则，24 个 skill 是其落地细则；一切规则必须可判定、可核验、可追溯，
  以门禁证据为准，不以意图与口头承诺为准。
- 多端一致：同一真源经 `scripts/assemble.sh` 与 `scripts/materialize.sh` 分发到 Qoder、Qwen 与 DSH 三端，
  以 npm 包发布，带 provenance 与 SBOM，制品可复现、可验证。
- 工程标准：契约测试与全量门禁先行，内容做语义级核验，未经验证不得宣称完成；安全、授权与不可逆约束
  优先于进度。

## 真源与入口

- 唯一真源：章程 `rules/global-user-constraints.md`；24 个 skill `skills/<name>/`；MCP 服务器 `mcp/`；
  hooks `shared/scripts/`；三包清单 `plugins/{qoder,qwen,dsh}` 与 `npm/{qoder,qwen}`。
- 三端入口由 `scripts/assemble.sh` 从 `skills/`、`rules/` 生成：`.dsh/skills`、`.qoder/rules`、
  `.qoder/skills`、`.qwen/rules`、`.qwen/skills`。生成目录不提交；不得手写第二份真源。
- 发布包由 `scripts/materialize.sh` 从顶层真源组装；不依赖也不提交软链。
- `old/` 是旧代归档，只作参考素材，不得修改，不参与构建与分发。

## 生命周期

- 每个变更按微项目执行：S0 受理并分级，S2 固定范围与验收，S3 实施，S4 验证，S5 提交或发布，S7 复盘。
- 风险分级：单文件措辞、断链与只读核对为 R0；多文件、共享分支或规范语义调整为 R1。触及授权、保密、
  不可逆条款，以及插件清单、CI 与发布脚本时按 R2 处理；级别变化时重新分级并说明依据。
- 门禁证据只接受可复核的测试输出、审查结论、演练记录或明确批准；计划、口头保证与“应该没问题”不构成证据。
- 阶段编号、门禁判据与风险分级由章程与 `project-lifecycle` 裁定；本文件不复述其定义。
- 未取得用户明确同意，不得推送、打 tag、发布、写生产数据、轮换凭据或执行其他不可逆操作。

## skill 结构契约

- skill 真源为 `skills/<name>/SKILL.md` 与其 `references/`；目录名与 frontmatter `name` 必须一致。
- `SKILL.md` 二级标题按序：适用范围与优先级 → 生命周期定位 → 门禁与证据 → 维度索引 → 参考资料（最后）。
- 生命周期定位节含阶段职责表（表头 `| 阶段 | 职责 | 产出与证据 |`）；门禁与证据节含门禁证据表（表头
  `| 门禁 | 必须提供的证据 | 不满足时 |`）；维度索引的行必须与 references 文件的编号节一致。
- 正文 ≤ 250 行；正文与 references 之间、跨 skill 之间不得有逐字重复段落；不得出现历史性措辞
  （来源、取证日期、版本基线、历史沿革、新旧对照、迁移说明）。
- 仓库共 24 个 skill。新增或改名 skill 时同步 `project-lifecycle` 的映射、README 分组表、
  [docs/content-map.md](docs/content-map.md)、[docs/prompt-inventory.md](docs/prompt-inventory.md)、
  `scripts/dist.sh` 与 `tests/dsh/provider.test.mjs` 的数量断言。

## 约束与文档

- 章程以 UTF-8 字节计硬上限 64 KiB（65,536 字节）；超过时按主题把细节提取到对应 skill 的 `references/`。
- skill 真源修改后运行 `scripts/assemble.sh dev` 刷新开发入口，不复制正文。
- 说明性文档只写当前状态与事实：不写来源清单、取证日期、版本基线、历史沿革、迁移说明、新旧对照、变更记录
  或未验证自述；上述内容写入 [CHANGELOG.md](CHANGELOG.md)、提交消息或 PR。
- 文档中的 skill 数量保持 24；相对链接必须指向存在的文件。

## 校验与交付

- 写完或改完提示词、规则或 skill 正文后，必须核对逻辑、规则与语义：条款不得互相矛盾，触发条件、例外与
  失败路径必须闭合；核对未通过或未执行的，不得交付。
- 提交前运行 `scripts/check.sh`，失败先修复；交付时粘贴真实输出与退出码。未运行的验证写“未运行”。
- 单文件 Markdown 校验：`python3 scripts/mdcheck/check.py --strict <文件>`。
- 相关用例：`python3 -B -m unittest discover -s tests/mdcheck -p 'test_*.py'`、
  `python3 -B -m unittest discover -s tests/skill -p 'test_*.py'`、`npm run --silent check:js`、
  `npm run --silent coverage:js`、`npm run --silent bench:hooks`。JS 工具链先运行 `npm ci`。
- 提交按事项拆分，信息使用 `type(scope): short description`，空行后写明修改原因；不提交生成目录、缓存、
  构建产物或调试残留。
- 发布、打 tag 与出包按 [docs/release.md](docs/release.md)，不得自行发布。
