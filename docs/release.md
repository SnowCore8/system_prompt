# 发布手册

本仓库用 SemVer 与 tag 发布。三个包的版本必须一致：`plugins/qoder/.qoder-plugin/plugin.json`、
`plugins/qwen/qwen-extension.json` 与 `plugins/dsh/package.json` 的 `version` 由发布者手动修改，
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
6. GitHub Actions 的 `release` 工作流会重跑校验、构建 zip 与 SHA256，并挂到 Release。
7. 用 `sha256sum -c global-user-constraints-<version>.sha256` 核对下载的制品。

本地出包可用 `scripts/dist.sh --require-tag`，要求 HEAD 正好带有 `v<version>` tag。

## 回滚

- 发布内容有误：先发新的 patch 版本修复，不要复用已发布的版本号或重打同一个 tag。
- 必须撤回时：在 GitHub 删除 Release 与 tag，再按新版本号重新走发布流程；已分发制品无法收回，
  在 CHANGELOG 写明受影响的版本与替代版本。
- 安全问题的撤回与披露节奏按 [SECURITY.md](../SECURITY.md) 处理。

## 发布检查单

- [ ] manifest 与 tag 版本一致
- [ ] CHANGELOG 已加版本节
- [ ] `scripts/check.sh` 通过，插件校验在本地通过
- [ ] 工作区干净，`scripts/dist.sh --require-tag` 通过
- [ ] Release 附件包含 zip 与 `.sha256`
