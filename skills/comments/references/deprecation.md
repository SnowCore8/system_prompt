# 弃用声明

## 1. 弃用声明

- 使用语言自带的弃用机制，并写明替代项与移除版本：`@deprecated Use create_invoice; removed in v3.0.`
- 仅有 `@deprecated` 而没有替代项的声明使调用方无路可走；替代项必须可执行。
- 弃用时机、移除窗口与公告位置由 `release-operations` 裁定；本文件只规定标记的语法与替代项写法。
- 弃用声明随发布说明一起公告；移除后删除该声明，不留永久的 `legacy_` 前缀。
