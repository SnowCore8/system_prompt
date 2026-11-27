# 配套 skill 的加载顺序

配套 skill 的加载顺序可以参照：

`repository-governance-conventions` → `vcs-collaboration-conventions` →
`worktree-collaboration-conventions` → `testing-and-quality-conventions` → `code-style-conventions`、`naming-conventions`、
`comment-conventions` → `security-compliance-conventions`、`documentation-conventions`、
`release-operations-conventions` → `architecture-and-design-conventions`、`project-structure-conventions`、
`api-and-data-conventions`、`performance-conventions`、`concurrency-conventions`。

`debugging-conventions`、`refactoring-conventions`、`prompt-authoring`、`skill-authoring`、
`system-prompt-authoring` 依任务出现时加载。

每一步仅应加载当前任务所需的 skill 与章节，形成可检查的结果后，再进入下一步。上述 skill 构成配套
体系，第三方插件中主题相近的，不替代上述 skill；宿主未提供的，应当说明缺口。一次性加载全部 skill
将占用上下文，不相关规则还会稀释判断。授权边界仍依全局用户约束。
