# 变更日志

按版本从新到旧记录可观察变更。自 0.2.0 起版本采用 SemVer、发布点为 tag `v<version>`，每节记录一个发布版本；0.2.0 之前按日期记录。条目按主题合并，记录最终可观察状态；被后续提交推翻的中间状态只在修复项里说明。

## 0.46.0（2026-11-27）

**新增**

- 新增 `@snowcore8/qwen-global-user-constraints` npm 包，承载 Qwen Code 扩展 zip 与校验和；`release` 工作流
  统一发布 DSH bundle、Qoder zip 与 Qwen zip 三个 npm 包。

**变更**

- 说明性文档只保留当前状态：删除来源对照、取证日期、版本基线与历史措辞；`AGENTS.md` 增加「说明性文档必须
  保持干净」的项目规则。
- `scripts/check.sh` 与 `release` 工作流按三个 npm 包校验并发布。

## 0.45.3（2026-11-27）

**修复**

- Qoder 去重候选在缺少 `payload.cwd` 时回退 `QODER_PROJECT_DIR`，项目 `AGENTS.md` 与 `.qoder/rules`
  不再漏查。
- `check.sh` 校验 `hooks.json` 引用的 `${QODER_PLUGIN_ROOT}` 脚本存在；`dist.sh` 的 zip 结构校验要求
  三个注入脚本进包。
- 文档修正：marketplace 需添加 `plugins/` 目录；压缩后时间实为时间戳与时区两行。

**新增**

- 新增 `@snowcore8/qoder-global-user-constraints` npm 包，随 release 发布 Qoder 插件 zip 与校验和，
  可用 jsdelivr 直链安装。

## 0.45.2（2026-11-27）

**修复**

- 修复 JavaScript 迁移后 Qoder `SessionStart` 约束注入失效：恢复显式根/环境变量解析、`resume` 跳过、
  同内容去重与缺失/超限提示。
- 修正 Qwen `contextFileName` 读取时机：启动/刷新读取一次并缓存，随后每个请求随 system prompt 携带；
  Qwen 无插件数据目录时时间状态按无状态输出（turn 1、elapsed unavailable）。
- hook 统一使用 `hookSpecificOutput` 输出，异常静默退出 0，不再用 `process.exit` 截断 stdout。

**变更**

- 共享 hook 拆分为 `shared/scripts/lib/` 模块；Qoder 去重候选收敛为 Qoder 路径；时间状态只认
  `QODER_PLUGIN_DATA`。
- DSH 插件拆分为 constraints、skills、paths 等模块，section 与 skill provider 行为不变。
- 新增 `docs/hooks-and-injection.md`；清理过时设计稿与文档中的 hook/注入、时间、发布事实。

## 0.45.1（2026-11-27）

**修复**

- 修复 0.45.0 发布错误：首次发布触发 npm publish 后 amend 提交导致版本冲突，升版为 0.45.1 重新发布。
- CHANGELOG.md 格式修正：首个标题改为 h1（`# 变更日志`），标题层级连续。

## 0.45.0（2026-11-27）

**变更**

