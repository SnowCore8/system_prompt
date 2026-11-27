# 全局用户约束：DeepSeek Harness bundle

本包把全局用户约束与 21 个 skill 装入 DeepSeek Harness（DSH）：约束以 `systemPrompt.section()` 注册，skill
以提供者注册，二者随 profile 的 bundle 层生效。本文件只说明安装、生命周期集成、行为与边界，规则以包内
`rules/global-user-constraints.md` 为准。

维护者：SnowCore8。

## 包结构

| 路径 | 作用 |
|---|---|
| `package.json` | npm 包与 `dsh.bundle.patch` 声明，含 `engines.dsh` |
| `plugins/dsh/cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `plugins/dsh/src/` | Cordis 入口与模块（`index.js`、`constraints.js`、`skills.js`、`paths.js`、`constants.js`） |
| `skills/` | 21 个 skill，含生命周期治理与各专业规范 |
| `rules/global-user-constraints.md` | 全局用户约束正文 |

## 安装

从 npm 公共包仓库安装（插件页可检测更新）：

```bash
pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@<版本>
```

也可从 Git 源安装（tag 方式不检测更新）或安装解压后的目录：

```bash
pnpm dsh plugin --profile web add "github:SnowCore8/system_prompt#v<版本>"
pnpm dsh plugin --profile web add /path/to/global-user-constraints-dsh-<版本>
```

装完开新会话；没生效重启 `pnpm dsh web`。

## 生命周期集成

插件在 `apply(ctx)` 中注册两项能力：约束 section 进入系统提示，skill 提供者把 21 个 skill 以 `bundled` 来源
注册。DSH 没有内建 hook，约束不依赖事件：每次装配 system prompt 都会求值 section，压缩后重建 system head。

| 机制 | 注册内容 | 生命周期作用 |
|---|---|---|
| `ctx.systemPrompt.section()` | 名称 `global-user-constraints`、order 400、`interpolate: false` 的约束正文 | G0 受理与后续阶段可用的常驻依据 |
| skill 提供者 | rank 700、source `bundled` 的提供者，暴露 `name` 与 `description` | S1–S6 按阶段加载对应规范 |
| profile patch 行 | `global-user-constraints-skills` | 可在 profile 的 `cordis.patch.yml` 覆盖或禁用 |

- 约束正文在 `apply` 时读取；文件缺失时注册跳过，超过 64 KiB 时注册提示 section 而不注入全文。
- 只对两个用户级 `AGENTS.md`（`$DSH_HOME`、`$DSH_AGENTS_HOME`）做 sha256 去重，项目级不参与；文件变化需
  重载插件。
- `engines.dsh` 为 `>=0.2.2-rc.1 <0.3.0`，不满足时跳过并记入 `skippedBundles`。
- 时间由 `dsh-time-context` 注入（Web `standard`/`ptc` 默认挂载，`minimal` 不含），本包不重复注入。

## 验证

- 安装后确认 profile 的 `package.json` 依赖与 bundle 列表包含本包，`cordis.patch.yml` 中 `global-user-constraints-skills`
  行未被禁用。
- 开新会话确认系统提示包含 `global-user-constraints` section；skill 目录可见 21 个 skill，标题与描述可读。
- `dsh --dump-config` 可核对组合后的配置层；`engines.dsh` 变化导致的跳过会记入 `skippedBundles`。

## 边界

- bundle 只读包内 `skills/`、`rules/` 并注册到宿主；不写盘、不联网、不持久化。
- 本 bundle 不注册 `constraints-check` 命令；直接按规则与 skill 审查，不引入另一套命令格式。
- 不修改 `AGENTS.md`，也不写入用户级 rules；卸载即移除 section 与 skill 提供者。
- 注入内容会进入模型上下文，敏感内容不要写进规则正文；只安装可信来源的包并核对 SHA256。
