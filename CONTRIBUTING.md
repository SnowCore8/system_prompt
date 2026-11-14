# 贡献与维护约定

本文件是本仓库的项目维护约定，根 `AGENTS.md` 软链指向本文件，供 DSH 等工作区指令消费者加载。
用户全局约束在 `rules/global-user-constraints.md`，那是仓库的分发内容：Qwen Code 通过
`.qwen/AGENTS.md` 软链读取，Qoder 通过插件规则激活，均不作为本仓库的贡献规则。

## 范围与优先级

- 本文件只约束本仓库的维护工作；若用户级约束已加载，两者冲突时以用户级约束为准。
- 只改被请求的内容；仓库是真源，不另建副本。

## 工作流

1. 改约束、skill 或插件前先读 `README.md` 与对应目录说明。
2. 真源位置：约束正文 `rules/global-user-constraints.md`；插件 `plugins/global-user-constraints/`；
   skill 真源在插件内，`.dsh/skills/` 只是软链入口。
3. 新增或调整入口时保持软链约定：相对路径、目标在仓库内、不复制第二份、不指向另一软链。
4. 提交前运行 `scripts/check.sh`，失败先修；交付时贴真实输出与退出码。

## 校验与打包

- 依赖：`python3 -m pip install -r requirements-dev.txt`。
- 全量校验：`scripts/check.sh`，覆盖 Markdown、skill 与 hook 测试、shellcheck、JSON、软链与 DSH 适配。
- 打包：`scripts/dist.sh`，zip 产物不入库；插件版本由插件路径提交数推导。

## 输出

- 结论先行；未运行的验证写“未运行”，不粘贴未见过的输出。
