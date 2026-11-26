# 三工具加载规则：rules、skills、plugins

维护者：SnowCore8；何时阅读：调整各工具入口或调研加载行为时。

本文分别整理 Qoder、Qwen Code 与 DeepSeek Harness（DSH）三类工件的加载规则与目录结构。
取证口径：官方文档优先，能读源码的读源码；DSH 以本地实现树为准，因为它就是运行中的版本。

版本基线：

| 工具 | 基线 | 取证日期 |
| --- | --- | --- |
| Qoder | 文档站 `docs.qoder.com` / `docs.qoder.cn`；Qoder CLI CN 1.1.88 实测 | 2026-11-14 |
| Qwen Code | 源码 `QwenLM/qwen-code` main @ `6ba8820`，`package.json` 0.27.2 | 2026-11-14 |
| DeepSeek Harness | 本地实现树（运行中的 DSH 安装目录） | 2026-11-14 |

## 结论摘要

- Qoder 三者齐全：`rules/` 目录、`skills/` 目录、插件市场；插件当前**不能**真正携带 rules。
- Qwen Code 没有独立的 rules 目录名，但 `.qwen/rules/` 是条件规则机制；常驻约束走 `QWEN.md`/`AGENTS.md`。
- DSH 没有 rules 目录：常驻约束是指令链，skills 走六个扫描根，插件以 bundle + profile 组合。

## Qoder

### Qoder 的 rules：一条规则一个 Markdown

| 作用域 | 路径 | 是否提交 |
| --- | --- | --- |
| 项目级 | `<project>/.qoder/rules/**/*.md` | 是 |
| 用户级 | `~/.qoder/rules/**/*.md`；CN 为 `~/.qoder-cn/rules/**/*.md` | 否 |

- 项目级规则可放在工作区任意层级（含嵌套子目录）；CLI 启动或刷新记忆时从当前目录**向上查找**
  到 `.git` 所在目录，逐层检查 `.qoder/rules/**/*.md` 与各级 `AGENTS.md`、`AGENTS.local.md`。
- 子目录记忆不预加载：只有成功读取子目录里的文件后，才从该目录向上补入此前未加载的规则。
- front matter 决定生效方式；`trigger` 存在时优先于 `alwaysApply`：

| 字段 | 取值 | 说明 |
| --- | --- | --- |
| `trigger` | `always_on` / `manual` / `model_decision` / `glob` | 生效方式 |
| `alwaysApply` | `true` / `false` | 兼容字段；`true` 等同 `always_on`，`false` 等同 `manual` |
| `description` | 字符串 | `model_decision` 必填，否则只注入路径 |
| `glob` | 单个 glob 或数组 | `trigger: glob` 必填 |
| `paths` | 单个 glob 或数组 | 等价于 `trigger: glob` + `glob` |

| 生效方式 | 配置 | 加载行为 |
| --- | --- | --- |
| 始终生效 | 不写 front matter，或 `trigger: always_on`，或 `alwaysApply: true` | 启动或刷新记忆时加载正文 |
| 手动引入 | `trigger: manual` 或 `alwaysApply: false` | 不自动注入正文 |
| 模型决策 | `trigger: model_decision` + 非空 `description` | 只注入路径和说明，模型判断相关后再读 |
| 指定文件 | `trigger: glob` + `glob`，或 `paths` | 访问匹配文件后按需加载 |

- 无 front matter 默认 `always_on`；`trigger: glob` 缺 `glob`、`model_decision` 缺 `description` 时正文不自动注入。
- 没有官方定义的跨作用域覆盖顺序：用户级、项目级、本级规则逐条拼接注入，冲突由模型处理。
  IDE 文档另有一条：`AGENTS.md` 与 rules 冲突时 rules 优先。
- IDE 限制所有活跃规则合计最多 100,000 字符，超出截断；CLI 是否有同一上限未在文档中说明。
- `@path` 导入只对 `AGENTS.md` 有官方说明；rules 正文是否支持导入未验证，保守做法是写自包含正文。
- 没有独立的企业级 rules 目录；团队共享就是把项目级 `.qoder/rules/` 提交进 Git。
- 插件侧预留了 `rules/` 目录与 manifest 字段，但当前 runtime 不加载，详见下文 plugins 一节。

