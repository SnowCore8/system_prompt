# skill 发布前检查清单

本文件把 skill 交付前的检查项与仓库的自动校验对应起来，避免“本地能跑、打包就坏”。

## 结构检查

- [ ] 入口文件是 `SKILL.md`，位于 `<skill-name>/` 下。
- [ ] frontmatter `name` 与目录名完全一致。
- [ ] `description` 写明适用与不适用场景。
- [ ] `argument-hint` 只在需要补充上下文时出现。
- [ ] references/scripts 只在需要时存在，目录内无空占位文件。

## 内容检查

- [ ] 一个 skill 只服务一类读者与一类任务。
- [ ] 第一屏说明用途、触发与边界。
- [ ] 规则可判定，带阈值或示例。
- [ ] 事实单一权威，跨 skill 用链接而非复制。
- [ ] 正文短，细节在 references。
- [ ] 脚本与测试分离，测试在仓库 `tests/`。

## 与自动校验的对应

| 检查项 | 对应命令或脚本 |
|---|---|
| Markdown 严格格式（200 字符行、列表空格、标题层级） | `scripts/check.sh` 的 Markdown 段 |
| `name` 与目录名一致 | `scripts/check.sh` 的 `check_skill_root` |
| 三端软链数量一致且可解析 | `scripts/check.sh` 的软链与 skill 入口段 |
| 三包版本一致、清单路径存在 | `scripts/check.sh` 的插件清单段 |
| 分发包不含测试、缓存、跨包文件 | `scripts/dist.sh` 的 allowlist 与黑名单 |
| 分发包 skill 数量一致 | `scripts/dist.sh` 的 `len(skills)` 断言 |
| DSH provider 返回全部 skill | `node --test tests/dsh/provider.test.mjs` |

## 打包前手工核对

- [ ] 新增 skill 已接入 `.dsh/skills/`、`.qoder/skills/`、`.qwen/skills/`。
- [ ] README 与清单描述里的 skill 计数已更新。
- [ ] `dist.sh` 的 skill 数量断言、provider 测试标题已更新。
- [ ] CHANGELOG 已加版本节，三包版本一致。
- [ ] 本地 `scripts/dist.sh --allow-dirty` 构建通过，zip 内 skill 数量正确。
- [ ] 无未跟踪的临时产物、缓存或 `.tgz` 残留。

## 发布后核对

- [ ] npm `latest` 指向新版本，元数据含 `dsh.bundle`。
- [ ] npm tarball 内 skill 数量正确，无测试与跨包引用。
- [ ] Release 三个 zip 与 SHA256 已生成。
