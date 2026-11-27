# @snowcore8/se-qoder

本包只承载 `se-governance` 的 Qoder 插件 zip 与 `.sha256`，供 `qoderclicn plugins install` 的 HTTPS 直链
使用（URL 必须以 `.zip` 结尾）：

```bash
qoderclicn plugins install \
  https://cdn.jsdelivr.net/npm/@snowcore8/se-qoder@<版本>/se-governance-qoder-<版本>.zip \
  --scope user
```

包内只有 zip、`.sha256` 与许可证文本，不含可执行代码。
