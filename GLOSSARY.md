# 术语表

本仓库的术语与写法约定。改文档、注释或校验输出前先读本表；维护者：仓库所有者。

| 术语 | 英文 | 用法 | 不要写成 |
|---|---|---|---|
| 全局用户约束 | Global User Constraints（插件名） | `rules/global-user-constraints.md` 的正文与整体 | 用户全局约束、约束规则、全局规则 |
| 约束正文 | constraint text | 该文件的内容 | 规则正文 |
| 约束条款 | constraint clause | 正文中的单条编号要求（SP-1 等） | 规则条款 |
| 约束文件 | constraints file | 承载全局用户约束的文件 | 规则文件 |
| 规则 | rule | 宿主 rules 机制（规则目录、规则激活），以及 skill 的内容与格式规则（各 skill 的规则表与 MD-*） | 指代约束正文 |
| 校验 | check | 自动化检查：运行 `check.py`、`check.sh` 或测试 | 机检、检查（指自动化工具时） |
| 校验脚本 | checker | `scripts/check.sh`（全量校验）；`skills/system-prompt-authoring/scripts/check.py`（Markdown 校验器） | 检查器、检查脚本、机检脚本 |
| 验证 | verification | 交付前运行命令、贴真实输出、人工核对 | 单次格式校验 |
| 审查 | review / audit | 对代码、文档、请求、方案的人工审查；`Review Checklist` 写「审查清单」 | 审计（指人工审查时）、评审 |
| 审计 | technical audit | 技术审计：审计日志、审计列、审计动作、审计轨迹 | 审查（指技术审计时） |
| 检查 | inspect | 人工阅读、核对具体内容，不指自动化工具 | |
| 第三方引入代码 / 第三方引入文档 | vendored code / vendored documentation | 随仓库引入并保留上游来源的代码或文档；首次写全称，之后可写「引入代码」 | vendored 代码、vendor 代码、内置第三方 |
| 包仓库 | package registry | npm、PyPI、crates.io 等包的注册与分发服务 | 注册表 |
| 运行手册 | runbook | 事故或运维的逐步处置文件 | 操作手册（指 runbook 时） |
| 操作手册 | playbook | 按场景组织的操作步骤文件 | 操作清单 |
| 事故复盘 | postmortem | 事故后的事实与改进记录 | 事后复盘、复盘（单独使用时） |
| 权威来源 | canonical source | 事实的唯一权威页面或名称来源 | 规范来源（canonical） |
| 规范名称 | canonical name | 命名表选定的名称 | 标准名称 |
| 制品 | artifact | 构建或发布产生的文件 | 产物（指构建/发布产物时） |
| 产物 | output | 生成结果、构建缓存等非发布物 | 制品（指普通输出时） |
| 销毁性 | destructive | 会删除或不可逆破坏数据的操作或变更 | 破坏性（destructive） |
| 破坏性 | breaking | 破坏兼容性的变更 | 销毁性（breaking） |
| 生命周期 | lifecycle | S0–S6 的阶段、门禁与迭代闭环，由 `project-lifecycle-governance` 裁定 | 流程、项目流程 |
| 阶段门 | gate | G0–G6 的决策点，只判断证据是否足以进入下一阶段 | 里程碑（指门禁时）、关卡 |
| 风险级别 | risk tier | R0/R1/R2，决定门禁裁剪、工件厚度与批准权限 | 优先级（指风险时） |
| 就绪定义 / 完成定义 | DoR / DoD | 条目进入迭代与增量完成时必须满足的条件 | 完成标准（指 DoD 时） |
| 系统提示 | system prompt | 交给模型的整体指令文本 | 系统指令、指代具体指令文件 |
| 指令文件 | instruction file | `AGENTS.md`、`CLAUDE.md`、`QWEN.md` 等承载持久指令的文件 | 与系统提示混用 |
| 插件 | plugin | 用户级安装包：Qoder 插件、Qwen 扩展、DSH bundle | 扩展、bundle（指具体包时） |
| 组件 | component | 插件内的 skills、commands、hooks 等 | |
| 宿主 | host | 加载插件与规则的 Qoder 客户端 | |
| 打包 | package | 生成 zip | |
| 组装 | assemble | 从顶层真源复制生成开发入口或安装包；生成物不提交 | 物化 |
| 开发入口 | dev entry | `scripts/assemble.sh` 生成的 `.dsh`、`.qoder`、`.qwen` 副本 | |
| 分发 | distribute | 通过市场或内网分发 | |
| 变更日志 | changelog | `CHANGELOG.md` | 更新日志 |

英文技术名保持原样（如 skill、hook、manifest、zip、payload、Markdown、JSON）。
`global-user-constraints` 与 Global User Constraints 是插件标识和英文名，中文一律写「全局用户约束」。

## 翻译与写作口径

本仓库规范与 skill 正文统一用中文写作，英文仅保留在不可翻译对象（代码、标识符、工具名等）中。

| 英文 | 中文 | 用法 |
|---|---|---|
| MUST | 必须 | 绝对要求，违反即任务失败 |
| MUST NOT | 禁止/不得 | 绝对禁止；不得与禁止同义 |
| SHOULD | 应当 | 默认行为，偏离要说明理由 |
| MAY | 可以 | 允许的行为 |

- 不译：代码、标识符、文件路径、命令、URL、协议与格式名、宿主概念名（skill、hook、plugin、manifest、rules）、条款编号（SP-1、ME-6 等）、skill 名与目录名。
- skill 名称写英文标识符（如 `naming-conventions`），首次出现可在括号内给中文描述；不写「命名规范 skill」这类中文名。
- 「评审」不用，统一写「审查」；技术审计写「审计」。
- 标题、表格与示例说明译成中文；代码块内不译。
- 同一术语全仓只用一种写法；首次出现可在括号内加英文。
- 行宽：正文每行不超过 200 字符（约 100 个汉字宽；表格、代码块与 URL 不受限）。
- 规范正文只有中文一份，仓库不维护英文译本。
