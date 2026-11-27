# Qwen Code 安装包

本包只承载 `global-user-constraints` 的 Qwen Code 扩展 zip 与 `.sha256`，供下载后安装；扩展内容与同版本
GitHub Release 附件一致。

```bash
curl -fLO https://cdn.jsdelivr.net/npm/@snowcore8/qwen-global-user-constraints@<版本>/global-user-constraints-qwen-<版本>.zip
qwen extensions install global-user-constraints-qwen-<版本>.zip
```

安装后开新会话生效。扩展结构与行为见仓库 `plugins/qwen/README.md`。
