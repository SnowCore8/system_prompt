# 文件与目录

## 1. 文件与目录

- 名称使用小写，不含空格与版本后缀；每种语言选定一种大小写：Python 与 Rust 模块用 snake_case，Web 资产与文档用 kebab-case，仅语言要求时用 PascalCase。
- 按主要导出或职责命名文件，不按层次命名：用 `user_repository.py` 而非 `db.py`，用 `billing/invoice_calculator.go` 而非 `helpers.go`。
- 目录中集合用复数名词（`users/`、`orders/`），单个功能用单数名词（`billing/`）；除项目已记录边界外避免 `misc/`、`common/`、`utils/`。
- 测试文件与被测单元同名并带语言后缀：`user_service_test.py`、`UserServiceTest.java`、`user-service.test.ts`。
- fixture 放 `fixtures/` 或 `testdata/`，快照放 `__snapshots__/` 或 `snapshots/`，基准文件放 `golden/`。
- 迁移文件带时间戳并保持有序：`20261114093000_add_order_status.sql`。
- 静态资产用 kebab-case，相关时带倍率或尺寸，不编码营销活动或人名：`hero-image@2x.png`、`icon-close.svg`。

| 好 | 差 | 原因 |
|---|---|---|
| `order_repository.py` | `repo2.py` | 说明概念与职责 |
| `billing/invoice_calculator.go` | `helpers.go` | 笼统名称会吸引不相关的代码 |
| `20261114093000_add_order_status.sql` | `migration.sql` | 顺序与意图可见 |
| `user-service.test.ts` | `test1.ts` | 与被测单元和测试运行器约定一致 |
