# 发布手册

发布属于生命周期中的 G5 发布门与 G7 收尾门。G4 验证证据齐备后才能准备发布；发布准备、生产授权、执行、
观测、通告与复盘各留下记录。版本、tag、制品与 npm 包的事实以本文件为准。

维护者：SnowCore8；何时阅读：切版本、打 tag、出包或回滚发布时。

## 发布在生命周期中的位置

| 环节 | 门禁 | 本仓库要做的事 | 证据 |
|---|---|---|---|
| 发布准备 | G4 → G5 | 确认 G4 验证证据、版本位、变更记录与回滚方案 | 校验输出、变更日志、回滚说明 |
| 生产授权 | G5 | 对打 tag、推送、npm publish 与创建 Release 取得逐次明确同意 | 批准记录 |
| 执行 | G5 | `scripts/check.sh`、`scripts/dist.sh --require-tag`、推送 tag、`release` 工作流 | CI/CD 记录、制品与校验和、provenance 与 attestation |
| 观测 | G5 | 核对工作流步骤、Release 附件与 npm 包内容 | 工作流结果、附件清单 |
| 通告 | G5 → G7 | Release 说明、CHANGELOG 版本节、弃用与迁移说明 | Release 页面 |
| 复盘 | G7 | 对照发布目标核对偏差，行动项进入后续变更 | 复盘记录 |

发布到 npm 公共仓库、创建 Release 与推送 tag 都是不可逆操作：已发布的版本不能覆盖，已分发制品无法收回，
只能靠弃用与新版本替代。

## 版本规则

六个清单的版本必须一致：`plugins/qoder/.qoder-plugin/plugin.json`、`plugins/qwen/qwen-extension.json`、
仓库根 `package.json`（DSH bundle）、`npm/qoder/package.json`、`npm/qwen/package.json` 与
`package-lock.json` 的根版本。版本用 `node scripts/bump-version.mjs <version>` 一次修改；`scripts/check.sh`
校验一致，`scripts/dist.sh` 校验三包版本且不推导或改写版本。

| 变更 | 版本位 |
|---|---|
| 规范正文或 skill 的语义不兼容变更、目录结构重组 | major |
| 新增 skill、规则条目或兼容的能力扩展 | minor |
| 错别字、链接、脚本缺陷与文档修正 | patch |

## 发布准备

1. 确认 G4 证据：`scripts/check.sh` 通过，插件校验在装有 `qoderclicn` 的机器上完成。
2. 确定版本位，运行 `node scripts/bump-version.mjs <version>`，在 [CHANGELOG.md](../CHANGELOG.md) 顶部
   加对应版本节。
3. 写明本次发布的变更范围、受影响的使用者、回滚方式与停止条件；R2 变更附独立结论或例外记录。
4. 确认工作区干净，生成目录未提交，`.gitignore` 覆盖本地配置与制品。

## 发布步骤

1. 运行 `node scripts/bump-version.mjs <version>`，并在 CHANGELOG 顶部加对应版本节。
2. 跑 `scripts/check.sh`，确认「全部通过」。
3. 提交 `release: <version>`，工作区保持干净。
4. 打注释 tag：`git tag -a v<version> -m "release <version>"`。
5. 推送：`git push origin master --tags`。
6. GitHub Actions 的 `release` 工作流重跑校验、构建 zip 与 SHA256，把 DSH bundle 与 Qoder、Qwen 两个 zip
   安装包以 provenance 发布到 npm 公共 registry，生成 SBOM（SPDX JSON）与构建来源证明，并把三个 zip、
   SHA256、`THIRD-PARTY-NOTICES.md` 与 SBOM 挂到 Release；需要仓库 secret `NPM_TOKEN`。
7. 下载三个 zip 与对应的 `.sha256` 后，用
   `for p in qoder qwen dsh; do sha256sum -c "se-governance-$p-<version>.sha256"; done` 核对；用
   `gh attestation verify <文件> --repo SnowCore8/system_prompt` 核对构建来源证明。
8. npm 是唯一发布通道；GitHub Packages 不是发布目标。MCP 包 `@snowcore8/se-mcp` 随 DSH bundle 分发，
   也可独立 `npm publish`。

## 发布完成判定

