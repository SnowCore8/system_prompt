# 函数与方法

## 1. 函数与方法

- 动作用动词短语：`sendInvoice`、`parseConfig`；一个名称对应一个动作，`do`、`handle`、`process` 后必须带对象。
- 谓词用布尔形容词：`isExpired`、`hasAccess`；非布尔值不得用 `isX` 形式。
- 工厂与构建器用 `createX`、`XBuilder`；仓库用 `XRepository`；真正的领域服务用 `XService`，外部集成用 `XAdapter`、`XGateway`。
- 错误用 `XError` 或 `XException`；选项、配置与结果用 `XOptions`、`XConfig`、`XResult`。
- 回调与事件处理器的命名遵循语言约定；语言不惯用时，不加 `Async` 后缀。
