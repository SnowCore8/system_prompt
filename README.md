# AI 编码代理 system prompt

本仓库只有两类内容：给编码代理读的指令基线，和审计这份基线的 skill。没有构建步骤，没有运行时依赖，改完 Markdown 就是改完。

## 文件

| 文件 | 作用 | 什么时候读 |
|---|---|---|
| `AGENTS.md` | 指令基线本体，会话开始时读进模型上下文，约束改代码时的行为 | 改规则时；想让代理遵守某条时 |
| `README.md` | 本文件，说明仓库里有什么、怎么用 | 第一次接触这个仓库 |
| `.qwen/skills/system-prompt-authoring/SKILL.md` | 审计与起草 `AGENTS.md` 的流程、S1–S13 规则表、机检脚本用法 | 要改 `AGENTS.md` 之前 |
| `.qwen/skills/system-prompt-authoring/references/provenance.md` | S1–S13 每条规则的厂商文档原句 | 某条规则的出处被质疑时 |
| `.qwen/skills/system-prompt-authoring/script/check.py` | 机检脚本，判 Markdown 结构与 S1–S13 | 改完 `AGENTS.md` 后 |
| `.qwen/skills/system-prompt-authoring/script/test_check.py` | `check.py` 的自测用例 | 改 `check.py` 时 |

## 用

把 `AGENTS.md` 放进目标仓库根目录。工具用固定文件名（`CLAUDE.md`、`QWEN.md`）时装成那个名字，或软链接：

```bash
ln -s AGENTS.md CLAUDE.md
```

改完跑机检：

```bash
python3 .qwen/skills/system-prompt-authoring/script/check.py AGENTS.md
python3 -m unittest discover -s .qwen/skills/system-prompt-authoring/script
```
