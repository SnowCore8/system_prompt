# 测试与提交

## 1. 测试与提交

- 测试函数名写行为加条件：`test_list_orders_returns_empty_for_new_user`；测试文件的命名见维度 1（`references/files.md`）。
- 测试替身按含义区分：`Fake` 是可运行的替代实现，`Stub` 返回预设值，`Mock` 记录并断言调用，`Spy` 记录调用；名称必须与行为匹配。
- 提交标题用 `type(scope): summary`，type 取小写受控集合（`feat`、`fix`、`refactor`、`docs`、`test`、`chore`）；summary 用祈使式，不超过 72 个字符。
- 提交正文另起一段说明原因，不重复标题；提交命名只裁定措辞，提交拆分与合并流程由 `vcs-collaboration` 裁定。
- issue 引用写作 `#123`，跨仓库写作 `owner/repo#123`，外部跟踪器用完整链接；裸的“以后修复”不属于引用。
