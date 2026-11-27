# MCP 用法

`@snowcore8/se-mcp` 是套件的 MCP 服务器（stdio），提供 8 个工具。安装方式分三端。

## 工具

| 工具 | 参数 | 输出 |
|---|---|---|
| `constraints_check` | `text` | 命中的章程条款编号与标题，附启发式审查免责声明 |
| `risk_classify` | `files?`、`shared?`、`production?`、`irreversible?` | R0/R1/R2 与依据 |
| `gate_record` | `gate`、`decision`、`evidence`、`conditions?`、`owner?`、`nextGate?` | 门禁记录模板 |
| `list_skills` | 无 | 24 个 skill 的名称与触发描述 |
| `lifecycle_stage` | `kind`（question/requirement/design/build/verify/release/operate/retire） | 建议阶段、门禁与最低证据 |
| `change_assessment` | `baseline`、`change`、`reason` | 变更请求与影响评估模板 |
| `release_checklist` | 无 | G5 发布检查单 |
| `retrospective` | 无 | G7 复盘模板 |

审查类输出是启发式静态匹配，不构成人工审查结论。

## Qoder CLI CN

在 `~/.qoder/settings.json`（或项目的 `.qoder/settings.json`）注册：

```json
{
  "mcpServers": {
    "se-governance": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@snowcore8/se-mcp@<version>"]
    }
  }
}
```

## Qwen Code

在 `~/.qwen/settings.json` 注册：

```json
{
  "mcpServers": {
    "se-governance": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@snowcore8/se-mcp@<version>"]
    }
  }
}
```

或使用 `qwen mcp add` 添加。

## DSH

DSH 经 `dsh-mcp-client` 挂载 MCP 服务器；本套件的 DSH bundle 已内置 `mcp/server.mjs`，在本套件的
`cordis.patch.yml` 基础上，把服务器挂到 `dsh-mcp-client` 的配置（command 指向包内 `mcp/server.mjs`）。

## 本地冒烟

```bash
node mcp/server.mjs
```

用 MCP inspector 或任意 MCP 客户端连接 stdio 即可；仓库自带 `tests/mcp/stdio.test.mjs` 做握手与工具
调用冒烟。
