# 智能体项目指令

本文件是智能体在本仓库的项目指令。全局用户约束由宿主加载，两者冲突时以全局用户约束为准。本文件只说明仓库
事实与本仓库的执行要求；人类贡献、治理与发布流程见 [CONTRIBUTING.md](CONTRIBUTING.md)、
[GOVERNANCE.md](GOVERNANCE.md) 与 [docs/release.md](docs/release.md)，本文件不重复这些流程。

## 真源与入口

- 唯一真源：约束正文 `rules/global-user-constraints.md`；skill `skills/`；命令与注入脚本 `shared/`；三包
  `plugins/`、根 `package.json` 与 npm 平台包 `npm/qoder/`、`npm/qwen/`。
- 修改前阅读 `README.md` 与对应目录说明；仓库为唯一真源，不建第二份副本。
- 三端入口由 `scripts/assemble.sh` 从 `skills/`、`rules/` 复制生成：`.dsh/skills`、`.qoder/rules`、
  `.qoder/skills`、`.qwen/rules`、`.qwen/skills`。生成目录不提交；不得手写第二份真源。
- 发布包由 `scripts/materialize.sh` 从顶层真源组装；不依赖也不提交软链。

## 生命周期

- 每个变更按微项目执行：S0 受理并分级，S2 固定范围与验收，S3 实施，S4 验证，S5 提交或发布，S6 复盘。
- 风险分级：单文件措辞、断链与只读核对为 R0；多文件、共享分支或规范语义调整为 R1。触及授权、保密、不可逆
  或完成判定条款，以及插件清单、CI 与发布脚本时按 R2 处理；级别变化时重新分级并说明依据。
- 门禁证据只接受可复核的测试输出、审查结论、演练记录或明确批准；计划、口头保证与“应该没问题”不构成证据。
- 阶段编号、门禁判据、风险分级、角色与工件由 `project-lifecycle-governance` 裁定；本文件不复述其定义。
- 未取得用户明确同意，不得推送、打 tag、发布、写生产数据、轮换凭据或执行其他不可逆操作。

## skill 结构

- skill 真源为 `skills/<name>/SKILL.md` 与其 `references/`；目录名与 frontmatter `name` 必须一致。
- `SKILL.md` 首节为 `## 适用范围与优先级`，含 `## 生命周期定位`（阶段职责、上下游交接、升级与停止）与
  `## 门禁与证据`（各门禁证据与不满足时的处理），末节为 `## 参考资料`；正文不超过 250 行。
- 每个 skill 的阶段契约写在 `references/lifecycle.md`：S0–S6 的输入、活动、输出与门禁，证据形态、交接、升级、
  裁剪与度量；阶段与门禁编号由 `project-lifecycle-governance` 裁定。
- 仓库共 21 个 skill。新增或改名 skill 时同步 `skills/project-lifecycle-governance/references/mappings.md`、
  [docs/content-map.md](docs/content-map.md)、[docs/prompt-inventory.md](docs/prompt-inventory.md)、
  README 的分组表、`scripts/dist.sh` 与 `tests/dsh/provider.test.mjs` 的数量断言。

## 约束与文档

- 约束正文以 UTF-8 字节计硬上限 64 KiB（65,536 字节）；超过时按主题提取到对应 skill 的 `references/`，
  正文只保留摘要与加载指引。`scripts/check.sh` 校验该上限。
- skill 真源修改后运行 `scripts/assemble.sh dev` 刷新开发入口，不复制正文。
- 说明性文档（`README.md`、`CONTRIBUTING.md`、`GOVERNANCE.md`、`SECURITY.md`、`GLOSSARY.md`、`docs/`、
  各包 README）只写当前状态与事实：不写来源清单、取证日期、版本基线、历史沿革、迁移说明、新旧对照、变更记录
  或未验证自述；上述内容写入 `CHANGELOG.md`、提交消息或 PR。
- 文档中的 skill 数量保持 21，约束上限保持 64 KiB（65,536 字节）；相对链接必须指向存在的文件。
- 代码注释与文档注释使用中文，只写当前事实；第三方引入代码保留原文注释。

## 校验与交付

- 写完或改完提示词、规则或 skill 正文后，必须核对逻辑、规则与语义：条款不得互相矛盾，触发条件、例外与失败
  路径必须闭合；核对未通过或未执行的，不得交付。
- 提交前运行 `scripts/check.sh`，失败先修复；交付时粘贴真实输出与退出码。未运行的验证写“未运行”。
- 单文件 Markdown 校验：`python3 skills/system-prompt-authoring/scripts/check.py --strict <文件>`。
- 相关用例：`python3 -B -m unittest discover -s tests/skill -p 'test_*.py'`、`node --test tests/hooks/*.test.js`、
  `node --test tests/dsh/provider.test.mjs`。
- 提交按事项拆分，信息使用 `type(scope): short description`，空行后写明修改原因；不提交生成目录、缓存、
  构建产物或调试残留。
- 发布、打 tag 与出包按 [docs/release.md](docs/release.md)，不得自行发布。
