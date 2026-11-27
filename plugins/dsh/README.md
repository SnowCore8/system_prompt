# se-governance（DSH bundle）

DSH bundle：以 skill 提供者注册 24 个 skill，通过 `systemPrompt.section()` 注入治理章程；用户级
`AGENTS.md` 已含同内容时按 sha256 去重。MCP 服务器随包提供（`mcp/server.mjs`），可经 `dsh-mcp-client`
挂载。

## 组件

| 组件 | 说明 |
|---|---|
| 章程 section | `rules/global-user-constraints.md`；超过 64 KiB 时只注入读取提示 |
| skill 提供者 | 24 个 skill 的索引与按需读取 |
| MCP | `mcp/server.mjs`（stdio），8 个工具；注册见 [docs/mcp-usage.md](../../docs/mcp-usage.md) |

## 安装

```bash
pnpm dsh plugin --profile PROFILE add @snowcore8/se-dsh@<version>
```

## 验证

- 测试：`npm run --silent coverage:js`（含 `tests/dsh/provider.test.mjs`）。
- 组装：`scripts/materialize.sh dsh /tmp/se-dsh`，核对 24 个 skill 与章程、MCP 文件齐全。
