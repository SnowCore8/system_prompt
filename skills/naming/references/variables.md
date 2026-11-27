# 变量、参数与常量

## 1. 变量、参数与常量

- 变量与参数用名词，长度随作用域变化：局部变量一到两个词，公开 API 两到四个词；长名称胜于含糊名称。
- 不编码类型：不用匈牙利命名法，不加 `obj`、`str`、`arr`、`list` 后缀；类型无法表达单位、范围或含义时方加后缀（`timeout_ms`、`amount_cents`）。
- 集合用复数（`users`），映射写明键（`usersById` 而非 `userMap`）；布尔值用肯定的 `is`/`has`/`can`/`should` 加形容词。
- 常量用 UPPER_SNAKE_CASE 并带单位：`MAX_RETRY_COUNT`、`DEFAULT_TIMEOUT_MS`；不使用魔法值。
- 避免单字母与双字母名称、省略元音的写法与辅音连缀；循环索引可以短。
