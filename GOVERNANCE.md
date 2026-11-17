# 治理

维护者：SnowCore8；何时阅读：需要了解决策、审查或发布规则时。

本文件说明本仓库的维护者、决策方式、审查与发布规则。日常流程与校验要求见
[CONTRIBUTING.md](CONTRIBUTING.md)。

## 维护者

- 维护者：SnowCore8（仓库所有者），负责审查、合并、发布与安全响应。
- 当前为单人维护：没有第二维护者，合入与发布由同一人完成。这是已知单点，
  在增加第二维护者前不对外承诺固定的响应时间。

## 决策

- 规范正文与 skill 语义变更：由维护者决定。改动 `rules/global-user-constraints.md`
  的语义时，提交说明必须写明动机、影响范围与回滚方式。
- 结构、入口、打包与校验变更：由维护者决定，按 `CONTRIBUTING.md` 的软链约定执行，
  并以 `scripts/check.sh` 通过为准入条件。
- 未覆盖的争议：由维护者裁定，并把结论补进文档，避免同类问题重复讨论。

## 审查

- 所有改动经维护者审查后合入；`.github/CODEOWNERS` 在接入 GitHub 远端后生效。
- PR 模板要求粘贴 `scripts/check.sh` 的真实输出与退出码，未运行的验证写「未运行」。
- 涉及规范正文、插件清单或发布脚本的改动，审查时同时核对
  [CHANGELOG.md](CHANGELOG.md) 是否同步。

## 发布

- 版本采用 SemVer，`plugins/qoder/.qoder-plugin/plugin.json`、`plugins/qwen/qwen-extension.json`
  与仓库根 `package.json`（DSH bundle）的 `version` 必须一致；
  发布点是注释 tag `v<version>`，tag 与三个包的版本必须一致。
- 发布流程见 [docs/release.md](docs/release.md)：改版本与 CHANGELOG → 校验 → 提交 → 打 tag → 推送，
  由 `release` 工作流构建 zip 与 SHA256 并挂到 Release。
- `scripts/dist.sh` 只出包，不改写版本；构建归一 mtime、按名称排序并使用 `zip -X`，
  同一版本同一 tag 的制品可复现，本地保留最近三个制品与校验和。
- 分支保护：`master` 要求 `check` 状态通过、禁止强推、要求线性历史；`v*` tag 受保护。
  免费计划的私有仓库不支持分支保护与仓库规则集（API 返回 403），升级到 GitHub Pro 后立即启用；
  在此之前以 `check` 工作流、CODEOWNERS 与 PR 模板约束。
- 对外分发前必须完成：双许可证随包分发、制品校验和、安全报告渠道可达。

## 不提供的文件

- 不提供 `CODE_OF_CONDUCT.md` 与 issue 模板：仓库是单人维护的内部规范仓库，
  没有外部贡献流程。
- 不提供独立的安全响应团队：安全响应由维护者承担，流程见 [SECURITY.md](SECURITY.md)。