- `release` 工作流成功即视为发布完成：校验、构建、npm publish、SBOM 与 GitHub Release 在同一次运行中完成。
- npm 包附带 provenance，Release 附件带构建来源证明；均可在 GitHub 的 attestations 页面复核。
- 不人工轮询 npm registry；索引传播延迟不属于发布失败。
- 工作流失败时按回滚节处理，并在变更记录中写明失败步骤与后续动作。

## 出包

- `scripts/dist.sh` 只出包，不改写版本；构建归一 mtime、按名称排序并使用 `zip -X`，同一版本同一 tag 的
  制品可复现；制品名 `se-governance-<包名>-<版本>.zip`。
- 默认要求工作区干净；`--allow-dirty` 放行并在文件名加 `-dirty`；浅克隆直接拒绝。
- `--require-tag` 要求 HEAD 正好带有 `v<version>` 注释 tag。
- 默认用 `qoderclicn` 校验组装后的 Qoder 包，缺失时失败；`--no-validate` 跳过校验，CI 发布流水线用它
  换取可重复构建，发布前须在本地补跑校验。
- 每个包只保留最新制品与校验和；zip 与 `.sha256` 不纳入版本库。
- CI 的 `reproducible` 任务在 UTC 与 Asia/Shanghai 两个时区重建同一提交并比对 SHA256。

## npm zip 直链安装

- Qoder 的 HTTPS 直链安装走 npm CDN，URL 必须以 `.zip` 结尾：

  ```bash
  qoderclicn plugins install \
    https://cdn.jsdelivr.net/npm/@snowcore8/se-qoder@<version>/se-governance-qoder-<version>.zip \
    --scope user
  ```

- Qwen 的 zip 从同前缀包下载后安装：

  ```bash
  curl -fLO https://cdn.jsdelivr.net/npm/@snowcore8/se-qwen@<version>/se-governance-qwen-<version>.zip
  qwen extensions install se-governance-qwen-<version>.zip
  ```

- `npm/qoder` 与 `npm/qwen` 只承载同版本 zip 与 `.sha256`，内容与 Release 附件一致。DSH bundle 为
  `@snowcore8/se-dsh`；MCP 包为 `@snowcore8/se-mcp`。

## 观测

- 观测对象是工作流步骤、制品与 Release 附件，不是 npm 索引的可见性。
- 发布后核对：三个 zip 与校验和齐全、SBOM 生成、Release 说明可读、三包版本一致。
- 核对 Release 附件与 npm 包的 provenance/attestation 可验证。
- 仓库不收集使用遥测；安装问题与行为异常来自使用者报告，按 [SECURITY.md](../SECURITY.md) 或普通变更请求
  处理。

## 通告

- Release 说明写明版本、变更范围、破坏性变更的迁移路径与受影响的使用者。
- CHANGELOG 版本节只记录可观察变更。
- 弃用先通告后移除：写明弃用版本、替代方案与移除窗口。旧代包已在 1.0.0 弃用。

## 回滚

- 发布内容有误：先发新的 patch 版本修复，不要复用已发布的版本号或重打同一个 tag。
- 已发布的 tag 与 Release 不可变：禁止删除或移动它们。确需撤回时，发新的 patch 版本弃用旧版本。
- 发布门禁失败时，在发布前删除尚未对外引用的 tag，重新走门禁；已发布后不再删除。
- 安全问题的撤回与披露节奏按 [SECURITY.md](../SECURITY.md) 处理。

## 收益复盘

- 对照发布前写下的目标核对偏差：版本是否按计划发布、变更是否被使用、是否出现安装或升级问题。
- 复盘结论与行动项写入后续变更请求或提交说明，行动项有负责人与到期日。
- 发布过程本身的缺陷进入下一次发布准备，不靠临时记忆。

## 发布检查单

- [ ] G4 证据齐备，`scripts/check.sh` 通过
- [ ] 版本清单与 tag 一致（`node scripts/bump-version.mjs <version>`）
- [ ] CHANGELOG 已加版本节，破坏性变更写明迁移路径
- [ ] 工作区干净，`scripts/dist.sh --require-tag` 通过
- [ ] 生产授权已取得：打 tag、推送、npm publish 与创建 Release
- [ ] `release` 工作流成功（含 npm publish 与 GitHub Release）
- [ ] Release 附件包含 zip、`.sha256` 与 SBOM
- [ ] npm 包带 provenance，Release 附件带构建来源证明
- [ ] `reproducible` 任务通过（跨时区重建一致）
- [ ] 复盘结论与行动项已记录
