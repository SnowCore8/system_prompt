# 安全策略

本仓库内容是面向编码代理的规范文本、skill 与一个 Qoder 插件；可执行部分为插件 hooks、
skill 内的 Python 校验脚本与 `scripts/` 下的发布/校验脚本。

## 支持的版本

安全修复只进入 `master` 最新提交，并按 SemVer 发新的 patch 版本（见 README「打包」）。
仓库不维护旧版本分支，也不为历史版本单独回补。

## 报告漏洞

首选 GitHub 的私下漏洞报告：仓库页 Security → Report a vulnerability。私有仓库需要
GitHub Advanced Security 才有该入口；入口不可用时直接邮件联系维护者 snowcore8@gmail.com，
不要开公开 issue，也不要在其他公开渠道披露细节。
报告请包含：

- 受影响的文件或路径；
- 复现步骤与所需环境；
- 影响范围（例如任意命令执行、路径穿越、信息泄露）；
- 建议修复（如有）。

## 处理流程

- 目标时限：2 个工作日内确认收到，5 个工作日内给出初步评估，严重问题 7 个自然日内修复；
  单人维护，时限为尽力而为，不构成 SLA。
- 修复在私有分支完成，发布后再公开细节；默认协调披露期限为 90 天。
- 文档内容的事实错误、措辞争议不属于安全漏洞，按普通 issue 处理。

## 范围

- 在范围内：`plugins/global-user-constraints/hooks/` 与 `scripts/` 下的脚本、
  `plugins/global-user-constraints/skills/*/scripts/` 的校验脚本、发布制品。
- 不在范围内：规范文本的合规性判断、第三方工具（Qoder、Qwen Code、DeepSeek Harness）自身漏洞。
