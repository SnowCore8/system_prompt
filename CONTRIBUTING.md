# 贡献与维护约定

本文件是本仓库的项目维护约定，根 `AGENTS.md` 软链指向本文件，供 DSH 等工作区指令消费者加载。
用户全局约束在 `rules/global-user-constraints.md`，那是仓库的分发内容：Qwen Code 通过
`.qwen/rules/` 读取项目级规则，Qoder 项目级通过 `.qoder/rules` 读取、
用户级安装插件后由 hook 自动注入，均不作为本仓库的贡献规则。

何时阅读：在本仓库改约束、skill、插件或脚本之前；维护者：SnowCore8（仓库所有者）。完成定义：
变更在范围内、`scripts/check.sh` 通过并粘贴真实输出。

## 范围与优先级

- 本文件只约束本仓库的维护工作；若用户级约束已加载，两者冲突时以用户级约束为准。
- 只改被请求的内容；仓库是真源，不另建副本。
- 代码注释与文档注释用中文；引入的第三方代码保留其原文注释。
- Windows 检出必须先启用 `git config core.symlinks true`（或开发者模式），否则软链会落成普通文本文件，
  各工具的 skill 与规则入口会静默失效；`scripts/check.sh` 的软链段会报数量不一致。

## 工作流

1. 改约束、skill 或插件前先读 `README.md` 与对应目录说明。
2. 真源位置：约束正文 `rules/global-user-constraints.md`；skill 真源 `skills/`；命令与注入脚本
   `shared/`；三个包在 `plugins/qoder|qwen|dsh`，包内只放清单、hook 与指向真源的软链。
3. 新增或调整入口时保持软链约定：相对路径、目标在仓库内、不复制第二份、不指向另一软链。
4. 提交前运行 `scripts/check.sh`，失败先修；交付时贴真实输出与退出码。
5. 分支模型为 trunk-based：单人维护，直接提交 `master`，不强制 PR；接入远端后启用 `master` 保护与必需 CI。

## 校验与打包

- 依赖：`python3 -m pip install -r requirements-dev.txt`。
- 全量校验：`scripts/check.sh`，覆盖 Markdown、skill 与 hook 测试、DSH bundle 的 `node --test`、
  shellcheck、ruff、依赖审计（pip-audit）、覆盖率（`--fail-under=90`）、JSON、敏感文件、软链、
  三工具项目级适配与三包清单一致性。缺 `shellcheck`、`node` 或 `qoderclicn` 时对应段会打印「跳过」，
  交付时要说明缺口。
- 单独跑测试：skill 测试
  `python3 -B -m unittest discover -s tests/skill -p 'test_*.py'`；
  hook 测试 `python3 -B -m unittest discover -s tests/hooks -p 'test_*.py'`；
  DSH 包测试 `node --test tests/dsh/provider.test.mjs`。
- 发布：版本为 SemVer，三个清单的 `version` 必须一致；改版本与 CHANGELOG 后打 `v<version>` tag，流程见
  `docs/release.md`。本地出包用 `scripts/dist.sh` 一次构建三个 zip（默认要求干净工作区，
  `--require-tag` 要求 tag 匹配），zip 与 `.sha256` 不入库。

## 输出

- 结论先行；未运行的验证写“未运行”，不粘贴未见过的输出。
