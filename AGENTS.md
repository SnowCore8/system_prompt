# 智能体项目指令

本文件是智能体在本仓库的项目指令。全局用户约束由宿主加载，两者冲突时以全局用户约束为准。人类贡献、治理与发布流程见 `CONTRIBUTING.md`、`GOVERNANCE.md` 与 `docs/release.md`；本文件不重复这些流程。

## 真源与入口

- 唯一真源：约束正文 `rules/global-user-constraints.md`；skill `skills/`；命令与注入脚本 `shared/`；三包 `plugins/`、根 `package.json` 与 npm 平台包 `npm/qoder/`、`npm/qwen/`。
- 修改前阅读 `README.md` 与对应目录说明；仓库为唯一真源，不建第二份副本。
- 三端入口由 `scripts/assemble.sh` 从 `skills/`、`rules/` 复制生成：`.dsh/skills`、`.qoder/rules`、`.qoder/skills`、`.qwen/rules`、`.qwen/skills`。生成目录不提交；不得手写第二份真源。
- 发布包由 `scripts/materialize.sh` 从顶层真源组装；不依赖也不提交软链。

## 约束与 skill

- 约束正文以 UTF-8 字节计硬上限 40 KiB（40,960 字节）；超过时按主题提取到对应 skill 的 `references/`，正文只保留摘要与加载指引。`scripts/check.sh` 校验该上限。
- skill 真源为 `skills/<name>/SKILL.md` 与其 `references/`；修改后运行 `scripts/assemble.sh` 刷新开发入口，不复制正文。
- 代码注释与文档注释使用中文；第三方引入代码保留原文注释。

## 校验与交付

- 写完或改完提示词、规则或 skill 正文后，必须核对逻辑、规则与语义；核对未通过或未执行的，不得交付。
- 提交前运行 `scripts/check.sh`，失败先修复；交付时粘贴真实输出与退出码。
- 发布、打 tag 与出包按 `docs/release.md`，不得自行发布。
