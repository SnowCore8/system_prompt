# 用户全局约束：DeepSeek Harness bundle

DSH bundle。安装到 profile 后，以 skill 提供者形式暴露仓库的十一个通用规范 skill。

## 结构

| 路径 | 作用 |
|---|---|
| `package.json`（仓库根） | npm 包与 `dsh.bundle.patch` 声明，版本与另外两包一致 |
| `plugins/dsh/cordis.patch.yml` | 插入 skill 提供者行 `global-user-constraints-skills` |
| `plugins/dsh/src/index.js` | Cordis 插件：`apply(ctx)` 注册 `ctx.skills.registerProvider` |
| `plugins/dsh/test/provider.test.mjs` | 提供者行为测试（`node --test`） |
| `skills/`、`rules/`（仓库根） | 真源，同时被 npm 包、git 源安装与 zip 打包使用 |

## 安装

包发布在 npm 公共 registry，安装不需要额外配置：

```bash
cd /home/snow/deepseek-harness
pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@0.8.0
```

装完开新会话；没生效重启 `pnpm dsh web`。

## 更新

- npm 的 registry 元数据保留自定义字段，DSH 插件页能读到 `dsh.bundle`，打开时会列出可用版本并支持一键更新；
- 命令行：`pnpm dsh plugin --profile web add @snowcore8/dsh-global-user-constraints@latest`；
- 卸载：`pnpm dsh plugin --profile web remove @snowcore8/dsh-global-user-constraints`。

## 备选安装方式

Git 源（不会检测更新；私有仓库需 `gh auth setup-git`）：

```bash
pnpm dsh plugin --profile web add "github:SnowCore8/system_prompt#v0.8.0"
```

本地目录或 Release zip：

```bash
scripts/materialize.sh dsh /tmp/dsh-bundle
dsh plugin --profile web add /tmp/dsh-bundle
```

## 发布

- 包内容（十一个 skill 与约束正文）随 npm 公开包发布，仓库本身仍可私有；不要把新增的敏感内容放进 `skills/` 或 `rules/`。
- 发布流水线在 `v*` tag 上执行 `npm publish --access public`，使用仓库 secret `NPM_TOKEN`。
- npm 账号或组织必须拥有 `@snowcore8` scope；已发布版本不能覆盖，必须换新版本号。

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
