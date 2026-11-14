# 变更日志

按日期记录本仓库的可观察变更，最新在前。版本号由 `scripts/dist.sh` 按改动插件的提交数推导，不构成发布边界，因此不按版本分节。条目由 git 历史整理，同一主题的重复提交合并为一条。

## 2026-11-14

**新增**

- `naming-conventions` skill：通用命名规范，覆盖文件、包、类型、函数、变量、常量、布尔、集合、数量与单位、异步、错误、测试、API、数据库、配置、CLI、日志、资产、提交、基础设施、权限与发布包等维度，并提供语言矩阵、审查清单与改名迁移规则。
- `comment-conventions` skill：代码注释规范，覆盖 doc 注释与 API 契约、文件与模块头、行内说明、单位与所有权、并发与性能警告、废弃标记、TODO、注释掉的代码、生成代码与许可证头、工具指令，并提供 24 个维度与 18 种语言的注释语法与文档工具对照。
- `documentation-conventions` skill：项目文档规范，覆盖 README、贡献指南、架构与设计文档、ADR、教程与指南、参考与 API 文档、变更日志、运行手册、安全与支持文档、迁移与废弃、文档测试与站点工具，并提供 26 个维度与 20 类文档模板。
- `code-style-conventions` skill：代码风格规范，覆盖格式化与 lint、目录与模块边界、依赖与配置管理、错误与日志策略、生成与第三方代码。
- `api-and-data-conventions` skill：接口与数据规范，覆盖 API 契约、错误模型、幂等分页与版本、数据库迁移与数据保留。
- `testing-and-quality-conventions` skill：测试与质量规范，覆盖测试分层、质量门禁与覆盖率、静态检查、本地开发环境。
- `vcs-collaboration-conventions` skill：版本控制与协作规范，覆盖 Git 工作流、PR、代码审查、分支保护与代码所有权。
- `release-operations-conventions` skill：发布与运维规范，覆盖版本与发布、变更管理、CI/CD、可观测性、事故响应与备份恢复。
- `security-compliance-conventions` skill：安全与合规规范，覆盖安全开发、凭据与密钥、许可证与 SBOM、隐私与漏洞披露。
- `repository-governance-conventions` skill：仓库治理规范，覆盖必需文件与元数据、仓库卫生、治理流程与打包分发。
- 根 `AGENTS.md` 软链指向 `rules/global-user-constraints.md`，供 DSH 作为工作区指令加载；Qoder 仍按插件规则激活。
- DeepSeek Harness 适配：新增 `.dsh/skills/` 项目级入口，以相对软链暴露插件内十一个 skill；`scripts/check.sh` 增加 DSH 适配校验。
- 软链治理：`scripts/check.sh` 增加全量软链校验（必须入库、相对路径、目标在仓库内且存在、不指向另一软链或 `.git`、目标已跟踪）；README 补充软链约定。
- 根 `AGENTS.md` 由约束正文软链改为本仓库项目维护约定；用户全局约束保留在 `rules/`，不再作为 DSH 项目指令自动加载，需要时由用户级指令或 Qoder 插件规则激活提供。
- 入口修正：删除 `.qwen` 软链（Qwen 不读 `rules/`）；根 `AGENTS.md` 恢复为约束正文入口，项目维护约定移至 `CONTRIBUTING.md`。
- Qwen 入口修正：Qwen Code 只读 `.qwen/AGENTS.md`，该文件软链指向约束正文；根 `AGENTS.md` 改为项目维护约定入口（软链 `CONTRIBUTING.md`）。
- 新增 `docs/agent-tooling-loading.md`：分别整理 Qoder、Qwen Code 与 DeepSeek Harness 的 rules/skills/plugins 加载规则，附对照表与本仓库映射。

**变更**