- **JavaScript 统一**：4 个 Python hook 脚本迁移为 Node.js ESM 模块，统一三包脚本语言
- **干净卸载**：移除 `install-constraints.js`，Qoder 改用 hook 注入，Qwen 添加 `contextFileName` 原生加载，三包卸载后无残留；
  从 0.44.0 及更早版本升级需手动删除 `~/.qoder-cn/rules/global-user-constraints.md` 与
  `~/.qoder/rules/global-user-constraints.md`（Windows 为 `%USERPROFILE%\.qoder-cn\rules\` 与 `%USERPROFILE%\.qoder\rules\`）
- **Qwen 字段补全**：扩展清单添加 `author`、`license`、`repository` 字段
- **测试迁移**：Python unittest 迁移为 Node.js test runner，18 个测试用例
- **文档更新**：新增 `docs/restructure-design.md`，更新 `docs/time-awareness.md`

---

## 0.44.0（2026-11-27）

**变更**

- 重写 ME-13：tree 与 goal 分别负责多步计划与跨轮目标；任务类工具由智能体主动建立、更新、推进与收尾，删除非平台强制的逐次确认，并补齐主代理/子代理、多 tree、paused、blocked 与 timeline_pull 边界。
- 新增 ME-17：goal、Timeline tree、todo、team task 的建立、分配、依赖、状态、进度与收尾由智能体自主负责；用户只决定目标、范围、验收与不可逆授权。
- 全仓收敛 6 处过度安全门槛：debugging 报告不完整时先做不修改代码与数据的调查；performance 无目标时先测量并提出
  标注假设的暂定目标，已达标路径支持用户要求或降风险/维护性例外；prompt-authoring 的本地可逆写直接执行。
- release 的本地标签创建与未公开删除在已批准发布内执行；system-prompt-authoring 仅对范围、授权与安全边界强制提问。

**修复**

- 三包版本升到 `0.44.0`。

## 0.43.0（2026-11-27）

**变更**

- 新增全局规则 ME-16：智能体团队只分为领导者智能体与协作者智能体；领导者统一管理全部工作树的创建、分配、基线更新、集成、恢复与清理，协作者只在其分配的工作树内写入。
- 工作树删除、强制移除与未跟踪内容清理显式引用 AU-1、IR-1、IR-3、IR-6；共享或保护分支推送引用 AU-1。

**修复**

- 三包版本升到 `0.43.0`。

## 0.42.0（2026-11-27）

**变更**

- 新增第二十个 skill `worktree-collaboration-conventions`：智能体团队分为领导者智能体与协作者智能体；领导者统一管理工作树创建、分配、集成、恢复与清理，协作者只在分配的工作树内写入；覆盖隔离环境、集成队列、Windows/Linux 与安全边界。
- 全仓库表示 AI agent 的“代理”统一改为“智能体”，覆盖规则、20 个 skill、文档、插件、脚本与测试。

**修复**

- 三包版本升到 `0.42.0`。

## 0.41.0（2026-11-27）

**变更**

- 约束正文硬上限从 32 KiB 提升到 40 KiB（40,960 字节）；新增 ME-15 提示词核对，要求提示词、规则与 skill 正文写完后核对逻辑、规则与语义。
- 新增第十九个 skill `project-structure-conventions`，承接项目目录、包/工作区边界、物理导入与构建依赖图；`architecture-and-design-conventions` 与 `code-style-conventions` 的边界同步收紧。
- Qoder 插件首次 `SessionStart` 把约束写入用户级 rules，内容不同直接覆盖；不再由 hook 注入全文，卸载需手动删除。
- Qoder `UserPromptSubmit` 保留 `Never violate global user constraints.` 与 DSH 风格时间块；`PreToolUse`/`PostToolUse`/`PostToolUseFailure` 注入一行时间；`SessionStart(source=compact)` 补约束与压缩后时间；`SessionEnd` 清理时间状态。
- 时间提示对齐 DSH 的 turn、浏览器时区解释与 elapsed；Qoder 无 step 字段，不输出恒为 1 的 step。Windows 无 tzdata 时回退系统时区，Linux 优先 IANA。

**修复**

- 三包版本升到 `0.41.0`。

## 0.40.0（2026-11-26）

**变更**

- 第 1 节新增加粗红线：绝不违反全局用户约束；违反必须、禁止或不得条款的，任务即告失败。
- 中文术语由「用户全局约束」统一为「全局用户约束」；规则、skill、插件描述、hooks、shared 脚本与文档同步更新，历史条目保留原文。

**修复**

- 三包版本升到 `0.40.0`。

## 0.39.0（2026-11-25）

**变更**

- 新增 ME-14 行动前说明：每次发起工具调用前，用一句不超过 30 个汉字的话说明动作与对象；该句不得写入思考内容，同一轮并行调用时一句覆盖整批。
- ME-10 的 skill 加载顺序细节移至 `skill-authoring/references/skill-load-order.md`，规则正文保留触发条件、全部 skill 名单与授权提示。
- performance 与 repository-governance 的重复表述收敛到同一 skill 的 `SKILL.md` 核心规则；核心规则与安全细节不变。

**修复**

- 对齐 OUT-5 与 ME-14：执行期自述不受最终正文预算约束，但发起工具调用前的动作说明依 ME-14。
- 三包版本升到 `0.39.0`。

## 0.38.0（2026-11-25）

**变更**

- ME-8 要求工具调用严格匹配 schema 的字段名、类型、必填项与枚举值；参数错误先修正，不得绕过。

**修复**

- 三包版本升到 `0.38.0`。

## 0.37.0（2026-11-25）

**变更**

- CH-2 严禁提示词、规则、skill 正文与代码注释写记录性措辞；来源、迁移与状态历史只进 CHANGELOG、提交消息或 PR。
- 历史措辞门禁覆盖提示词、规则、skill 与代码注释，新增 was/now、formerly、FIXED、日期条目、原编号等检查。
- 删除 `docs/system-prompt-maintenance.md` 与 `docs/system-prompt-sources.md`，并清理 SKILL、内容地图与分类清单中的引用。
- 自测中的帮助与参数错误输出改为捕获，`check.sh` 日志不再出现伪报错。

**修复**

- 三包版本升到 `0.37.0`。

## 0.36.0（2026-11-25）

**变更**

- 语义不变重写 global 约束与 18 个 `SKILL.md`；保留条款编号、阈值、示例与行为。
- 拆分 `AGENTS.md` 与 `CONTRIBUTING.md`：前者只承载智能体项目指令，后者仅人类流程。
- 取消 64 个分发软链，新增 `scripts/assemble.sh` 与显式 `materialize` 组装；`check.sh` 校验零软链、开发入口与组装包。
- 拆分 `skill-authoring`、`system-prompt-authoring`、`documentation-conventions` 及 references 的维护者内容；新增内容结构地图与 Qoder 本地市场组装。
- 清洗 README 与根文档，统一“组装”术语。

**修复**

- 修正逐项核对发现的 API 版本边界、ADR 归属、命名表定义重复、vcs 历史修复审批、system-prompt 审查清单、跨 skill 重复与单一权威问题。
- 三包版本升到 `0.36.0`。

## 0.35.0（2026-11-25）

**变更**

- 将多步阈值统一为超过四步：先建 timeline_tree，无 Timeline 时用 todo list，再列子任务。
- goal 仅用于跨自动续轮的长任务；多步时目标写明对应子项，不替代顶层 tree；单步长任务也先建单项 todo
  list 再建 goal。
- 保留选项卡等待与禁止自动续轮、goal 恢复路径与 `timeline_pull` 收尾检查。

**修复**

- 三包版本升到 `0.35.0`。

## 0.34.0（2026-11-25）

**变更**

- 恢复 ME-13：存在 goal 工具时，每个任务开始前必须先 create_goal，并明确本条优先于工具描述中的 single-turn 限制。
- 新增选择协议：需要用户选择时，先建 goal，再发 ask_user_question 选项卡，发完停止等待，禁止自动续轮。
- 保留多步任务复用 active tree、goal/tree 边界与 goal 恢复路径；4.10 与第 5 节压缩以保持在 32 KiB 内。

**修复**

- 三包版本升到 `0.34.0`。

## 0.33.0（2026-11-24）

**变更**

- 将 ME-13 从“所有任务开始前先建 goal”改为按工作形态选择：单轮简单不建；单轮多步建 tree；跨轮建 goal，
  跨轮多步再建 tree；明确 goal 管连续性、tree 管分解且不绑定 goal。
- 补充 goal 恢复路径：改前先 `get_goal`，paused 由用户恢复，封顶先 `edit` 再 `resume`；收尾前 `timeline_pull`。
- 4.10 摘要与第 5 节压缩为要点与 references 指针，以保持在 32 KiB 内；约束正文 32,696 字节。

**修复**

- 三包版本升到 `0.33.0`。

## 0.32.0（2026-11-24）

**变更**

- 新增 ME-13：存在 goal 工具时，任务开始前必须先调用该工具立目标；不存在时说明缺口。
- 压缩 4.7 迁移注为紧凑映射，保留 CH-1/7/11、CH-4、CH-5/6、CH-8、CH-9/10 的 skill 归属；约束正文
  32,712 字节，仍在 32 KiB 内。
- 全文语义与迁移引用经独立复核，无阻断问题。

**修复**

- 三包版本升到 `0.32.0`。

## 0.31.0（2026-11-24）

**变更**

- 新增 ME-12：新方案失败时至少试 3 个实现版本，每版先定位根因、不得叠加补丁；3 版均无效且根因有证据，
  才可判定该方案不可行；未定位根因不得断言不可行。
- 调试 skill 的根因治理 reference 补充 ME-12 与 CH-4 的关系：3 个版本应针对不同根因假设或实现路径，
  不得做成 3 次叠补丁。
- 约束正文 32,717 字节，仍在 32 KiB 硬上限内；全文语义与迁移引用已由独立审查复核。

**修复**

- 三包版本升到 `0.31.0`。

## 0.30.0（2026-11-24）

**变更**

- 用户全局约束正文加入 32 KiB（32,768 UTF-8 字节）硬上限；超过时按主题把规则提取到对应 skill 的
  `references/`，正文只保留摘要与加载指引。
- 约束正文由 43,665 字节降至 32,553 字节：收录原则、制定理由、适用限制、示例与依据迁入
  `system-prompt-authoring`；CH-1、CH-4 至 CH-11 按主题迁入 debugging、architecture、refactoring、
  testing 与 documentation；OUT-1 至 OUT-10 迁入 `prompt-authoring`。
- `scripts/check.sh`、Qoder/Qwen 注入脚本与 DSH systemPrompt 注入统一执行 32 KiB 检查；超限时不注入全文，
  提示读取 `rules/global-user-constraints.md`。

**修复**

- 三包版本升到 `0.30.0`。

## 0.29.0（2026-11-24）

**变更**

- 新增 IN-8：用户说“不需要 X”时，不得直接删除、停用或改写 X；先区分“不需要等待或关注”与“移除”，
  列出理解并确认。
- 新增 IN-9：消息没有可识别对象、与当前任务无关或疑似发往其他会话时，先问清指代；确认前不检索、不推断、
  不执行。
- §2 明确仓库特定的发布、打包、目录与工具流程写入项目文档或对应 skill，不得写入全局约束。

**修复**

- 约束注入脚本在规则文件缺失或读取失败时显式提示“未注入”，不再静默返回。
- 三包版本升到 `0.29.0`。

## 0.28.0（2026-11-23）

**变更**

- 新增 HO-7：不得擅自降级或变更目标。降低验收标准、缩小范围、简化实现、跳过步骤或替换目标，须先说明
  原目标、拟降级内容、影响与替代方案并取得明确同意；无法达成原目标的，报告障碍与可选方案，不得改用较低
  目标或冒充完成。

**修复**

- 三包版本升到 `0.28.0`。

## 0.27.1（2026-11-23）

**变更**

- OUT-5 明确执行期间可以逐步自述：说明动作、命令目的、中间发现与下一步；此类自述不限长度与频率，也不
  构成需要删减的废话。
- ME-7 去掉提交前说明“只能一行”的限制。

**修复**

- 三包版本升到 `0.27.1`。

## 0.27.0（2026-11-23）

**变更**

- 放宽范围刹车：为完成点名行为所必需、不修改则请求无法成立或测试无法通过的调用点、测试与配置同步纳入
  范围；上下文明确可推定的对象，说明依据后即可开工，只有新增模块、环境或外部对象等待确认。
- 新增 IN-7：不得猜测意图；输入存在错字、粘贴错误、中断、缺关键对象或意图多解时，指出可疑之处并列出
  实际存在的不同理解，由用户选择；IN-7 优先于第 4.5 节其他条款。
- 允许顺手修复任务中发现的小问题：限于不改变接口、契约、配置键、依赖与数据，且无需新依赖或迁移的问题；
  单独提交并在交付中一行说明。

**修复**

- 统一“不同理解”表述，不再要求两种以上；IR-7 明确引用 AU-1 第 3 级同意。
- 三包版本升到 `0.27.0`。

## 0.26.0（2026-11-23）

**变更**

- 授权不再扩张：明确同意仅覆盖点名的行为与对象，范围内实现细节不需另问；新增对象、文件或环境依 AU-4 取得
  同意。交付验收不再以沉默推定。
- 同层强制规则冲突改为报告用户裁决，非强制项目约定冲突由智能体说明并记录；并发不可变、ADR 状态、外部消费方、
  JSON 标识符、PostgreSQL 语法与泄露轮换时点同步统一。

**修复**

- 删除“已记录无法补充测试”等自证例外；仅修症状、无测试重构的例外须一次明确同意；SP-4 与公开分发对齐，
  IR-6 清理范围限于任务自身产物，ME-7 允许一行说明提交拆分。
- 发布手册改为 0.x 破坏性变更递增 minor，并移除历史叙述；审查命令补第 2 级授权与范围扩张检查。
- 三包版本升到 `0.26.0`。

## 0.25.2（2026-11-23）

**变更**

- 将 AU-1/AU-2 改为三级授权：任务级预授权覆盖请求范围内的本地读取、编辑、测试、构建与提交；计划级确认
  覆盖非保护分支推送、PR/MR、依赖安装与测试环境操作；逐次明确同意保留给受保护分支推送、强推、远端历史、
  远端标签与 Release、生产发布/部署/回滚与凭据轮换等不可逆动作。
- 明确目标授权：一个明确的发布目标覆盖该版本的 tag、推送、发布与部署链，不覆盖后续版本、其他环境或其他
  对象；SP-3、AU-4、IR-3/IR-4 的独立门禁不变。
- VCS 同步 amend、主题分支推送、强制推送与分支删除的分级。

**修复**

- 三包版本升到 `0.25.2`。

## 0.25.1（2026-11-23）

**修复**

- OUT-5 将简洁性约束限定于最终正文：智能体自身的执行过程、工具调用、命令前后的简短描述与中间记录不属于
  该条范围；最终正文仍禁止逐项复述工具输出与按编辑顺序罗列改动。
- 三包版本升到 `0.25.1`。

## 0.25.0（2026-11-23）

**破坏性变更**

- 移除模型角色与人格提示：`prompt-authoring` 不再提供“角色与人格”类型，`system-prompt-authoring` 不再要求
  角色设定，模板与来源引用同步删除；组织角色（安全、事故指挥、维护者）保留。依赖旧角色或人格行为的项目应
  固定 0.24.0。

**变更**

- 将 `code-style-conventions` 的维度文件拆分为 `dimensions.md`（维度 1-4）与 `dimensions-errors.md`
  （维度 5-6），满足单文件 300 行上限；SKILL 索引与参考资料同步。
- 三包版本升到 `0.25.0`。

**修复**

- 闭合用户全局约束的形式逻辑：定义“不得/明确同意/用户文件/归档/共享事实”，合并效力顺序，修正完成与失败
  判定、删除与归档、测试豁免、发布与凭据轮换的授权，以及跨平台清理边界。
- 修复各 skill 的逻辑矛盾：API 分页/错误/重试/schema 迁移，架构依赖/例外/ADR，代码风格 formatter/
  ShellCheck/日志超时，性能阈值/环境，并发多锁/超时，文档生成/删除/变更日志，命名与术语所有权，测试门禁/
  豁免/不稳定测试，发布矩阵/回滚/演练，仓库产物/依赖分级，安全披露/门禁，VCS 决策树，重构条件。
- 修复两处断链、审查命令覆盖、必需文件 skill 边界、角色与人格删除后的元规范引用，以及 code-style 维度拆分
  后的索引。

## 0.24.0（2026-11-22）

**变更**

- 全部面向语言模型的提示词统一改写为现代汉语法典体：覆盖用户全局约束、十八个 skill 的 `SKILL.md` 与
  `references/`、项目维护约定与审查命令；保留条款编号、章节结构、阈值、链接、表格与示例。
- `shared/scripts` 的时钟与约束头注入文案同步改为法典体。
- 三包版本升到 `0.24.0`。

**修复**

- 校对修正改写引入的语法、指代与术语问题；统一“用户全局约束”“审查”“系统提示”“发布制品”等写法与
  引号样式。

## 0.23.0（2026-11-21）

**变更**

- 整篇重写用户全局约束：改成第二人称短句，删掉模板化理由、学术式章节与重复；保留全部
  73 个条款编号、交叉引用与规则语义。
- OUT-5 增加反水字数要求：禁止复述请求、背景铺垫、正确的废话、模板化结构和拆句凑长度。
- 三包版本升到 `0.23.0`。

## 0.22.0（2026-11-21）

**新增**

- OUT-10 补充直接批评：对明显不好的方案、代码、结论或请求直接指出并批评，不粉饰；批评必须指向
  具体问题、给出理由与影响，不得人身攻击或用情绪代替证据。
- 三包版本升到 `0.22.0`。

## 0.21.0（2026-11-21）

**破坏性变更**

- 移除随包人格：删除 `rules/persona.md`，DSH 不再注册人格 `systemPrompt.section`，Qoder/Qwen 的
  `SessionStart` hook 不再注入人格。用户全局约束的注入、去重与顺序保持不变；需要旧人格行为的
  用户应停留在 `0.20.x`。
- 三包版本升到 `0.21.0`。

## 0.20.1（2026-11-19）

**修复**

- `rules/persona.md` 补 Qoder 规则 front matter（`name`、`description`、`trigger: always_on`、
  `alwaysApply: true`），与约束正文一致；缺表头时不同工具按各自默认值处理，无法显式声明始终生效。
- 三包版本升到 `0.20.1`。

## 0.20.0（2026-11-19）

**新增**

- 新增随包人格 `rules/persona.md`（大肥鱼 / 鲸鱼娘二创形象）：DSH 通过独立 `systemPrompt.section`
  注入，排在用户全局约束之前；Qoder/Qwen 的 `SessionStart` hook 同时注入约束与人格，分别按
  sha256 去重。
- 人格称呼用户「哥哥」，默认短答、先结论、带情绪与「白饭 = Token」比喻；身份被问时说明社区
  二创来源、官方形象为蓝鲸 Logo。
- 三包版本升到 `0.20.0`。

## 0.19.0（2026-11-18）

**修复**

- 划清事实判断与偏好表达：OUT-7 只约束事实判断，OUT-10 的表达偏好不得冒充事实、不改变 §3.3 的
  效力顺序；信息不足时按 UN-4 说明不确定，不猜测，OUT-6 的标注不算模糊措辞。
- IR-7 改为“未经 AU-1 的明确同意，禁止改写已发布历史”，并补上理由，消除与 AU-1/IR-3 的
  绝对禁止与同意路径矛盾。
- 表 1 增加“同时要求解释与变更、但未给出顺序”的分类；ME-9 明确为在内部规划调用；IN-6 与
  OUT-6 统一解释数量口径（超过四个时合并同类项）。
- OUT-10 的“决策权不相同”改为“权限不相同”，明确对话地位平等不等于授权相同。
- 三包版本升到 `0.19.0`。

## 0.18.0（2026-11-18）

**变更**

- 任务跟踪规则 ME-6 新增：平台同时提供时间线与待办列表时，优先用时间线工具跟踪；同一任务不再维护
  两套列表。
- 三包版本升到 `0.18.0`。

## 0.17.0（2026-11-18）

**破坏性变更**

- 效力层级改为「宿主系统消息 > 全局规则 > 已加载 skill 的规则 > 项目约定与事实 > 个人偏好」。18 个
  skill 的「适用范围与优先级」及 references 中的“项目约定优先”表述统一到该层级；项目约定只在 skill
  未规定时补充，现有契约、架构、流水线、配置作为事实输入，不能覆盖 skill。
- 红线改为「用户可容忍范围的边界」；完成/失败与交付/验收拆成两个轴：完成可与待验收并存，失败即使
  已验收仍是失败；交付后未反驳或补充即视为验收通过，但不构成对后续动作的授权。

**变更**

- 约束正文补齐完成定义中的“合规”、SP-4 的仓库维护/发布边界、IR-6 对 IR-2/SP-6 的引用、AU-1 的任务
  产物例外、OUT-5 的逐项披露例外、ME-10 的授权表述。
- 并发规范把竞态检测器限定到有运行期检测器的语言，Java/Python 改用压力测试、静态分析与审查；条件
  变量超时对 Go `sync.Cond` 等不支持超时的原语给出例外。
- 调试流程改为先写回归测试并跑红，再最小修复、跑绿；无法自动化时用可复现步骤替代。
- API/数据规范分开“影响评估默认破坏性”与“实施默认增量”；索引要求统一为热过滤/排序必须有索引，
  其余记录接受成本；废弃窗口交给 `release-operations-conventions`。
- 重构判定改为测试绿只是必要条件，还需核对可观察行为；推理模型温度按平台设置；行宽、注释例外、
  测试文件命名、日志级别、单维护者例外、双许可与仓库布局归属统一。
- 机器契约与文档：Python 下限改为 3.9+；发布 SHA256 命令按包名；250 行按正文计数；`argument-hint`
  必填；skill 模板补维度索引；新增跨 references 去重测试；provider 断言字面 18；Qwen 审查路径补
  `.qwen/rules`/`constraints`；DSH 文档与 package description 与实际注入对齐。
- `dist.sh` 只保留最新 zip 与校验和，构建新版本时删除同包旧制品。
- 三包版本升到 `0.17.0`。

## 0.16.0（2026-11-17）

**新增**

- 约束正文 3.4 新增「验收标准是合规，不是完成」：用户不在意智能体能否完成任务，只在意智能体是否违反
  本文条款；未违规的未完成按未完成如实报告，违规即使产出了可用结果也按失败处理。
- 三包版本升到 `0.16.0`。

## 0.15.0（2026-11-17）

**新增**

- 约束正文新增 ME-11（复用优先）：实现任何功能前依次检查标准库、现有依赖与维护良好的第三方库；
  任一项能胜任时禁止手写替代实现。依赖准入仍核验维护状况、已知漏洞、许可证兼容性与移除路径，但
  费用、安装体积与传递依赖数量不再构成拒绝优质库的理由；自研时在交付中说明缺少可复用实现的原因。
- 约束正文新增 CH-11（替换即清理）：替换实现、接口、配置键或依赖时，同一变更删除被替换的实现、
  调用点、开关与兼容层，禁止新旧实现长期并存；确需迁移窗口时记录移除条件与期限并在窗口结束后清理，
  无法当场清理的残留列出位置、风险与移除路径。
- `refactoring-conventions` 同步替换与复核流程：核心规则、复核步骤、反模式与审查清单补「替换后删除
  旧实现」的判定与证据要求。

**变更**

- ME-10 改为只要求按需加载：删除「禁止预先批量装载」，保留按任务实际触及的方面逐步加载与「加载
  skill 不等于授权变更」的边界。
- `code-style-conventions` 的依赖准入与预算改为复用优先：标准库、现有依赖或维护良好的第三方库能
  胜任时不写替代实现，安装大小与传递依赖数量如实记录，但不构成拒绝优质库的理由。
- 三包版本升到 `0.15.0`。

## 0.14.0（2026-11-15）

**新增**

- 约束正文新增 ME-10（规范按需加载）：新建项目、为项目立规范或整改明显不规范的存量项目时，按任务
  实际触及的方面按需加载宿主提供的对应规范 skill，禁止预先批量装载；给出分步推进的参考顺序、每步
  可检查产出与「加载 skill 不等于授权变更」的边界。
- 附录 A 补一个行为示例：空仓库立规范时按需加载、逐步产出。
- 三包版本升到 `0.14.0`。

## 0.13.0（2026-11-14）

**修复**

- 消除跨 skill 的归属冲突：命名改由 `naming-conventions` 独占（原先 `architecture-and-design-conventions`
  把它判给 `code-style-conventions`）；锁竞争拆成「正确性归 `concurrency-conventions`、性能归
  `performance-conventions`」，两处不再互相移交同一主题；必需门禁集合由 `testing-and-quality-conventions`
  定义，`vcs-collaboration-conventions` 只决定按分支类别启用哪些项；依赖漏洞豁免、发布标签权限、
  CODEOWNERS 复核节奏与第三方声明文件名各自指定唯一 owner。
- `testing-and-quality-conventions` 的单元测试预算改以测试层级矩阵为唯一口径，删除与矩阵冲突的
  「10 秒规则」与项目类型表的 PR 预算列。

**变更**

- 18 个 skill 中的 16 个（两个元规范 skill 除外）的维度索引统一为「维度｜首条规则｜详情」三列，详情指向 `references/dimensions.md` 的节号；
  首节统一为「适用范围与优先级」、末节统一为「参考资料」；`references/` 内部引用改用同目录相对名。
- 13 个 skill 的 description 补写「不适用于…」，触发面同时给出适用与排除。
- `release-operations-conventions`、`repository-governance-conventions`、`security-compliance-conventions`、
  `testing-and-quality-conventions` 与 `vcs-collaboration-conventions` 补单人维护、无部署仓库与无 PR 的
  降级路径；`skill-authoring` 的正文上限从「约一屏」改为 250 行。
- 三包版本升到 `0.13.0`。

**新增**

- `tests/skill/test_skills_meta.py`：校验 frontmatter、首末节标题、索引三列与节号一致性、正文行数、
  references 内自引用与正文逐字重复段落，已纳入 `scripts/check.sh`。

## 0.12.0（2026-11-14）

**新增**

- DSH bundle 安装后由插件经 `ctx.systemPrompt.section()` 自动注入约束全文，无需手动复制到
  `~/.dsh/AGENTS.md`；`~/.dsh/AGENTS.md` 或 `~/.agents/AGENTS.md` 已含同内容时按 sha256 去重跳过，
  避免重复。DSH provider 测试补 section 注入、去重、缺文件与字面保留四类用例。
- 三包版本升到 `0.12.0`。

## 0.11.0（2026-11-14）

**新增**

- 新增 5 个编码工程 skill，补齐编码智能体动手写代码的主干能力：`debugging-conventions`（缺陷诊断：
  复现、二分定位、根因分析、最小修复验证）、`architecture-and-design-conventions`（模块边界、分层与
  依赖方向、数据流与控制流、可测试性设计与 ADR）、`refactoring-conventions`（重构与修复的判定、安全
  手法、小步提交、代码异味）、`performance-conventions`（先测量后优化、性能目标与预算、瓶颈定位、
  复杂度分析）、`concurrency-conventions`（共享状态与数据竞争、同步原语、死锁与活锁、异步模型、
  并发测试、不可变性与消息传递）。
- 五个 skill 同时接入三端软链；DSH provider 测试与 `dist.sh` 结构校验从 13 个 skill 改为 18 个。
- 三包版本升到 `0.11.0`。

## 0.10.0（2026-11-14）

**新增**

- 新增第 13 个 skill `skill-authoring`：定义、审查并重构 skill 包的结构、frontmatter、渐进披露、命名与
  触发词、质量校验、打包与三端分发，附 `references/templates.md` 与 `references/checklist.md`。
- 三个包同时分发该 skill；DSH provider 测试与 `dist.sh` 结构校验从 12 个 skill 改为 13 个。

## 0.9.0（2026-11-14）

**新增**

- 新增第 12 个 skill `prompt-authoring`：覆盖系统提示、任务指令、角色人格、few-shot、输出契约、工具与
  检索指令、分类评审，以及评测集、断言、回归、成本与对抗输入；附 `references/templates.md` 与
  `references/evaluation.md`。
- 三个包同时分发该 skill；DSH provider 测试与 `dist.sh` 结构校验从 11 个 skill 改为 12 个。

## 0.8.4（2026-11-14）

**修复**

- Qwen 扩展的 `rules/` 会被 Qwen 当作扩展规则扫描，无 `paths:` 的常驻正文会被丢弃并产生告警；
  Qwen 包改用 `constraints/global-user-constraints.md`，注入脚本同时支持 `constraints/` 与 `rules/`。
- `dist.sh` 增加按包 allowlist：qwen 不再允许 `rules/`，并要求 `constraints/` 存在；测试文件黑名单
  阻止开发测试进入任何包。三包版本升到 `0.8.4`。
- `check.sh` 在本地校验包内容（Qwen `constraints/`、Qoder `rules/`、包内不得有测试）；README 与
  发布手册说明 GitHub Packages 旧包已删除，npm 是唯一发布通道。

## 0.8.3（2026-11-14）

**修复**

- Qwen 包补 `rules/`：此前注入脚本在扩展包里找不到约束正文，`SessionStart` 静默跳过；
  `dist.sh` 的 qwen 结构校验现在要求 `rules/global-user-constraints.md`。
- 开发测试全部移出包目录：skill 测试、hook 测试与 DSH provider 测试改到 `tests/`，包内只保留运行时文件。
- `dist.sh` 增加按包的 allowlist 与开发测试黑名单，防止跨包文件或测试进入 zip；三个包 README 只保留
  自己的安装与行为说明，不再引用仓库工具与测试命令。
- 三包版本升到 `0.8.3`。

## 0.8.2（2026-11-14）

**修复**

- npm 包改为从物化后的 DSH 目录发布，包页 README 用 `plugins/dsh/README.md`，不再显示仓库级的
  三包总览；`files` 去掉重复的 `plugins/dsh/README.md`。
- 根 `package.json` 描述改为 DSH bundle 本身；README 的三包表与源安装示例同步 npm 安装方式。

## 0.8.1（2026-11-14）

**修复**

- 0.8.0 是 npm 上该包名的首次发布，被 npm 的分阶段发布流程收进待审批队列，超时后只剩
  `0.0.0-stage` 占位版本；升到 0.8.1 重新发布。包已存在后为普通发布，不再产生占位版本。

## 0.8.0（2026-11-14）

**变更**

- DSH bundle 改为发布到 npm 公共 registry：`publishConfig` 改为 `access: public`，
  release 工作流用仓库 secret `NPM_TOKEN` 执行 `npm publish --access public`，不再发布 GitHub Packages。
- 原因是 GitHub Packages 的元数据会把自定义 `dsh` 字段裁掉，DSH 插件页因此判定“没有声明组合包”；
  npm 官方 registry 保留该字段，更新检测恢复可用。
- 安装恢复到无需 `.npmrc` 的 `pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@<版本>`；
  三包版本升到 `0.8.0`，文档同步公开包说明。

## 0.7.1（2026-11-14）

**修复**

- Qoder/Qwen 的约束注入在 `SessionStart` 且 `source` 为 `resume` 时跳过，避免恢复会话时把
  32 KB 正文再注入一遍造成上下文膨胀；`startup`、`new`、`clear`、`compact` 仍会注入。
- 三包版本升到 `0.7.1`；注入脚本的测试补 resume 跳过与四种重建来源的用例。

## 0.7.0（2026-11-14）

**新增**

- DSH bundle 发布到 GitHub Packages 私有 registry：仓库根 `package.json` 增加 `publishConfig`
  与 `repository`，release 工作流用 `GITHUB_TOKEN` 执行 `npm publish`；消费方配置 profile 的
  `.npmrc` 后可安装 `@snowcore8/dsh-global-user-constraints@<版本>`。
- 走 registry 的安装可被 DSH 插件页检测到更新；Git 源安装（tag/branch spec）仍然不会检测更新，
  文档已分别说明。
- `check.sh` 增加 DSH `publishConfig` 校验；三包版本统一升到 `0.7.0`。

## 0.6.0（2026-11-14）

**新增**

- 支持 DSH Git 源安装：仓库根新增 `package.json`，把仓库本身声明为
  `@snowcore8/dsh-global-user-constraints` bundle；`pnpm dsh plugin --profile web add
  "github:SnowCore8/system_prompt#v0.6.0"` 即可安装，私有仓库需 `gh auth setup-git`。
- `plugins/dsh/src/index.js` 改为从最近含 `package.json` 的父目录定位包根，同时兼容仓库根布局、
  git 安装布局与 zip 布局；`materialize.sh dsh` 按根布局物化；`dist.sh` 的 dsh 结构校验同步。

**变更**

- 三包版本统一升到 `0.6.0`；`check.sh`、`dist.sh` 与 release 工作流的 DSH 清单位置改为仓库根
  `package.json`；DSH bundle 不再在 `plugins/dsh` 内保留 `package.json`、`skills/` 和 `rules/` 软链。

## 0.5.0（2026-11-14）

**变更**

- 拆成三个独立包：`plugins/qoder`（Qoder 插件）、`plugins/qwen`（Qwen Code 扩展）、`plugins/dsh`
  （DSH bundle）；`rules/`、`skills/` 与 `shared/` 成为唯一真源，包内用相对软链引用，发布时物化。
- 新增 DSH bundle `@snowcore8/dsh-global-user-constraints`：`cordis.patch.yml` 插入 skill 提供者行，
  `src/index.js` 注册 `ctx.skills.registerProvider` 并解析 frontmatter，附 3 项 `node --test` 测试。
- 新增 `scripts/materialize.sh` 物化带软链的包；`dist.sh` 一次构建 `qoder`、`qwen`、`dsh` 三个 zip；
  `check.sh` 校验三包版本、包内软链指向与物化后的 Qoder 插件；release 工作流核对三包版本并挂载三个制品。
- Qoder 本地市场 `plugins/marketplace.json` 的来源改为 `./qoder`；README 与三个包各自的使用文档同步拆分。

**修复**

- 约束注入脚本支持命令行传包根，Qwen 扩展 hook 不再依赖未被设置的环境变量。

## 0.4.0（2026-11-14）

**新增**

- 双端时间感知：新增 `scripts/inject-clock.py`，在 `SessionStart` 与 `UserPromptSubmit` 注入当前本地时间、
  UTC 偏移、时区与星期；Qoder 插件与 Qwen 扩展各接一条 hook，长会话与压缩后仍能拿到最新时间。
- Qwen Code 原生扩展清单 `qwen-extension.json` 与 `hooks/qwen-hooks.json`：同一插件包可被 Qwen 作为扩展安装，
  约束注入、时间注入、十一个 skill 与审查命令一并生效。

**变更**

- 约束注入脚本兼容双端根目录与去重路径（新增 Qwen 用户级/项目级规则与 `QWEN.md`），并移除重复的时间头。
- `scripts/check.sh`、`scripts/dist.sh` 与 release 工作流校验双端清单版本一致；hook 测试增至 18 项。
- 仓库 README、加载规则调研文档与插件说明同步双端安装与时间设计，新增 `docs/time-awareness.md`。

## 0.3.0（2026-11-14）

**变更**

- Qoder 插件包重新设计：安装后由单一 `SessionStart` hook 把约束全文注入上下文（约 32 KB，已实测完整进入），
  用户级或项目级已加载同内容规则/`AGENTS.md` 时跳过；删除未验证的 `qoder.md` 与 9 个事件的时间注入 hook。
- 插件 manifest 补 `repository` 并重写描述；README 重写为「安装即生效、去重、降级」；hook 测试改为
  注入脚本的表驱动用例（9 项）。
- 仓库 README 与加载规则调研文档同步新的 Qoder 生效方式。

## 0.2.1（2026-11-14）

**修复**

- `scripts/dist.sh` 打包前归一暂存目录权限（目录 755、文件 644），消除检出 umask 进入 zip 的 Unix
  属性差异。同一 tag 在本机与 CI 构建的 zip 已字节一致（0.2.0 制品 SHA256 `11b2aaec…`）。

## 0.2.0（2026-11-14）

**变更**

- 版本切换到 SemVer + tag 发布：manifest 的 `version` 是唯一来源，`scripts/dist.sh` 不再推导或改写版本；
  新增 `docs/release.md`、`release` 工作流与 Dependabot，制品为可复现 zip 与 SHA256。
- 引入 ruff 质量门禁：固定开发依赖 `ruff==0.17.5`，新增 `pyproject.toml`，`scripts/check.sh` 与 CI 运行
  `ruff check`。
- 仓库托管到 GitHub 私有仓库并推送 `master` 与 `v0.2.0` tag，`check`、`release` 工作流与 CODEOWNERS 生效。

**修复**

- 发布脚本：`--require-tag` 校验 tag 与 manifest 版本，`--no-validate` 供没有 `qoderclicn` 的 CI 使用；
  构建失败不落制品。

**限制**

- 仓库为私有仓库且未使用 GitHub Pro：经典分支保护与仓库规则集不可用（API 返回 403），
  私有漏洞报告需要 GitHub Advanced Security；`SECURITY.md` 提供邮箱兜底，分支约束暂由 `check` 工作流、
  CODEOWNERS 与 PR 模板承担。

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
- DeepSeek Harness 适配：`.dsh/skills/` 以相对软链暴露插件内十一个 skill，`scripts/check.sh` 校验入口。
- Qwen Code 适配：`.qwen/rules` 目录软链到 `rules/`（无 `paths:`，baseline 规则），`.qwen/skills/` 暴露十一个 skill。
- Qoder 适配：`.qoder/rules` 目录软链到 `rules/`，`.qoder/skills/` 暴露十一个 skill；用户级按插件 README 的「规则激活」安装。
- 软链治理：`scripts/check.sh` 增加全量软链校验（必须入库、相对路径、目标在仓库内且存在、不指向另一软链或 `.git`、目标已跟踪）；
  README 补充软链约定。
- 新增 `docs/agent-tooling-loading.md`：分别整理 Qoder、Qwen Code 与 DeepSeek Harness 的 rules/skills/plugins 加载规则，附对照表与本仓库映射。
- 仓库治理：新增双许可证（文档 CC BY 4.0、代码 MIT）、`SECURITY.md`、`GOVERNANCE.md`、`THIRD-PARTY-NOTICES.md`、
  `.gitattributes` 与 `.github/`（CI、CODEOWNERS、PR 模板）；`scripts/dist.sh` 把许可证打进制品，归一 mtime 并排序后输出
  可复现 zip 与 SHA256 校验和。

**变更**

- 根 `AGENTS.md` 指向 `CONTRIBUTING.md`，只承载本仓库维护约定；用户全局约束留在 `rules/`，由用户级入口与插件分发。
- 入口统一为各工具的主项目路径：`.qwen` 与 `.qoder` 为普通目录，分别含 `rules` 与 `skills` 软链；
  不再提供 `.qwen/AGENTS.md`、`.qoder-cn`、`.qoder/plugins` 等无加载语义的占位入口。
- 规范正文与十一个 skill 改为中文语义正文；`rules/global-user-constraints.md` 是唯一规范文件，英文参考译本已移除。
- `GLOSSARY.md` 增加翻译与写作口径与中英术语对照，统一审查/审计、校验/检查、第三方引入、包仓库、
  运行手册/操作手册、事故复盘、制品/产物、销毁性/破坏性等写法；行宽统一为 200 字符（约 100 汉字宽）。

**修复**

- 旧 skill 治理：`naming-conventions`、`comment-conventions`、`documentation-conventions`、`system-prompt-authoring` 补齐与七个通用规范的归属边界，移除重复的教学与流程内容；命名索引与 34 个维度章节一一对应。
- `system-prompt-authoring` 补 Scope 与 Review Checklist，核验来源并修正过期引文，`--strict` 说明与 checker 行为对齐；仓库 README 与术语表不再把内容规则限定为 S1–S13。
- Qwen 入口两次修正：先由 `.qwen` 软链改为 `.qwen/AGENTS.md`；核实 Qwen 只扫描 `.qwen/rules/` 与各级
  `AGENTS.md` 后改为 `.qwen/rules`，因 `readdir` 的 `isFile()` 跳过文件软链，最终固定为目录软链。
- 术语与口径：README 与插件说明的「检查」改为「校验」，zip「产物」改为「制品」，「规范来源/规范源」
  改为「权威来源」；`requirements-dev.txt` 固定版本并同步 `check.py` 依赖提示。
- 插件：hook 测试补充注册命令与 `QODER_PLUGIN_ROOT` 替换执行的断言，并从实现加载事件集合，去掉测试里的副本；
  README 增加安全边界；manifest 补 `license` 字段；`scripts/check.sh` 增加敏感文件忽略与私钥内容回归。
- 校验器：`count_row_cells` 按 GFM 只把反斜杠转义管道当字面量，代码跨度内未转义管道不再漏报；测试同步更新。
- 打包：`dist.sh` 默认要求干净工作区（`--allow-dirty` 放行）、拒绝浅克隆、在暂存区完成校验后原子落盘，
  并输出 SHA256 校验和、保留最近三个制品。
- 配置：`.editorconfig` 行宽 200 与 `check.py` 对齐；CI 先确认 `shellcheck` 可用；`scripts/check.sh`
  结尾报告跳过项数；`CONTRIBUTING.md` 写明 Windows 软链前置、注释语言与 trunk-based 分支模型。

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
