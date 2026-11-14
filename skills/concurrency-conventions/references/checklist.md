# 并发审查与排查工作表

本文件是并发 diff 审查与故障排查的速查表：同步原语决策表、死锁诊断工作表、竞态检测器命令与各语言原语对照。它与
`SKILL.md` 配合使用；维度规则在 `references/dimensions.md`，这里只有决策表与操作步骤，不重复维度规则。

## 同步原语决策表

| 场景 | 选用 | 理由 | 注意 |
|---|---|---|---|
| 保护一组字段的临界区，写多读多 | 互斥锁 | 默认互斥，推理简单 | 持锁区间小，不回调不嵌套 |
| 读远多于写、读可并发 | 读写锁 | 读并发，写互斥 | 写频繁时开销反超，先测读写比例 |
| 限制并发访问资源数或有界缓冲 | 信号量 | 只做计数，不保护状态 | 状态保护另加互斥锁 |
| 等待某个状态变为真 | 条件变量 | 挂起等待，避免忙等 | 循环重查谓词，带超时 |
| 单个标量的读改写 | 原子操作 | 无锁的读改写 | 不保护多字段不变量 |
| 数据只有一个所有者 | 通道/队列 | 传递所有权而非共享 | 传递后不再共享引用 |
| 创建后不再改变的值 | 不可变值 | 零竞争 | 创建后不再修改 |

## 死锁诊断工作表

1. 画资源等待图。每个执行流一个节点；执行流持有锁 X 并等待锁 Y 时，画一条从"持有 X 的执行流"指向"持锁 Y 的
   执行流"的边。
2. 找环。有环就是死锁；环上的每一条边都是"某个执行流持锁等待另一把锁"。
3. 破环。任选其一：统一全局锁顺序（消除循环等待）、把等待改成 try-lock 加超时（打破持有并等待）、减少锁数量
   （合并不变量）、把回调与 I/O 移出临界区（消除锁嵌套）。
4. 验证。修复后跑压力测试与检测器；检测器不覆盖死锁时，用带超时的看门狗在卡住时打印每个执行流的锁状态。

## 竞态检测器命令

| 语言/运行时 | 命令或工具 | 覆盖 |
|---|---|---|
| Go | `go test -race` | 数据竞争 |
| C/C++ | ThreadSanitizer（`-fsanitize=thread`） | 数据竞争 |
| Rust | `loom` 或 `cargo miri test` | 数据竞争与交错枚举 |
| Java | 无内置检测器；用并发压力测试与静态工具 | 人工与压力 |
| Python | 无内置检测器；用 `threading` 压力测试与代码审查 | 人工与压力 |

## 各语言原语对照

以下为常见语言的对应原语示例，以各语言文档为准。

| 概念 | Go | Rust | Java | Python | C/C++ |
|---|---|---|---|---|---|
| 互斥锁 | `sync.Mutex` | `std::sync::Mutex` | `ReentrantLock` | `threading.Lock` | `std::mutex` |
| 读写锁 | `sync.RWMutex` | `std::sync::RwLock` | `ReentrantReadWriteLock` | 无内置读写锁 | `std::shared_mutex` |
| 原子操作 | `sync/atomic` | `std::sync::atomic` | `AtomicInteger` 等 | 需持锁模拟 | `std::atomic` |
| 条件变量 | `sync.Cond` | `std::sync::Condvar` | `Condition` | `threading.Condition` | `std::condition_variable` |
| 通道/队列 | `chan` | `std::sync::mpsc` | `BlockingQueue` | `queue.Queue` | 无内置 |
| 事件循环 | goroutine 加运行时 | `tokio`/`async-std` | 虚拟线程或执行器 | `asyncio` | 无内置 |

## 审查前先读

审查并发 diff 前，先读 `references/dimensions.md` 中与该 diff 相关的维度；本工作表只做速查，不重复维度规则。
