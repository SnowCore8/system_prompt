# 代理项目指令

本文件是代理在本仓库的项目指令。用户全局约束由宿主加载，两者冲突时以用户全局约束为准。人类贡献、治理与发布流程见 `CONTRIBUTING.md`、`GOVERNANCE.md` 与 `docs/release.md`；本文件不重复这些流程。

## 真源与入口

- 唯一真源：约束正文 `rules/global-user-constraints.md`；skill `skills/`；命令与注入脚本 `shared/`；三包 `plugins/` 与根 `package.json`。
- 修改前阅读 `README.md` 与对应目录说明；仓库为唯一真源，不建第二份副本。
- 三端入口全部使用仓库内相对软链：`.qwen/rules`、`.qoder/rules`、`.dsh/skills`、`.qwen/skills`、`.qoder/skills`，以及包内 `skills/`、`commands/`、`scripts/`。不得复制内容或指向另一软链。
- Windows 检出必须先启用 `git config core.symlinks true`，或启用开发者模式；否则软链会落为普通文本，入口静默失效。

## 约束与 skill

- 约束正文以 UTF-8 字节计硬上限 32 KiB（32,768 字节）；超过时按主题提取到对应 skill 的 `references/`，正文只保留摘要与加载指引。`scripts/check.sh` 校验该上限。
- skill 真源为 `skills/<name>/SKILL.md` 与其 `references/`；修改 skill 时同步入口软链，不复制正文。
- 代码注释与文档注释使用中文；第三方引入代码保留原文注释。

## 校验与交付

- 提交前运行 `scripts/check.sh`，失败先修复；交付时粘贴真实输出与退出码。
- 发布、打 tag 与出包按 `docs/release.md`，不得自行发布。
