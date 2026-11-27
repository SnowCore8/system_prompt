# 发布手册

维护者：SnowCore8；何时阅读：切版本、打 tag 或回滚发布时。

本仓库用 SemVer 与 tag 发布。三个平台包与两个 zip npm 包的版本必须一致：
`plugins/qoder/.qoder-plugin/plugin.json`、`plugins/qwen/qwen-extension.json`、仓库根 `package.json`
（DSH bundle）、`npm/qoder/package.json` 与 `npm/qwen/package.json` 的 `version` 由发布者手动修改；
`scripts/check.sh` 校验五者一致，`scripts/dist.sh` 校验三包版本且不推导或改写版本。

## 版本规则

| 变更 | 版本位 |
| --- | --- |
| 规范正文或 skill 的语义不兼容变更、目录结构重组 | 1.0 起为 major；0.x 阶段递增 minor |
| 新增 skill、规则条目或兼容的能力扩展 | minor |
| 错别字、链接、脚本缺陷与文档修正 | patch |

在 0.x 阶段仍按 SemVer 递增；破坏性变更递增 minor，并在发布说明中给出迁移路径。

## 发布步骤

1. 更新五个清单的 `version`：`plugins/qoder/.qoder-plugin/plugin.json`、`plugins/qwen/qwen-extension.json`、
   `package.json`、`npm/qoder/package.json` 与 `npm/qwen/package.json`；在 `CHANGELOG.md` 顶部加对应版本节。
2. 跑 `scripts/check.sh`，确认「全部通过」；没有 `qoderclicn` 时要在有它的机器上补跑插件校验。
3. 提交 `release: <version>`，工作区保持干净。
4. 打注释 tag：`git tag -a v<version> -m "release <version>"`。
5. 推送：`git push origin master --tags`。
6. GitHub Actions 的 `release` 工作流会重跑校验、构建 zip 与 SHA256，把 DSH bundle 与 Qoder、Qwen 两个
   zip 安装包发布到 npm 公共 registry，生成 SBOM（SPDX JSON）并把三个 zip、SHA256、`THIRD-PARTY-NOTICES.md`
   与 SBOM 挂到 Release；需要仓库 secret `NPM_TOKEN`，三个包版本必须新。
7. 下载三个 zip 与对应的 `.sha256` 后，用
   `for p in qoder qwen dsh; do sha256sum -c "global-user-constraints-$p-<version>.sha256"; done` 核对。
8. npm 是唯一发布通道；GitHub Packages 不是发布目标。

## 发布完成判定

- `release` 工作流成功即视为发布完成：校验、构建、npm publish、SBOM 与 GitHub Release 都在同一次运行中完成。
- 不人工轮询 npm registry；索引传播延迟不属于发布失败，也不以 `npm view` 或网页可见性作为发布门禁。
- 工作流失败时按回滚节处理。

## 出包

- `scripts/dist.sh` 只出包，不改写版本；构建归一 mtime、按名称排序并使用 `zip -X`，
  同一版本同一 tag 的制品可复现。
- 本地出包可用 `scripts/dist.sh --require-tag`，要求 HEAD 正好带有 `v<version>` tag；
  每个包只保留最新制品与校验和，构建新版本时删除旧制品；zip 与 `.sha256` 不纳入版本库。

## npm zip 直链安装

- GitHub Release 资产在私有仓库不可匿名下载；Qoder 的 HTTPS 直链安装走 npm CDN，URL 必须以 `.zip` 结尾：

  ```bash
  qoderclicn plugins install \
    https://cdn.jsdelivr.net/npm/@snowcore8/global-user-constraints-qoder@<version>/global-user-constraints-qoder-<version>.zip \
    --scope user
  ```

- `npm/qoder` 与 `npm/qwen` 只承载同版本 zip 与 `.sha256`，内容与 Release 附件一致；对应包在 `npm publish`
  成功后才可下载。Qwen 先下载 zip 再 `qwen extensions install`；DSH bundle 为
  `@snowcore8/global-user-constraints-dsh`。

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
- [ ] `release` 工作流成功（含 npm publish 与 GitHub Release）
- [ ] Release 附件包含 zip 与 `.sha256`
- [ ] DSH、Qoder 与 Qwen 三个 npm 包已随 `release` 工作流发布
