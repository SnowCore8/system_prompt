# 贡献与维护约定

本文件是本仓库的项目维护约定，根 `AGENTS.md` 软链指向本文件，供 DSH 等工作区指令消费者加载。
用户全局约束在 `rules/global-user-constraints.md`，那是仓库的分发内容：Qwen Code 通过
`.qwen/rules/` 读取项目级规则，Qoder 项目级通过 `.qoder/rules` 读取、
用户级按插件 README 激活，均不作为本仓库的贡献规则。

## 范围与优先级

- 本文件只约束本仓库的维护工作；若用户级约束已加载，两者冲突时以用户级约束为准。
- 只改被请求的内容；仓库是真源，不另建副本。
- 代码注释与文档注释用中文；引入的第三方代码保留其原文注释。
- Windows 检出必须先启用 `git config core.symlinks true`（或开发者模式），否则软链会落成普通文本文件，
  各工具的 skill 与规则入口会静默失效；`scripts/check.sh` 的软链段会报数量不一致。

## 工作流

1. 改约束、skill 或插件前先读 `README.md` 与对应目录说明。
2. 真源位置：约束正文 `rules/global-user-constraints.md`；插件 `plugins/global-user-constraints/`；
   skill 真源在插件内，`.qwen/skills/`、`.qoder/skills/`、`.dsh/skills/` 只是软链入口。
3. 新增或调整入口时保持软链约定：相对路径、目标在仓库内、不复制第二份、不指向另一软链。
4. 提交前运行 `scripts/check.sh`，失败先修；交付时贴真实输出与退出码。
5. 分支模型为 trunk-based：单人维护，直接提交 `master`，不强制 PR；接入远端后启用 `master` 保护与必需 CI。

## 校验与打包

- 依赖：`python3 -m pip install -r requirements-dev.txt`。
- 全量校验：`scripts/check.sh`，覆盖 Markdown、skill 与 hook 测试、shellcheck、JSON、敏感文件、
  软链与 DSH/Qwen/Qoder 适配。缺 `shellcheck` 或 `qoderclicn` 时对应段会打印「跳过」，交付时要说明缺口。
- 单独跑测试：skill 测试
  `python3 -B -m unittest discover -s plugins/global-user-constraints/skills/system-prompt-authoring/scripts -p 'test_*.py'`；
  hook 测试在 `plugins/global-user-constraints/` 下运行 `python3 -B -m unittest discover -s scripts -p 'test_*.py'`。
- 打包：`scripts/dist.sh`，zip 制品不入库；插件版本由插件路径提交数推导，默认要求工作区干净，
  加 `--allow-dirty` 才允许从脏工作区打包。

## 输出

- 结论先行；未运行的验证写“未运行”，不粘贴未见过的输出。