- 根入口改为 `.qoder` 实际目录；`.qwen`、`.qoder-cn` 软链指向 `.qoder`，`.gitignore` 的本地配置路径同步。
- `documentation-conventions` 的 `SECURITY.md` 条目只保留页面结构与行文，必需内容与响应承诺归 `security-compliance-conventions`。
- 规范正文与十一个 skill 改为中文语义正文：`rules/global-user-constraints.zh-CN.md` 成为规范源，英文版降为参考译本；`AGENTS.md`、插件 README、命令、`qoder.md`、manifest 与 hooks 描述同步。
- `GLOSSARY.md` 增加翻译与写作口径与中英术语对照，统一审查/审计、校验/检查、第三方引入、包仓库、运行手册/操作手册、事故复盘、制品/产物、销毁性/破坏性等写法。
- 移除英文参考译本：中文正文改名为 `rules/global-user-constraints.md` 并成为唯一规范文件；`AGENTS.md`、插件 README、命令与 `qoder.md` 同步。

**修复**

- 旧 skill 治理：`naming-conventions`、`comment-conventions`、`documentation-conventions`、`system-prompt-authoring` 补齐与七个通用规范的归属边界，移除重复的教学与流程内容；命名索引与 34 个维度章节一一对应。
- `system-prompt-authoring` 补 Scope 与 Review Checklist，核验来源并修正过期引文，`--strict` 说明与 checker 行为对齐；仓库 README 与术语表不再把内容规则限定为 S1–S13。
- 入口按三工具实际加载规则整改：Qwen 项目级约束入口改为 `.qwen/rules/global-user-constraints.md`
  （baseline 规则），删除不被读取的 `.qwen/AGENTS.md`；删除项目级无加载语义的 `.qoder-cn` 与
  `.qoder/plugins`，保留 `.qoder/rules`；`scripts/check.sh` 新增「Qoder 适配」并改写「Qwen 适配」；
  README、CONTRIBUTING 与插件 README 同步，插件 README 的 `.qoder*/rules` 说法改为实际路径。

## 2026-11-12

**新增**

- `scripts/check.sh`：校验全部未忽略的 Markdown，并运行 skill 与 hook 测试、shellcheck 与 JSON 解析；`qoderclicn` 存在时再跑插件校验。
- `requirements-dev.txt` 声明 `markdown-it-py>=3`；`.editorconfig` 统一编码、换行与缩进。
- `GLOSSARY.md`：术语与写法约定，作为文档、注释与校验输出的统一口径。
- `rules/global-user-constraints.zh-CN.md`：用户全局约束中文译本，条款编号与英文原文一一对应，英文原文为准。

**修复**

- `check.py` 的 `MD-LINK-SYNTAX` 改为按段落行范围比对，多行段落里的合法链接不再误报；补三条回归测试。
- `dist.sh` 去掉对不存在路径的排除项；`check.sh` 纳入未跟踪但未忽略的 Markdown 与 JSON；`.gitignore` 的临时目录改为 `.qwen/tmp/`。

**变更**

- skill 的 `script/` 更名为 `scripts/`，SKILL 与 README 的引用同步。
- 移除 `qoderwork.md`，插件级指令文件只保留 `qoder.md`。
- 约束正文精修：统一关键词用法，补 Internal address 与 Delivery 定义，消除请求分类与输出条款的歧义。
- 经 `python3` 调用的脚本改为 644，直接执行的脚本保持 755。

**文档**

- README 验证段改为 `scripts/check.sh`，目录表补 `check.sh` 与 `GLOSSARY.md`。
- 中文术语按 `GLOSSARY.md` 统一：用户全局约束、约束正文、校验、校验脚本等；旧写法不再使用。
- README 的校验说明改为准确描述；移除 `qoder.md` 中无法生效的回退句；删除变更日志里无信息的「约束正文更新」条目。

## 2026-11-11

**变更**

- 约束正文改为条款化规范（MUST / MUST NOT / SHOULD / MAY），明确违反任一 MUST 即任务失败。
- `.qwen/settings.local.json` 不再进入版本库。

**移除**

- ts2cpp 工作流与 Translator、Critic、Fixer、Orchestrator 四个 agent 定义。

**修复**

- 插件校验命令统一改用 `qoderclicn`，避免 `qodercn` 把仓库根的 `plugins/` 当作 IDE 目标。

**文档**

- 两份 README 按受众去重，修正失效命令；规则激活、打包与校验说明回流根 README。

## 2026-11-06

**变更**

