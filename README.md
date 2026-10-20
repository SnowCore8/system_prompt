# AI 编码代理 system prompt

`AGENTS.md` 是会话开始时读进模型上下文的指令，约束它改代码时的行为：不交空壳、不假报通过、不改未授权文件、危险操作先问。

## 用

放进仓库根目录。工具用固定文件名（`CLAUDE.md`、`QWEN.md`）时装成那个名字，或软链接：

```bash
ln -s AGENTS.md CLAUDE.md
```
