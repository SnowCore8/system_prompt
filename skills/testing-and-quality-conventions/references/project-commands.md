# 项目命令（原用户全局约束 CH-8）

本文件收录《用户全局约束》原 CH-8「项目命令」的条款。上述条款现由 `testing-and-quality-conventions` skill
（本 skill）管辖，条款编号沿用原编号，作为本 skill 的规范内容维护。

## CH-8 项目命令

构建与测试命令应当自项目配置读取，包括 `README`、`package.json`、`pyproject.toml`、`Makefile` 或 CI 配置。
代理不得依习惯确定命令。项目命令常与默认值不同，依习惯执行将导致错误。
