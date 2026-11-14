# 用户全局约束：DeepSeek Harness bundle

DSH bundle。安装到 profile 后，以 skill 提供者形式暴露仓库的十一个通用规范 skill。

## 结构

| 路径 | 作用 |
|---|---|
| `package.json`（仓库根） | npm 包与 `dsh.bundle.patch` 声明，版本与另外两包一致 |
| `plugins/dsh/cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `plugins/dsh/src/index.js` | Cordis 插件：`apply(ctx)` 注册 `ctx.skills.registerProvider` |
| `plugins/dsh/test/provider.test.mjs` | 提供者行为测试（`node --test`） |
| `skills/`、`rules/`（仓库根） | 真源，同时被 registry 包、git 源安装与 zip 打包使用 |

## 安装

DSH 的更新检查只对 npm registry 包和固定到 40 位 commit 的 git 包生效，所以推荐走
GitHub Packages 私有 registry，这样插件页能看到新版本并一键更新。

### 1. 配置 profile 的 npm 认证

在 `~/.dsh/profiles/web/.npmrc` 写入（token 需要 `read:packages`）：

```ini
@snowcore8:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=<TOKEN>
```

用 `gh auth token` 拿当前 gh token（已含 packages 权限），或建一个带 `read:packages` 的 PAT。

### 2. 安装

```bash
cd /home/snow/deepseek-harness
pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@0.7.0
```

装完开新会话；没生效重启 `pnpm dsh web`。

### 3. 更新

- 插件页会列出 registry 包的可用版本（打开时查询，不后台轮询），可一键更新；
- 或用命令：`pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@latest`；
- 卸载：`pnpm dsh plugin --profile web remove @snowcore8/dsh-global-user-constraints`。

### 备选：Git 源安装（不会检测更新）

```bash
gh auth setup-git
pnpm dsh plugin --profile web add "github:SnowCore8/system_prompt#v0.7.0"
```

tag/branch spec 被 DSH 视为不可更新，升级要手动换 tag 重装。

### 备选：本地目录或 Release zip

```bash
scripts/materialize.sh dsh /tmp/dsh-bundle
dsh plugin --profile web add /tmp/dsh-bundle
```

## 行为

- 行 id 是 `global-user-constraints-skills`，可在 profile 的 `cordis.patch.yml` 里覆盖或禁用。
- 版本准入由 `engines.dsh` 声明（当前 `>=0.2.2-rc.1 <0.3.0`），不匹配会被跳过。
- 约束正文：DSH 的用户级指令链读取 `~/.dsh/AGENTS.md`，把 `rules/global-user-constraints.md`
  复制到该位置即可生效；时间由 DSH 自身注入，本包不重复。

## 测试

```bash
node --test plugins/dsh/test/provider.test.mjs
scripts/check.sh
```
