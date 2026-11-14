# 用户全局约束：DeepSeek Harness bundle

DSH bundle。安装到 profile 后，以 skill 提供者形式暴露仓库的十一个通用规范 skill。

## 结构

| 路径 | 作用 |
|---|---|
| `package.json` | npm 包与 `dsh.bundle.patch` 声明，版本与另外两包一致 |
| `cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `src/index.js` | Cordis 插件：`apply(ctx)` 注册 `ctx.skills.registerProvider` |
| `test/provider.test.mjs` | 提供者行为测试（`node --test`） |
| `skills/`、`rules/` | 软链到仓库顶层真源 |

## 安装

```bash
scripts/materialize.sh dsh /tmp/dsh-bundle
dsh plugin --profile web add /tmp/dsh-bundle
```

- bundle 直接用 `link:` 安装时软链可用；从 Release zip 解压后是自包含目录，两种方式都行。
- 行 id 是 `global-user-constraints-skills`，可在 profile 的 `cordis.patch.yml` 里覆盖或禁用。
- 版本准入由 `engines.dsh` 声明（当前 `>=0.2.2-rc.1 <0.3.0`），不匹配会被跳过。

## 约束与时间

- skill：十一个 skill 出现在会话目录，模型按需加载正文。
- 约束正文：DSH 的用户级指令链读取 `~/.dsh/AGENTS.md`，把本包的
  `rules/global-user-constraints.md` 复制到该位置即可生效。
- 时间：DSH 自身在会话上下文中提供时间，本包不重复注入。

## 测试

```bash
node --test plugins/dsh/test/provider.test.mjs
scripts/check.sh
```
