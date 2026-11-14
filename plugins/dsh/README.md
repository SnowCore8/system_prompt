# 用户全局约束：DeepSeek Harness bundle

DSH bundle。安装到 profile 后，以 skill 提供者形式暴露仓库的十一个通用规范 skill。

## 结构

| 路径 | 作用 |
|---|---|
| `package.json`（仓库根） | npm 包与 `dsh.bundle.patch` 声明，版本与另外两包一致 |
| `plugins/dsh/cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `plugins/dsh/src/index.js` | Cordis 插件：`apply(ctx)` 注册 `ctx.skills.registerProvider` |
| `plugins/dsh/test/provider.test.mjs` | 提供者行为测试（`node --test`） |
| `skills/`、`rules/`（仓库根） | 真源，同时被 git 源安装与 zip 打包使用 |

仓库根 `package.json` 就是 git 源安装入口，所以 GitHub 仓库可以直接作为 DSH bundle 安装。

## 安装

### Git 源安装（推荐）

```bash
pnpm dsh plugin --profile web add "github:SnowCore8/system_prompt#v0.6.0"
```

- 私有仓库需要 git 凭据；已登录 `gh` 时先执行 `gh auth setup-git`。
- `#v0.6.0` 可换成 `#master` 或具体 commit，装最新合并用 `#master`。
- pnpm 会按仓库根的 `files` 取包，拿到 `package.json`、`plugins/dsh/src`、`cordis.patch.yml`、
  `skills/` 与 `rules/`。

### 本地目录或 Release zip

```bash
scripts/materialize.sh dsh /tmp/dsh-bundle
dsh plugin --profile web add /tmp/dsh-bundle
```

Release 里的 `global-user-constraints-dsh-<版本>.zip` 解压后就是同样布局，直接把目录传给 `add`。

## 行为

- 行 id 是 `global-user-constraints-skills`，可在 profile 的 `cordis.patch.yml` 里覆盖或禁用。
- 版本准入由 `engines.dsh` 声明（当前 `>=0.2.2-rc.1 <0.3.0`），不匹配会被跳过。
- 约束正文：DSH 的用户级指令链读取 `~/.dsh/AGENTS.md`，把 `rules/global-user-constraints.md`
  复制到该位置即可生效；时间由 DSH 自身注入，本包不重复。
- 卸载：`pnpm dsh plugin --profile web remove @snowcore8/dsh-global-user-constraints`。

## 测试

```bash
node --test plugins/dsh/test/provider.test.mjs
scripts/check.sh
```
