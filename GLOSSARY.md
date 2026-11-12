# 术语表

本仓库的术语与写法约定。改文档、注释或校验输出前先读本表；维护者：仓库所有者。

| 术语 | 英文 | 用法 | 不要写成 |
|---|---|---|---|
| 用户全局约束 | Global User Constraints（插件名） | `rules/global-user-constraints.md` 的正文与整体 | 全局用户约束、约束规则、全局规则 |
| 约束正文 | constraint text | 该文件的内容 | 规则正文 |
| 约束条款 | constraint clause | 正文中的单条编号要求（SP-1 等） | 规则条款 |
| 约束文件 | constraints file | 承载用户全局约束的文件 | 规则文件 |
| 规则 | rule | 宿主 rules 机制（规则目录、规则激活），以及 skill 的内容与格式规则（S1–S13、MD-*） | 指代约束正文 |
| 校验 | check | 运行 `check.py`、`check.sh` 或测试 | 机检、检查（指自动化工具时） |
| 校验脚本 | checker | `check.py` | 检查器、检查脚本、机检脚本 |
| 验证 | verification | 交付前运行命令、贴真实输出、人工核对 | 单次格式校验 |
| 审查 | audit | 按用户全局约束人工审查请求或方案 | 审计 |
| 检查 | inspect | 阅读、核对具体内容，不指自动化工具 | |
| 系统提示 | system prompt | 交给模型的整体指令文本 | 系统指令、指代具体指令文件 |
| 指令文件 | instruction file | `AGENTS.md`、`CLAUDE.md`、`QWEN.md` 等承载持久指令的文件 | 与系统提示混用 |
| 插件 | plugin | 用户级 Qoder 插件包 | |
| 组件 | component | 插件内的 skills、commands、hooks 等 | |
| 宿主 | host | 加载插件与规则的 Qoder 客户端 | |
| 打包 | package | 生成 zip | |
| 分发 | distribute | 通过市场或内网分发 | |
| 软链 | symlink | 指向另一路径的链接 | 符号链接 |
| 变更日志 | changelog | `CHANGELOG.md` | 更新日志 |

英文技术名保持原样（如 skill、hook、manifest、zip、payload、Markdown、JSON）。
`global-user-constraints` 与 Global User Constraints 是插件标识和英文名，中文一律写「用户全局约束」，不按英文语序回译。
