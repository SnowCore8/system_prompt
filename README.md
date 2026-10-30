# AI 编码代理 system prompt

本仓库维护全局约束、`system-prompt-authoring` skill，以及把两者打包在一起的用户级 Qoder 插件。插件包是唯一事实源；根 `AGENTS.md` 和项目 skills 路径都是指向它的软链。改规则、改 skill 或改插件前先读本文件。维护者：仓库所有者。

Markdown 没有构建步骤；格式机检依赖 `markdown-it-py`。插件 zip 由 `scripts/dist.sh` 打包，产物在仓库根目录。

## 目录

| 路径 | 作用 |
|---|---|
| `AGENTS.md` | 指向 `.qoder/plugins/global-user-constraints/rules/` 下规则文件的软链 |
| `.qoder/plugins/global-user-constraints/` | 插件包：规则、skill、审查命令、时间注入 hook |
| `.qoder/plugins/global-user-constraints/rules/global-user-constraints.md` | 始终生效的规则正文 |
| `.qoder/plugins/global-user-constraints/skills/system-prompt-authoring/` | skill 源 |
| `.qoder/skills/` | 指向插件 `skills/` 目录的软链 |
| `.qwen` | 指向 `.qoder` 的兼容软链，供只认 `.qwen` 的工具使用 |
| `scripts/dist.sh` | 分发脚本：编译两个平台的 hook 二进制，按插件提交数生成版本，按当前 commit id 打包到仓库根目录 |
| `scripts/build-hooks.sh` | 编译 hook 二进制：本机 gcc 出 POSIX 版，mingw-w64 交叉编译 Windows 版 |
| `scripts/test_inject_time.py` | hook 二进制（Linux 版）的表驱动测试，不随插件分发 |

## 编辑

1. 改规则：编辑 `.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`；`AGENTS.md` 跟随软链。
2. 改 skill：编辑 `.qoder/plugins/global-user-constraints/skills/system-prompt-authoring/`；`.qoder/skills` 跟随软链。
3. 不要另建副本。路径经软链解析时，改目标，不改副本。

## 验证

```bash
python3 .qoder/skills/system-prompt-authoring/script/check.py --strict AGENTS.md
python3 -m unittest discover -s .qoder/skills/system-prompt-authoring/script
scripts/build-hooks.sh
python3 -m unittest scripts.test_inject_time
```

机检只验证 Markdown 格式；内容规则 S1–S13 按 `SKILL.md` 人工核对。

## 分发

```bash
scripts/dist.sh
```

版本由当前 `HEAD` 推导：`0.1.<改动插件的提交数（不含 plugin.json）>`，写回 manifest 后按短 commit id 打成两个包：`global-user-constraints-<commit>-linux-x64.zip` 与 `global-user-constraints-<commit>-windows-x64.zip`。
同一 commit 重复运行版本不变；新提交只要改动插件目录，版本加一。
每份 zip 只含本平台二进制并改写 hook `command`；Windows 交叉编译依赖 `mingw-w64`（`apt install mingw-w64`），缺失时打包失败。
版本写回本身不算工作区改动；其他未提交改动会让文件名追加 `-dirty`，并提示到 stderr。
打包后检查 zip 结构并运行 Qoder 离线校验，`--no-validate` 跳过校验；校验器不存在时脚本会提示并跳过。
版本写回要随代码提交；zip 与 `.qoder/plugins/global-user-constraints/scripts/bin/` 是生成物，已在 `.gitignore` 中忽略。

插件包内容与 hook 行为见插件 [README](.qoder/plugins/global-user-constraints/README.md)。不要把规则文件、插件或 zip 上传到公网平台；走企业内网或已批准的通道。

企业 `global-security-guard` 是独立的托管（managed）插件；本仓库不关闭也不替代它。