来源：[Qoder CLI 记忆](https://docs.qoder.cn/cli/memory)、[Qoder IDE 规则](https://docs.qoder.com/user-guide/rules)。

### Qoder 的 skills：目录名即身份

| 来源 | 路径 | 注册名 |
| --- | --- | --- |
| 项目级 | `<project>/.qoder/skills/<name>/SKILL.md` | 目录名 |
| 项目共享 | `<project>/.agents/skills/<name>/SKILL.md` | 目录名 |
| 用户级 | `~/.qoder/skills/<name>/SKILL.md`；CN 为 `~/.qoder-cn/skills/` | 目录名 |
| 插件 | `<plugin>/skills/<name>/SKILL.md` | `<plugin>:<skill>` |
| 内置 | 随 CLI 发布 | 内置名 |

- 只扫描 `SKILL.md`，大小写敏感；`scripts/`、`references/`、`templates/` 等辅助文件随 skill 目录
  一起保留，按需读取，用于渐进式披露。
- 官方 front matter 必填 `name`（最多 64 字符，小写字母、数字、连字符）与 `description`
  （最多 1024 字符）。CLI 1.1.88 实测：身份取**目录名**，`name` 与目录名不一致不报错，
  且会递归发现 `skills/nested/deep/SKILL.md`。
- 同名优先级存在文档矛盾：IDE 文档说项目级优先；CLI 文档与 1.1.88 实测都是**用户级优先**
  （内置 < 插件 < 项目 < 用户）。跨端使用时应避免同名。
- 插件被禁用时其全部 skill 一并禁用，不能单独禁用插件内的某个 skill。
- 管理命令：`qoderclicn skills list|install|link|enable|disable|uninstall`；没有 `skills validate`。
  交互态用 `/skills` 查看、`/skills reload` 重新发现；插件内的 skill 由 `plugins validate` 校验。

来源：[Qoder CLI Skills](https://docs.qoder.com/cli/Skills)、[Qoder IDE Skills](https://docs.qoder.cn/user-guide/skills)。

### Qoder 的 plugins：清单、作用域与市场

插件是「目录 + 清单」的能力包，清单为 `.qoder-plugin/plugin.json`。

| 路径 | 作用 |
| --- | --- |
| `skills/` | 技能目录，自动发现 |
| `commands/` | 自定义斜杠命令，可嵌套子目录 |
| `agents/` | 子代理定义文件（`.md`） |
| `hooks/hooks.json` | Hook 配置，形状为 `{"hooks": {...}}` |
| `output-styles/` | 输出风格 |
| `workflows/` | Workflow 定义 |
| `bin/` | 可执行文件，加入 PATH |
| `.mcp.json` | 插件自带 MCP，回退读 `mcp.json` |
| `rules/` | CN 打包规范列出，但当前 runtime 不加载 |

清单字段：`name` 必填；`version`、`displayName`、`description`、`author`、`homepage`、
`repository`、`license`、`keywords`、`dependencies` 可选。组件字段 `skills`、`commands`、
`agents`、`hooks`、`mcpServers`、`outputStyles` 用于覆盖约定目录或内联声明。

| scope | 启用状态写入 |
| --- | --- |
| `user` | `~/.qoder/settings.json` 的 `enabledPlugins`（CN `~/.qoder-cn/settings.json`） |
| `project` | `<project>/.qoder/settings.json` 的 `enabledPlugins` |
| `local` | `<project>/.qoder/settings.local.json` 的 `enabledPlugins` |

- 插件 ID 形如 `name@marketplace` 或 `name@local`；禁用插件会一次性禁用其全部组件。
- 安装包体在用户配置根的 `plugins/cache/<marketplace>/<plugin>/<version>/`；注册表
  `installed_plugins_v2.json`，市场注册表 `known_marketplaces.json`。
- 命令：`qoderclicn plugins list|install|validate|uninstall|enable|disable|update|marketplace`；
  没有 `pack`，发布需自行打 zip（根目录含 `.qoder-plugin/`）。`--plugin-dir <dir>` 可临时追加搜索目录。
- 市场清单 `marketplace.json` 含 `name`、`owner`、`plugins`；条目里写 `source`、`category`、
  `tags`、`strict`。`category`/`tags`/`strict` 属于市场清单，写进插件清单会被提示放错位置。

插件携带 rules 的现状：CN 支持矩阵把 Rules 标为 Desktop「即将支持」、CLI「不适用」；
CLI 1.1.88 的 `plugins validate` 把 `"rules"` 报为 unknown field 并忽略，只含 `rules/` 的插件
会因「没有可安装组件」被拒。宿主原生的做法仍是把规则放用户级或项目级 `.qoder/rules/`；
插件若要让约束安装即生效，只能在 `SessionStart` hook 中把规则写进用户级 `.qoder/rules/`
（本仓库插件首次/内容变化时覆盖写入，不通过 hook 注入正文，之后由 Qoder 原生 rules 加载；
`UserPromptSubmit` 每轮提醒 `Never violate global user constraints.`）。卸载需手动删除该
rules 文件。`qoder.md` 是否加载未验证，本仓库已移除。

来源：[Qoder 插件参考](https://docs.qoder.com/cli/plugins-reference)、[Qoder CN 插件打包规范](https://docs.qoder.cn/qoder-plugins)。

### Qoder 三者关系

- `AGENTS.md` 与 rules 都属于静态记忆，进入同一份上下文；skills 启动只建
  `name + description` 索引，正文在触发时载入；plugins 是分发与注册层。
- 加载时序：合并 settings 与信任目录 → 解析已启用插件并注册组件 → 加载静态记忆
  （`AGENTS.md` 与 rules，按 front matter 决定正文时机）→ skills 建索引 → MCP 与 hooks 生效。
- 禁用插件即禁用其全部组件；规则与 skill 的分工是「约束」与「可复用流程」。

## Qwen Code

### Qwen Code 的 rules：上下文文件加 `.qwen/rules`

Qwen Code 有两套常驻指令机制：上下文文件（`QWEN.md`/`AGENTS.md`）与规则目录（`.qwen/rules/`）。

上下文文件的默认文件名列表是 `["QWEN.md", "AGENTS.md"]`：

| 路径 | 说明 |
| --- | --- |
| `~/.qwen/QWEN.md`、`~/.qwen/AGENTS.md` | 用户级，总是加载 |
| 项目根到 cwd 各级的 `QWEN.md` | 需工作区可信；由项目根向 cwd 逐层查找 |
| 项目根到 cwd 各级的 `AGENTS.md` | 同上 |
| `<project>/.qwen/QWEN.local.md` | 仅真实 git 根，最后追加 |
| 已启用扩展的 context 文件 | 每个请求携带，默认扩展目录内 `QWEN.md` |

- `context.fileName`（`string | string[]`）会**替换**默认列表而不是追加；旧顶层键
  `contextFileName` 已迁移为 `context.fileName`。
- 多个文件按「文件名优先、目录其次」的顺序拼接，每段包在
  `--- Context from: <路径> ---` 标记里；按 realpath 去重；没有覆盖语义，冲突需自行删改。
- `@path/to/file` 导入受支持：相对被导入文件所在目录解析，深度上限 5，代码块与行内代码里的
  `@` 不导入，默认限制在项目根内。
- 没有显式的文件体积上限，只有模型上下文窗口这一硬约束；官方反复强调保持短小。
- **项目级 `<project>/.qwen/AGENTS.md` 不在发现列表**：源码只在每一级目录查
  `QWEN.md`/`AGENTS.md` 文件名，不会进入 `.qwen/` 子目录再找 `AGENTS.md`。
  `CLAUDE.md`、`GEMINI.md` 默认也不读。

规则目录 `.qwen/rules/` 是另一套机制：

| 作用域 | 路径 | 加载条件 |
| --- | --- | --- |
| 用户级 | `~/.qwen/rules/**/*.md` | 总是加载 |
| 项目级 | `<project>/.qwen/rules/**/*.md` | 工作区可信时 |
| 扩展 | `<extension>/rules/**/*.md` | 只接受带 `paths:` 的条件规则 |

- 递归扫描所有 `.md`，按绝对路径字典序排序；front matter 只解析 `description` 与 `paths`。
- 无 `paths:` 的 baseline 规则从首个请求起进入 system prompt；有 `paths:` 的条件规则在工具
  读取或修改匹配文件时注入一次，本会话不再重复。glob 相对项目根、匹配 dotfiles、解析软链。
- 扩展规则必须带 `paths:`，否则被丢弃并在启动时警告；扩展规则不受 folder trust 限制。
- 没有用户开关；safe 模式禁用全部 rules 与 context，bare 模式也不加载 rules。
- HTML 注释在发送前剥离。

来源：[Qwen Code Rules](https://qwenlm.github.io/qwen-code-docs/en/users/features/rules/)、
[Qwen Code Memory](https://qwenlm.github.io/qwen-code-docs/en/users/features/memory/)、
源码 `packages/core/src/{memory/memoryDiscovery.ts,config/rulesDiscovery.ts}`。

### Qwen Code 的 skills：一层目录

| 来源 | 路径 | 注册名 |
| --- | --- | --- |
| 项目级 | `.qwen/skills/<name>/SKILL.md` | front matter `name` |
| 项目别名 | `.agents/skills/<name>/SKILL.md` | 同上 |
| 用户级 | `~/.qwen/skills/<name>/SKILL.md` | 同上 |
| 用户别名 | `~/.agents/skills/<name>/SKILL.md` | 同上 |
| 自定义 | `skills.directories` 里的每个目录 | 同上 |
| 扩展 | `<extension>/skills/<name>/SKILL.md` | `<ext>:<name>` |
| 内置 | 随包发布 | 内置名 |

- 只扫描一层 `<name>/SKILL.md`，不递归；技能目录本身可以是软链。默认不读 `.claude/skills/`。
- 必填 `name`（匹配 `/^[\p{L}\p{N}_:.-]+$/u`）与 `description`；可选 `priority`、`paths`、
  `user-invocable`、`disable-model-invocation`、`allowedTools`、`hooks`、`argument-hint`、
  `when_to_use`、`model`。注意工具白名单只认 `allowedTools`，`allowed-tools` 会被忽略。
- `paths` 让技能在命中前不进模型可见清单，命中后本会话保持激活；用户仍可 `/name` 直接调用。
- 优先级：项目 > 用户（含自定义目录）> 扩展 > 内置；同一级别内 `.qwen` > `.agents`。
- 模型通过 `Skill` 工具调用，用户通过 `/name` 或 `/skills` 面板；没有 `qwen skills` 校验子命令，
  排查靠 `qwen --debug` 的 `SKILL_MANAGER` 日志。

来源：[Qwen Code Skills](https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/)、
源码 `packages/core/src/skills/skill-manager.ts`。

### Qwen Code 的 plugins：extensions

Qwen Code 的插件叫 extensions，原生清单为 `qwen-extension.json`；安装时还能转换
Gemini（`gemini-extension.json`）、Claude（`.claude-plugin/plugin.json`）、Qoder
（`.qoder-plugin/plugin.json`）与 Agent Plugins v1（根 `plugin.json`）格式。

| 位置 | 说明 |
| --- | --- |
| `~/.qwen/extensions/<name>/` | 唯一加载目录（`$QWEN_HOME/extensions`） |
| `~/.qwen/extension-store/state.json` | 启用状态，含工作区覆盖 |
| `~/.qwen/.env`、`.qwen/.env` | 扩展设置值，工作区优先 |

- 没有项目级 `.qwen/extensions/` 加载：`--scope project` 只限定当前工作区的启用范围，
  扩展文件仍装在用户目录。
- 清单字段：`name`、`version`、`displayName`、`description`、`mcpServers`、`lspServers`、
  `contextFileName`、`commands`、`skills`、`skillStates`、`agents`、`workflows`、`settings`、
  `hooks`、`channels`。
- 可贡献工件与时机：

| 工件 | 加载时机 |
| --- | --- |
| context 文件 | 启用后每个请求拼接，无相关性过滤、无体积上限 |
| rules | 启动时加载，只接受带 `paths:` 的条件规则 |
| skills | 启动时注册为 `<ext>:<name>`，调用时载入正文 |
| commands | 启动时注册；冲突时降级为 `/<ext>.<cmd>` |
| agents、hooks、MCP、LSP、workflows、channels | 启动时注册或连接，各有开关 |
| settings | 安装时询问，值写入 `.env` |

- 冲突：MCP 同名时 `settings.json` 优先；扩展命令优先级最低；技能因带 `<ext>:` 前缀不会互相遮蔽。
- 命令：`qwen extensions install|link|list|update|uninstall|enable|disable|new|settings|sources`；
  交互态用 `/extensions` 与 `/reload-plugins`。CLI 改动在运行中的会话里需重启或重载才生效。

来源：[Qwen Code 扩展介绍](https://qwenlm.github.io/qwen-code-docs/en/users/extension/introduction/)、
[Agent Plugins](https://qwenlm.github.io/qwen-code-docs/en/users/extension/agent-plugins/)、
源码 `packages/core/src/extension/extensionManager.ts`。

### Qwen Code 三者关系

- 启动时先加载 extensions、context 与 rules，再组装 system prompt：context 全文 + baseline rules
  + 技能清单（只有 name 与 description）。
- 运行中条件规则按文件访问解锁，skill 正文在调用时载入，扩展 context 每个请求都携带。
- 官方分工：永远为真的短事实放 `QWEN.md`；只在某路径下成立的约束放带 `paths:` 的规则；
  模型自选流程放 skill；必须无条件执行放 hook；要分发或带工具放 extension。

## DeepSeek Harness

### DSH 的 rules：指令链，没有 rules 目录

DSH 不读 `.dsh/rules` 或 `.claude/rules`。常驻约束由 `dsh-agent-instructions` 插件装载，
`dsh-base` 默认启用，读取两条链：

| 链 | 文件 | 说明 |
| --- | --- | --- |
| 用户全局 | `$DSH_HOME/AGENTS.md`，然后 `$DSH_AGENTS_HOME/AGENTS.md` | 默认 `~/.dsh/AGENTS.md`、`~/.agents/AGENTS.md`；无本地覆盖文件 |
| 项目 | 项目根到会话 cwd 每层的 `AGENTS.md`、`CLAUDE.md` | 再由 `AGENTS.local.md`、`CLAUDE.local.md` 叠加 |

- 项目根是最近的含 `.git` 的祖先；找不到时用当前 cwd。同一候选组内内容相同的文件只渲染一次。
- 按由宽到窄拼接：用户全局链在前，项目链从根到 cwd。首轮请求注入一条持久的
  `<system-reminder>` 消息；不解释 `@path` 导入、大小写变体或 `.claude/rules/`。
- 预算按链分别计：`maxBytes` 默认 65536 字节，单个源文件 `maxSourceBytes` 默认 1 MiB。
  超预算先整份丢弃更宽的文件，再截断剩下的最后一个，并输出 `Workspace instruction budget` 提示。
- 首次加载后不持续监听：后续 `read`、`write`、`edit` 成功进入更深目录时补入新文件；
  内容变化替换原文，文件消失或与更早候选重复时给出移除通知；会话恢复时对账。
- 更具体的文件优先于更宽的；指令不覆盖系统、开发者或直接用户指令。

来源：DSH 源码树 `packages/context/agent-instructions/README.md`。

### DSH 的 skills：六个扫描根，一层深度

skills 由注册表 `dsh-skill`、文件系统提供者 `dsh-skill-filesystem` 与消费者 `dsh-tool-skill`
组成。默认扫描根按 rank 从低到高：

| Rank | 来源 | 根 |
| --- | --- | --- |
| 100 | `project-dsh` | `<projectRoot>/.dsh/skills` |
| 200 | `project-agents` | `<projectRoot>/.agents/skills` |
| 300 | `custom` | `customSkillDirs` 配置项 |
| 400 | `user-dsh` | `<dshHome>/skills`，跳过其 `.system` 子目录 |
| 500 | `user-agents` | `<agentsHome>/skills` |
| 600 | `bundled` | 配置了 `bundledSkillDir` 时 |

- 项目根同样是最近的含 `.git` 的祖先；没有时用 cwd。用户根默认 `~/.dsh` 与 `~/.agents`。
- 两种形式：目录包 `<name>/SKILL.md`，或扫描根顶层的平铺文件 `<name>.md`。不递归发现嵌套
  `SKILL.md`；`references/`、`scripts/`、`assets/` 等资源不算目录项。
- front matter 必填 `name`（kebab-case）与 `description`；可选 `whenToUse`、`metadata`、
  `disable-model-invocation`、`user-invocable`。`name` 与目录名不要求一致，旧 camelCase 键被拒。
- 模型只在会话目录看到 `name` 与 `description`（描述上限默认 500 字符）；正文由 `skill` 工具
  按需读取，返回 `<skill_content>`、`<skill_resources>`、`<skill_instructions>`。
- 同名解析：先看作用域层（preset 层覆盖全局层），同层再按 rank、提供者注册顺序、本地顺序。
- 目录变化由 chokidar 监听；根不存在时从最近的已存在祖先逐段探测。监听失败只让本次观测不完整，
  可用候选仍可直接加载；不完整观测不缓存，下次重试。

来源：DSH 源码树 `docs/subsystems/skills.md`、`packages/skill/skill-filesystem/README.md`。

### DSH 的 plugins：plugin、bundle、profile 三层

DSH 里「插件」是 TypeScript 模块，导出 `apply(ctx)`；可分发的安装单元叫 bundle，
可启动的组合叫 profile。

| 概念 | 形态 | 声明 |
| --- | --- | --- |
| plugin | 模块、对象或类，导出 `apply`；用 `inject` 声明依赖服务 | 无独立清单，被 patch 行引用 |
| bundle | npm 包，含一个或按序多个 patch 文件 | `package.json` 的 `dsh.bundle.patch` |
| profile | `<DSH_HOME>/profiles/<name>` 目录 | `package.json` 的 `dsh.profile.bundles` 有序列表 |

- profile 目录固定两个文件：`package.json`（依赖与 bundle 列表）与 `cordis.patch.yml`
  （用户覆盖层）；可选 `compatibility.json` 记录精确版本豁免。
- 层序：按 `dsh.profile.bundles` 列表顺序应用每个 bundle 的 patch，然后 profile 的
  `cordis.patch.yml`，然后 `$DSH_HOME/cordis.patch.yml`，最后按 argv 顺序应用 `--patch`。
  后应用的层按行 id 覆盖先前的层，且替换整份 `config`，不做深合并。
- 安装与移除：`dsh plugin --profile <name> add <包>` 与 `remove <包>`，参数原样转发给
  profile 目录里的 pnpm；首次使用会初始化以 `@deepseek-ai/dsh-base` 为首个 bundle 的 profile。
- 兼容性：`engines.dsh` 优先，其次检查 `@deepseek-ai/dsh*` 的 peer 范围；不满足的 bundle
  被跳过并记入 `skippedBundles`，不改变已保存的选择。
- 启停：在 profile patch 里给对应行写 `disabled`；Web 的 Plugins 页与 `plugin_manager` 工具
  做同样的事，只有启用 HMR 时才即时生效，否则重启后生效。
- 插件可贡献的能力没有白名单：`ctx` 上能注册什么就能贡献什么，例如工具、人类命令、
  skill 提供者、MCP 服务器、指令上下文与界面组件。Claude Code 风格 hooks 经
  `dsh-experimental-claude-code-mods` 桥接，而不是读 `plugin.json`。
- agent preset 是另一个作用域层：preset 的 standing composition 挂载的插件落在该 preset 的层，
  影响该 agent 可见的 skills 与工具。

来源：DSH 源码树 `docs/user/develop/basic/publish.md`、`packages/boot/app-boot/README.md`、
`packages/boot/plugin-manager/README.md`。

### DSH 三者关系

- 指令链是「常驻上下文」，skills 是「按需能力」，插件是「组合与分发」；三者不共用目录约定。
- skills 与工具的能力边界由 provider 决定；插件可以提供新的 skill provider，从而改变扫描根。
- 项目级入口是 `.dsh/skills` 与根 `AGENTS.md`；用户级入口是 `~/.dsh/skills` 与 `~/.dsh/AGENTS.md`。

## 对照表

| 维度 | Qoder | Qwen Code | DeepSeek Harness |
| --- | --- | --- | --- |
| 常驻约束载体 | rules 目录 + `AGENTS.md` | `QWEN.md`/`AGENTS.md` + `.qwen/rules` | 指令链 `AGENTS.md`/`CLAUDE.md` |
| 项目级约束路径 | `.qoder/rules/` | 项目根 `AGENTS.md` 或 `.qwen/rules/` | 项目链 `AGENTS.md` |
| 用户级约束路径 | `~/.qoder/rules/`（CN `~/.qoder-cn/rules/`） | `~/.qwen/AGENTS.md`、`~/.qwen/rules/` | `~/.dsh/AGENTS.md`、`~/.agents/AGENTS.md` |
| 条件规则 | `trigger: glob` + `glob`/`paths` | `paths:` 条件规则 | 无（只有整份文件） |
| 指令文件导入 | 仅 `AGENTS.md` 支持 `@path` | `@path`，深度 5 | 不支持 |
| 项目根判定 | 向上查到 `.git` | 最近 `.git` | 最近 `.git` |
| skills 项目路径 | `.qoder/skills/`、`.agents/skills/` | `.qwen/skills/`、`.agents/skills/` | `.dsh/skills/`、`.agents/skills/` |
| skills 用户路径 | `~/.qoder/skills/`（CN `~/.qoder-cn/skills/`） | `~/.qwen/skills/`、`~/.agents/skills/` | `~/.dsh/skills/`、`~/.agents/skills/` |
| skills 扫描深度 | 递归（1.1.88 实测） | 一层 | 一层 |
| skills 必填字段 | `name`、`description` | `name`、`description` | `name`、`description` |
| skills 同名优先级 | 用户级优先（CLI 实测）；IDE 文档相反 | 项目 > 用户 > 扩展 > 内置 | rank 低者优先，preset 层覆盖全局层 |
| 插件清单 | `.qoder-plugin/plugin.json` | `qwen-extension.json` | `package.json` 的 `dsh.bundle` |
| 插件安装位置 | 用户配置根 `plugins/cache/`，按 scope 记 `enabledPlugins` | 仅 `~/.qwen/extensions/` | `$DSH_HOME/profiles/<name>/` |
| 插件能否带 rules | 规范可放，当前不加载 | 可放 `rules/`，仅条件规则生效 | 插件即代码，可注册任何能力 |
| 校验命令 | `qoderclicn plugins validate` | 无 `skills` 校验；靠 `/skills` 与日志 | `dsh --dump-config`、web 加载日志 |

## 与本仓库的映射

本仓库按上文的规则整改后，各工具的项目级入口如下：

- Qwen Code：`.qwen/rules`（由 `scripts/assemble.sh` 从 `rules/` 生成）。其中的规则没有 `paths:`，属 baseline，
  首个请求进入 system prompt；`.qwen/AGENTS.md` 会被 Qwen 忽略，因此不再提供。
- Qoder：项目级 `.qoder/rules`，由 `scripts/assemble.sh` 从根级 `rules/` 生成；用户级由插件 `SessionStart` hook 自动写入
  （同内容已存在时跳过，不注入正文），也可手动复制到 `~/.qoder-cn/rules`（国际版 `~/.qoder/rules`）。
  `.qoder-cn` 与 `.qoder/plugins` 在项目级没有加载语义，已移除。
- DeepSeek Harness：`.dsh/skills` 是 rank 100 的 skill 扫描根，由 `scripts/assemble.sh` 从顶层
  `skills/` 生成；根 `AGENTS.md` 是项目指令入口；约束正文由 bundle 经 `ctx.systemPrompt.section()` 自动注入，
  `~/.dsh/AGENTS.md` 已含同内容时按 sha256 去重跳过。
- skills：`.qwen/skills`、`.qoder/skills`、`.dsh/skills` 都是由 `scripts/assemble.sh` 生成的普通目录；
  Qoder 与 Qwen Code 只扫描一层，DSH 也不递归发现嵌套 `SKILL.md`。
- 三包分发：Qoder 插件在 `plugins/qoder`（`command` + `args`，`${QODER_PLUGIN_ROOT}`），
  Qwen 扩展在 `plugins/qwen`（单条 `command`，`${CLAUDE_PLUGIN_ROOT}`），DSH bundle 在
  `plugins/dsh`（`ctx.skills.registerProvider`）；Qoder/Qwen 共用 `rules/`、`skills/` 与 `shared/`，
  DSH bundle 只带 `rules/` 与 `skills/`。
- 时间：两者都没有内建时间感知；Qwen 在 `SessionStart` 与 `UserPromptSubmit`、Qoder 在
  `UserPromptSubmit` 注入 DSH 风格三行时间块（Qoder 用插件数据记录 turn 与耗时，不输出 step）；
  Qoder 另在 `PreToolUse`/`PostToolUse`/`PostToolUseFailure` 注入一行时间，并在
  `SessionStart(source=compact)` 补约束提醒与压缩后时间，见 `docs/time-awareness.md`。
- 根 `AGENTS.md` 也会被 Qwen Code 当作项目级 `AGENTS.md` 读取，所以它只承载本仓库的代理项目指令；
  人类贡献与发布流程在 `CONTRIBUTING.md`，不进入模型上下文。
- 插件包内 Qoder 与 DSH 随包分发 `rules/`、Qwen 分发 `constraints/`（Qwen 把扩展的 `rules/` 当作
  条件规则，见 Qwen 一节）；Qoder 宿主当前不加载插件的 `rules/`（见 Qoder 一节）。

## 未验证与文档矛盾

- Qoder skills 同名优先级：IDE 文档写项目级优先，CLI 文档与 1.1.88 实测相反。
- Qoder 插件 rules 的落地时间：schema 与打包规范已存在，CLI 不加载，Desktop 标注「即将支持」。
- Qoder IDE 的 100,000 字符上限是否同样适用于 CLI：文档未说明。
- Qoder `qoder.md` 是否作为插件级指令加载：打包规范提到，支持矩阵标「—」，未验证。
- Qwen Code 历史版本是否读过 `<project>/.qwen/AGENTS.md`：当前版本不支持，历史未找到证据。
- Qwen Code 项目级扩展：`storage.ts` 注释提到过 `<project>/.qwen/extensions/`，当前实现不加载。

## 来源

Qoder：

- [Qoder CLI 记忆（rules 与 AGENTS.md）](https://docs.qoder.cn/cli/memory)
- [Qoder IDE 规则](https://docs.qoder.com/user-guide/rules)
- [Qoder CLI Skills](https://docs.qoder.com/cli/Skills)
- [Qoder 插件参考](https://docs.qoder.com/cli/plugins-reference)
- [Qoder CN 插件打包规范与支持矩阵](https://docs.qoder.cn/qoder-plugins)

Qwen Code：

- [Rules](https://qwenlm.github.io/qwen-code-docs/en/users/features/rules/)
- [Skills](https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/)
- [Memory](https://qwenlm.github.io/qwen-code-docs/en/users/features/memory/)
- [Extensions 介绍](https://qwenlm.github.io/qwen-code-docs/en/users/extension/introduction/)
- 源码：`memoryDiscovery.ts`、`memory-constants.ts`、`rulesDiscovery.ts`、`skill-manager.ts`、
  `extensionManager.ts`、`storage.ts`（`QwenLM/qwen-code` main）。

DeepSeek Harness：

- 源码树 `packages/context/agent-instructions/README.md`
- 源码树 `docs/subsystems/skills.md`
- 源码树 `docs/user/develop/basic/publish.md`
- 源码树 `packages/boot/plugin-manager/README.md`
