# 贡献与维护约定

本文件规定本仓库的维护约定。根 `AGENTS.md` 为指向本文件的软链，供 DSH 等工作区指令消费者加载。用户全局约
束位于 `rules/global-user-constraints.md`，属于仓库的分发内容：Qwen Code 通过 `.qwen/rules/` 读取项目级规
则；Qoder 项目级通过 `.qoder/rules` 读取；用户级安装插件后，由 hook 自动注入。上述规则属于分发内容，不另行
定义本仓库的贡献流程；本仓库贡献仍应遵守已加载的用户全局约束。

阅读时机：在本仓库修改约束、skill、插件或脚本之前。维护者：SnowCore8（仓库所有者）。完成定义：变更在范围
内，内容可用且遵守用户全局约束，`scripts/check.sh` 通过并粘贴真实输出；`check.sh` 仅为仓库附加门禁。

## 范围与优先级

- 本文件仅约束本仓库的维护工作；用户全局约束已经加载的，两者冲突时以用户全局约束为准。
- 代理仅应修改被请求的内容；仓库为唯一真源，不得另建副本。
- 代码注释与文档注释使用中文；第三方引入代码保留其原文注释。
- Windows 检出必须先启用 `git config core.symlinks true`，或启用开发者模式；否则软链将落为普通文本文件，
  各工具的 skill 与规则入口将静默失效，`scripts/check.sh` 的软链段将报告数量不一致。

## 工作流

1. 修改约束、skill 或插件前，应当先阅读 `README.md` 与对应目录说明。
2. 真源位置如下：约束正文为 `rules/global-user-constraints.md`；skill 真源为 `skills/`；命令与注入脚本为
   `shared/`；Qoder/Qwen 包位于 `plugins/qoder|qwen`，包内放置清单、hook 与指向真源的软链；DSH bundle 的
   清单为仓库根 `package.json`，`plugins/dsh` 放置源码与 patch，构建时复制 `skills/` 与 `rules/`。约束正文
   以 UTF-8 字节计硬上限 32 KiB；超限时按主题把规则提取到对应 skill 的 `references/`，正文只保留摘要与加载
   指引。
3. 新增或调整入口时，应当保持软链约定：使用相对路径、目标位于仓库内、不复制第二份、不指向另一软链。
4. 提交前应当运行 `scripts/check.sh`，失败先行修复；交付时应当粘贴真实输出与退出码。
5. 分支模型为 trunk-based：单人维护，直接提交 `master`，不强制 PR；接入远端后，启用 `master` 保护与必需
   CI。

## 校验与打包

- 依赖安装：`python3 -m pip install -r requirements-dev.txt`。
- 全量校验：`scripts/check.sh`，覆盖常驻约束体积（≤32 KiB）、Markdown、skill 与 hook 测试、DSH bundle 的
  `node --test`、shellcheck、ruff、依赖审计（pip-audit）、覆盖率（`--fail-under=90`）、JSON、敏感文件、
  软链、三工具项目级适配与三包清单一致性。缺少 `shellcheck`、`node` 或 `qoderclicn` 时，对应段将打印“跳过”，交付时应
  当说明缺口。
- 单独运行测试：skill 测试使用
  `python3 -B -m unittest discover -s tests/skill -p 'test_*.py'`；hook 测试使用
  `python3 -B -m unittest discover -s tests/hooks -p 'test_*.py'`；DSH 包测试使用
  `node --test tests/dsh/provider.test.mjs`。
- 发布：版本采用 SemVer，三个清单的 `version` 必须一致；修改版本与 CHANGELOG 后，创建 `v<version>` tag，
  流程见 `docs/release.md`。本地出包使用 `scripts/dist.sh` 一次构建三个 zip（默认要求干净工作区，
  `--require-tag` 要求 tag 匹配）；zip 与 `.sha256` 不纳入版本库。
