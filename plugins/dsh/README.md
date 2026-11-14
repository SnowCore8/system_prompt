# 用户全局约束：DeepSeek Harness bundle

维护者：SnowCore8；何时阅读：安装或排查本 bundle 时。

安装到 profile 后，以 skill 提供者形式提供十三个通用规范 skill。

## 结构

| 路径 | 作用 |
|---|---|
| `package.json` | npm 包与 `dsh.bundle.patch` 声明 |
| `plugins/dsh/cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `plugins/dsh/src/index.js` | Cordis 插件：`apply(ctx)` 注册 `ctx.skills.registerProvider` |
| `skills/` | 十三个通用规范 skill |
| `rules/global-user-constraints.md` | 用户全局约束正文 |

## 安装

来自 npm 公共 registry（推荐，插件页可检测更新）：

```bash
pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@<版本>
```

也可以从 Git 源安装（tag 方式不会检测更新）或解压 Release 里的 dsh zip 后安装目录：

```bash
pnpm dsh plugin --profile web add "github:SnowCore8/system_prompt#v<版本>"
pnpm dsh plugin --profile web add /path/to/global-user-constraints-dsh-<版本>
```

装完开新会话；没生效重启 `pnpm dsh web`。

## 行为

- 行 id 是 `global-user-constraints-skills`，可在 profile 的 `cordis.patch.yml` 里覆盖或禁用。
- 版本准入由 `engines.dsh` 声明（当前 `>=0.2.2-rc.1 <0.3.0`），不匹配会被跳过。
- 约束正文：把 `rules/global-user-constraints.md` 复制到 `~/.dsh/AGENTS.md` 即可由 DSH
  用户级指令链加载；时间由 DSH 自身注入，本包不重复。
