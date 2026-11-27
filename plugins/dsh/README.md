# 全局用户约束：DeepSeek Harness bundle

维护者：SnowCore8。本文只说明安装与运行行为，不定义规则；规则以包内 `rules/global-user-constraints.md` 为准。

## 结构与安装

| 路径 | 作用 |
|---|---|
| `package.json` | npm 包与 `dsh.bundle.patch` 声明 |
| `plugins/dsh/cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `plugins/dsh/src/` | Cordis 入口与模块（`index.js`、`constraints.js`、`skills.js`、`paths.js`、`constants.js`） |
| `skills/` | 二十一个通用规范 skill |
| `rules/global-user-constraints.md` | 全局用户约束正文 |

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

## 行为

- 行 id 为 `global-user-constraints-skills`，可在 profile 的 `cordis.patch.yml` 覆盖或禁用；
  `engines.dsh` 不匹配时跳过（当前 `>=0.2.2-rc.1 <0.3.0`）。
- 约束正文由插件在 `apply` 时经 `ctx.systemPrompt.section()` 注册，无需手动复制；只对两个用户级
  `AGENTS.md`（`$DSH_HOME`、`$DSH_AGENTS_HOME`）做 sha256 去重，项目级不参与，文件变化需重载插件。
- 时间由 `dsh-time-context` 注入（Web `standard`/`ptc` 默认挂载，`minimal` 不含），本包不重复。

## 命令

本 bundle 不注册 `constraints-check` 命令；直接按规则与 skill 审查，不引入另一套命令格式。

## 安全边界

- bundle 只读包内 `skills/`、`rules/` 并注册到宿主；不写盘、不联网、不持久化。
- 注入内容会进入模型上下文，敏感内容不要写进规则正文；只安装可信来源的包并核对 SHA256。
