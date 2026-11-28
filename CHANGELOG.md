# 变更日志

本文件只记录可观察变更；来源、取证与新旧对照不写入说明性文档。

## 1.0.0（2026-11-28）

- 全新一代：se-governance（软件工程治理套件）取代旧代 global-user-constraints。
- 治理章程重写：8 阶段全生命周期（S0 受理–S7 收尾，门禁 G0–G7）；规则编号改为域前缀体系
  （SEC/AUT/IRR/HON/INT/GAT/EXE/CHG/UNC/OUT）。
- skill 体系重建：24 个（生命周期主链 8 个、编码维度 13 个、智能体工程 3 个），每个带阶段职责、
  门禁证据与维度索引。
- 新增 MCP 服务器 `@snowcore8/se-mcp`：8 个工具（条款审查、风险分级、门禁记录、skill 索引、阶段建议、
  变更评估、发布检查单、复盘模板）。
- hooks、scripts、workflows 全部重写：Markdown 校验器迁至 `scripts/mdcheck`；出包产物更名
  `se-governance-<包>-<版本>.zip`；npm 包名改为 `@snowcore8/se-{dsh,qoder,qwen,mcp}`。
- 旧代包 `@snowcore8/{qoder,qwen,dsh}-global-user-constraints` 弃用，保留在 npm 但不再更新。
- 24 个 skill 的正文与 references 完成逐句语义审查：跨 skill 重复规则改为指向单一管辖方，模糊措辞
  全部可判定化，门禁决定与章程六种决定对齐；skill description 以 UTF-8 字节计不超过 1KB 并固化为契约测试。
- `constraints-check` 命令补齐 frontmatter，修复 Qoder 插件校验告警。
