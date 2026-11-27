# 全局用户约束：DeepSeek Harness bundle

维护者：SnowCore8。本文只说明安装与运行行为，不定义规则；规则以包内 `rules/global-user-constraints.md` 为准。

安装到 profile 后，以 skill 提供者形式提供二十个通用规范 skill。

## 结构

| 路径 | 作用 |
|---|---|
| `package.json` | npm 包与 `dsh.bundle.patch` 声明 |
| `plugins/dsh/cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `plugins/dsh/src/index.js` | Cordis 插件入口：`apply(ctx)` 注册 skill provider 与 `systemPrompt.section()` |
| `plugins/dsh/src/constraints.js`、`skills.js`、`paths.js`、`constants.js` | 约束 section、skill provider、路径与常量模块 |
| `skills/` | 二十个通用规范 skill |
| `rules/global-user-constraints.md` | 全局用户约束正文 |

## 安装

来自 npm 公共 registry（推荐，插件页可检测更新）：

```bash
pnpm dsh plugin --profile web add @snowcore8/global-user-constraints-dsh@<版本>
```

也可以从 Git 源安装（tag 方式不会检测更新）或解压 Release 里的 dsh zip 后安装目录：

```bash
pnpm dsh plugin --profile web add "github:SnowCore8/system_prompt#v<版本>"
pnpm dsh plugin --profile web add /path/to/global-user-constraints-dsh-<版本>
```

装完开新会话；没生效重启 `pnpm dsh web`。

## 命令

本 bundle 不注册 `constraints-check` 命令；该命令由 Qoder/Qwen 包提供。DSH 中直接按规则与 skill 审查，
不引入另一套命令格式。

## 行为

- 行 id 是 `global-user-constraints-skills`，可在 profile 的 `cordis.patch.yml` 里覆盖或禁用。
- 版本准入由 `engines.dsh` 声明（当前 `>=0.2.2-rc.1 <0.3.0`），不匹配会被跳过。
- 约束正文：安装后由插件在 `apply` 时经 `ctx.systemPrompt.section()` 注册，无需手动复制；只对两个用户级
  `AGENTS.md`（`$DSH_HOME`、`$DSH_AGENTS_HOME`）做 sha256 去重，项目级不参与，文件变化需重载插件。
  时间由 `dsh-time-context` 注入（Web `standard`/`ptc` 默认挂载；`minimal` 不含），本包不重复。

## 安全边界

- bundle 只读包内 `skills/`、`rules/` 并注册到宿主；不写盘、不联网、不持久化。
- 注入的约束全文会进入模型上下文；敏感内容不要写进规则正文。
- 安装即执行：只安装可信来源的包，并核对 SHA256 校验和。
