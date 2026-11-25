# 提示词与纯规则清单

本文件是全仓提示词与纯规则的分类台账与迁移方案。维护者：SnowCore8。阅读时机：修改 rules、skill、命令、插件注入或仓库文档前。

## 分类

| 类别 | 含义 | 消费者 |
|---|---|---|
| P | 提示词：运行时进入模型上下文的内容 | 模型 |
| R | 纯规则：维护者、CI 或人类阅读，不自动进入模型上下文 | 人类/CI |
| H | 混合：同一文件或段落既被模型加载，又承载人类流程 | 两者 |
| C | 代码、脚本、测试、CI、宿主插件源码 | 运行时/CI |
| M | 清单、许可证、变更日志、第三方声明等元数据 | 宿主/平台/人类 |

## 台账

| 路径 | 类别 | 加载者或消费者 | 结论 |
|---|---|---|---|
| `rules/global-user-constraints.md` | P | DSH systemPrompt；Qoder/Qwen rules 与 hook；命令按需读取 | 常驻约束唯一真源 |
| `AGENTS.md` | P | DSH/Qwen/Qoder 项目指令 | 已拆分：只放代理项目指令 |
| `CONTRIBUTING.md` | R | 人类贡献者与维护者 | 已拆分：不进入模型上下文 |
| `skills/*/SKILL.md` | P（主要 H 已拆） | 三端 skill 发现；正文按需加载 | 3 个混合段已移除；`system-prompt-authoring` 保留项目文档指针 |
| `skills/*/references/*.md` | P（2 个 R；迁移头已精简） | skill 按需读取 | 主体是 P；`constraint-maintenance.md`、`provenance.md` 标为维护者资料；迁移头仅保留编号来源；`check-rules.md` 仍 H |
| `shared/commands/constraints-check.md` | P | Qoder/Qwen 命令；DSH 未注册 | 命令提示词 |
| `shared/scripts/*.py` | C | Qoder/Qwen hook | 提示词发射器，不是提示词正文 |
| `plugins/dsh/src/index.js`、hooks | C | 宿主运行时 | 注入与 skill 提供者 |
| `docs/*` | R | 维护者 | 不注入、不随包 |
| `README.md`、`GOVERNANCE.md`、`SECURITY.md`、`GLOSSARY.md`、`CHANGELOG.md` | R | 人类/GitHub/npm | 不自动加载 |
| `scripts/`、`tests/`、`.github/` | C | CI/维护者 | 不进入上下文、不随包 |
| `package.json`、三包清单、`plugins/marketplace.json` | M/C | npm、宿主、市场 | 清单 description 面向人类/UI，不是提示词 |
| 许可证、第三方声明 | M | 人类/平台 | 分发元数据 |

## 错位与风险

1. **AGENTS/CONTRIBUTING 已拆分。** 根 `AGENTS.md` 现为真实文件，只放代理项目指令；`CONTRIBUTING.md` 只面向人类，不进入模型上下文。
2. **通用 skill 夹带本仓库流程（已拆）。** `skill-authoring` 的打包、三端软链、计数与 zip/npm 检查已移除；`system-prompt-authoring` 的 32 KiB、`check.sh`、脚本测试命令已泛化，来源表移入 `provenance.md`。
3. **references 维护材料（已清理）。** `constraint-maintenance.md`、`provenance.md` 标为维护者资料；
   `skill-authoring/references/checklist.md` 已删除，发布/新增 skill 清单移入 `CONTRIBUTING.md`；
   六个迁移头精简为编号来源说明；`system-prompt-authoring/references/check-rules.md` 仍混有脚本文档。
4. **仓库事实已泛化。** `documentation-conventions` 与 `change-records.md` 已改为通用表述，不再陈述本仓库软链或 CHANGELOG 事实。
5. **描述职责重叠（部分处理）。** `skill-authoring` 已收窄；`repository-governance` 的“分支/发布政策”与 `naming-conventions` 的“提交”仍待收窄。
6. **重复与漂移。** `docs/time-awareness.md` 复制注入文本；发布流程在 README、CONTRIBUTING、GOVERNANCE 与 `docs/release.md` 各有一份。`CONTRIBUTING` 输出段与 Qoder README 体积已修。
7. **入口差异。** Qoder 插件 `rules/` 当前不被 CLI 加载；DSH 未注册 `constraints-check` 命令；DSH/Qoder/Qwen 对 frontmatter 的处理不一致。

## 目标结构

- `AGENTS.md`：真实文件，只放代理每次都要遵守的短规则；不再软链到 CONTRIBUTING。
- `CONTRIBUTING.md`：仅人类贡献、发布、检出流程；删除与全局约束重复的输出段。
- `rules/`：保持单一常驻约束真源；不新增第二个会被 Qwen/Qoder 自动加载的 `.md`。
- `skills/`：SKILL.md 与 references 只放模型规范；维护者流程移至 `docs/` 或 CONTRIBUTING。
- `docs/`：维护者材料、调研、发布 runbook 与分类台账；不得被包分发。
- `shared/`：命令提示词（P）与注入脚本（C）分离。
- `tests/`、`scripts/`、`.github/`：C，保持不进入上下文。

## 迁移批次

1. **文档与重复（进行中）**：已修 Qoder README 体积与 `CONTRIBUTING` 输出段；仍待处理 `docs/time-awareness.md` 副本、发布流程重复与 DSH 命令缺失说明。
2. **skill 错位（大部分完成）**：已拆 `skill-authoring` 与 `system-prompt-authoring` 的仓库流程；已删 `checklist.md`、泛化 documentation 与迁移头；剩余 `check-rules.md` 与 2 个 description。
3. **AGENTS/CONTRIBUTING 拆分（已完成）**：`AGENTS.md` 为真实代理指令，`CONTRIBUTING.md` 为人类文档；`check.sh`、README 与 docs 已同步。