- 插件源由 `.qoder/plugins/` 迁至根级 `plugins/`，约束正文由插件包内迁至根级 `rules/`。
- 插件包重新随包分发约束：包内 `rules` 软链指向根级 `rules/`，`scripts/dist.sh` 用 `cp -aL` 解引用后打包，并在结构校验中要求 `rules/global-user-constraints.md` 存在。
- 新增 `.qwen/` 作为统一入口，其下 `rules`、`plugins` 软链指向根级同名目录；`.qoder`、`.qoder-cn` 指向 `.qwen`。
- `scripts/dist.sh` 的 `PLUGIN_REL` 改为 `plugins/global-user-constraints`；版本推导把迁移前 `.qoder/plugins/` 路径的提交一并计入，避免版本回退。

**移除**

- 根 `AGENTS.md`、`.qoder/agents`、`.qoder/skills` 软链，以及旧版 `.qwen -> .qoder` 软链。

**文档**

- 根 README 与插件 README 的目录表、编辑步骤、验证命令、规则激活步骤更新到新布局。
- 插件 README 的规则激活步骤区分本地目录安装与 zip/市场安装的复制源；`marketplace.json` 描述改为根级 `plugins/`。

## 2026-11-01

**新增**

- `ts2cpp` 工作流，串联 Translator、Critic、Fixer、Orchestrator 四个 agent。
- TS→C++ 翻译流水线的四个 agent 定义。
- `marketplace.json` 承载市场字段，manifest 相应精简。

**修复**

- `constraints-check` 命令补 frontmatter。
- skill 校验脚本的级别与长度规则矛盾。
- agent 工作流的严重度与输出契约不对齐。
- `dist.sh` 校验改用 `qodercn plugins validate`。
- 插件说明补充规则激活步骤，打包说明校正。

**变更**

- `dist.sh` 打包成功后清理仓库根目录的旧 zip。

**文档**

- 移除企业插件相关说明，文档改为正向陈述。
- 补充 agent 与 marketplace 目录说明，纠正规则加载边界。

## 2026-10-31

**变更**

- 尝试由 `SessionStart` / `SubagentStart` hook 注入规则，随后回滚。

## 2026-10-30

**新增**

- hook 改为按事件注入当前时间。

**修复**

- hook 解释器改用 `python`，兼容 Windows。
- `dist.sh` 只拦截 `scripts/` 下残留的 Python 脚本。

**变更**

- hook 一度改为编译二进制以去除运行时依赖，随后回退到 Python 实现。

## 2026-10-28

**新增**

- `global-user-constraints` 插件。
- 分发脚本 `scripts/dist.sh`，产物按 commit id 命名。
- `.qwen` 兼容软链。

**变更**

- 插件移动到 `.qwen/plugins`，随后目录名从 `.qwen` 改为 `.qoder`。
- 根 `AGENTS.md` 改为插件约束的软链。
- skill 改为插件源软链，并直接链接整个 `skills/` 目录。
- zip 文件名改用 commit id；版本先自动递增 patch，后改为按插件提交数推导。

**修复**

- secret hook 的提交识别与 `--all` 扫描。

**文档**

- README 重写并改为简体中文。
- 约束文档按模块拆分，并区分问题、陈述与明确动作请求。

## 2026-10-27

**变更**

- 约束正文改为英文并重写。
- skill 文档补充决策表与状态表指南，并翻译为英文。

## 2026-10-26

**新增**

- Markdown 格式校验扩展为完整结构校验，补齐格式规则表。

**变更**

- 校验范围收敛为 Markdown 格式，校验脚本重写。
- provenance 长引文折行。

## 2026-10-23

**新增**

- 正文单行长度上限，先设 100 字后调整为 200 字。

**变更**

- 约束正文多次修订：优先级声明、分节排序、语义去重与压缩。
- 保密范围扩展到项目内容。

**文档**

- README 补文件职责表与校验命令。

## 2026-10-21

**新增**

- 以 `markdown-it-py` 重写的校验脚本，新增 `--strict` 与 `MD-HEAD-START`。
- 结构校验补齐链接、图片、列表与退化表格。

**修复**

- 引用块表格漏检、嵌套图片误判空链接、编码路径漏判。
- 示例区与行内 HTML 判定。
