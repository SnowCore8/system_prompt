# Qoder 安装包

本包只承载 `global-user-constraints` 的 Qoder 插件 zip 与 `.sha256`，供 `qoderclicn plugins install`
通过 HTTPS 直链安装；插件内容与同版本 GitHub Release 附件一致。

```bash
qoderclicn plugins install \
  https://cdn.jsdelivr.net/npm/@snowcore8/qoder-global-user-constraints@<版本>/global-user-constraints-qoder-<版本>.zip \
  --scope user
```

URL 必须以 `.zip` 结尾，CLI 才会按远程地址下载；安装后开新会话生效。插件结构与行为见仓库
`plugins/qoder/README.md`。
