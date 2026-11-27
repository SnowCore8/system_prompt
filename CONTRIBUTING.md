# 贡献与维护约定

本文件是人类贡献者与维护者的约定；智能体项目指令见 `AGENTS.md`，两者分离，本文件不进入模型上下文。约束正文为
`rules/global-user-constraints.md`，随插件分发：Qwen Code 通过 `.qwen/rules/` 读取项目级规则，Qoder 通过
`.qoder/rules` 读取；用户级安装插件后，由插件包提供同一份约束。约束正文不定义本仓库的贡献流程；在本仓库贡献仍须
遵守已加载的全局用户约束。

阅读时机：修改约束、skill、插件或脚本之前。维护者：SnowCore8（仓库所有者）。完成定义：变更在范围内、内容可用
且遵守全局用户约束，`scripts/check.sh` 通过并粘贴真实输出；`check.sh` 是仓库附加门禁。

## 范围与优先级

- 本文件仅约束本仓库的维护工作；与已加载的全局用户约束冲突时，以全局用户约束为准。
- 只修改被请求的内容；仓库为唯一真源，不另建副本。
- 代码注释与文档注释使用中文；第三方引入代码保留其原文注释。
- 开发入口由 `scripts/assemble.sh` 生成到 `.dsh`、`.qoder`、`.qwen`；生成目录不提交，不依赖 Windows `core.symlinks`。

## 工作流

1. 修改约束、skill 或插件前，先阅读 `README.md` 与对应目录说明。
2. 真源位置：约束正文为 `rules/global-user-constraints.md`；skill 为 `skills/`；命令与注入脚本为 `shared/`；Qoder 与
   Qwen 包位于 `plugins/qoder`、`plugins/qwen`，包内只放清单与 hook，安装包由 `scripts/materialize.sh` 从顶层真源
   组装；DSH bundle 的清单为根 `package.json`，`plugins/dsh` 放源码与 patch，构建时复制 `skills/` 与 `rules/`；zip npm
   包清单为 `npm/qoder/package.json` 与 `npm/qwen/package.json`，只承载 zip 与校验和。约束正文以 UTF-8 字节计硬上限
   40 KiB；超限时按主题把规则提取到对应 skill 的 `references/`，正文只保留摘要与加载指引。
3. 新增或调整入口后运行 `scripts/assemble.sh` 重新组装；不手工复制，不提交软链。
4. 提交前运行 `scripts/check.sh`，失败先修复；交付时粘贴真实输出与退出码。
5. 分支模型为 trunk-based：单人维护，直接提交 `master`，不强制 PR；分支保护与必需 CI 见
   [GOVERNANCE.md](GOVERNANCE.md)。

## 新增或改名 skill

- 在 `skills/<name>/` 同步 `SKILL.md`、`references/` 与 `scripts/`；frontmatter 的 `name` 必须与目录名一致。
- 运行 `scripts/assemble.sh` 生成三端开发入口；运行 `scripts/materialize.sh` 验证安装包，不复制正文。
- skill 数量变化时，更新 README 中的计数、`scripts/dist.sh` 的数量断言与 `tests/dsh/provider.test.mjs` 的标题。
- 运行 `scripts/check.sh`；按 [docs/release.md](docs/release.md) 出包，并核对 zip 内 skill 数量与本包入口。

## 校验与打包

- 环境：`python3`、`node` 与 `git`（CI 使用 Python 3.12 与 Node 20）。
- 依赖安装：`python3 -m pip install -r requirements-dev.txt`。
- 全量校验：`scripts/check.sh`，覆盖常驻约束体积（≤40 KiB）、Markdown、skill 与 hook 测试、DSH bundle 的
  `node --test`、shellcheck、ruff、依赖审计（pip-audit）、覆盖率（`--fail-under=90`）、JSON、敏感文件、
  零软链与组装、发布包清单一致性。缺少 `shellcheck` 或 `qoderclicn` 时对应段打印「跳过」；缺少 `python3`、
  `node`、`git` 或任一 Python 校验依赖时，脚本直接退出 2。交付时说明缺口。
- 单独运行测试：skill 测试使用
  `python3 -B -m unittest discover -s tests/skill -p 'test_*.py'`；hook 测试使用
  `node --test tests/hooks/*.test.js`；DSH 包测试使用 `node --test tests/dsh/provider.test.mjs`。
- 发布、版本、tag 与出包流程见 [docs/release.md](docs/release.md)；本地出包使用 `scripts/dist.sh`。
