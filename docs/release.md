# 发布手册

维护者：SnowCore8；何时阅读：切版本、打 tag 或回滚发布时。

本仓库用 SemVer 与 tag 发布。三个包的版本必须一致：`plugins/qoder/.qoder-plugin/plugin.json`、
`plugins/qwen/qwen-extension.json` 与仓库根 `package.json`（DSH bundle）的 `version` 由发布者手动修改，
`scripts/dist.sh` 只读取和校验，不推导或改写。

## 版本规则

| 变更 | 版本位 |
| --- | --- |
| 规范正文或 skill 的语义不兼容变更、目录结构重组 | major |
| 新增 skill、规则条目或兼容的能力扩展 | minor |
| 错别字、链接、脚本缺陷与文档修正 | patch |

在 0.x 阶段仍按 SemVer 递增，`0.2.0` 表示发布体系切换到 tag 发布。

## 发布步骤

1. 更新 manifest 的 `version`，在 `CHANGELOG.md` 顶部加对应版本节。
2. 跑 `scripts/check.sh`，确认「全部通过」；没有 `qoderclicn` 时要在有它的机器上补跑插件校验。
3. 提交 `release: <version>`，工作区保持干净。
4. 打注释 tag：`git tag -a v<version> -m "release <version>"`。
5. 推送：`git push origin master --tags`。
6. GitHub Actions 的 `release` 工作流会重跑校验、构建 zip 与 SHA256，把 DSH bundle 发布到
   npm 公共 registry，生成 SBOM（SPDX JSON）并把三个 zip、SHA256、`THIRD-PARTY-NOTICES.md` 与
   SBOM 挂到 Release；需要仓库 secret `NPM_TOKEN`，包版本必须新。
7. 用 `sha256sum -c global-user-constraints-<version>.sha256` 核对下载的制品。
8. GitHub Packages 不再发布，旧包已删除；npm 是唯一发布通道。

本地出包可用 `scripts/dist.sh --require-tag`，要求 HEAD 正好带有 `v<version>` tag。

## 回滚

- 发布内容有误：先发新的 patch 版本修复，不要复用已发布的版本号或重打同一个 tag。
- 已发布的 tag 与 Release 不可变：禁止删除或移动它们。确需撤回时，发新的 patch 版本弃用旧版本，
  在 CHANGELOG 写明受影响的版本与替代版本；npm 已发布的版本不能覆盖，已分发制品无法收回，
  只能靠弃用与新版本替代。
- 发布门禁失败时，在发布前删除尚未对外引用的 tag，重新走门禁；已发布后不再删除。
- 安全问题的撤回与披露节奏按 [SECURITY.md](../SECURITY.md) 处理。

## 发布检查单

- [ ] manifest 与 tag 版本一致
- [ ] CHANGELOG 已加版本节
- [ ] `scripts/check.sh` 通过，插件校验在本地通过
- [ ] 工作区干净，`scripts/dist.sh --require-tag` 通过
- [ ] Release 附件包含 zip 与 `.sha256`
