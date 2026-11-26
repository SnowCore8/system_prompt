# 全局用户约束：Qoder 插件

维护者：SnowCore8。本文只说明安装与运行行为，不定义规则；规则以包内 `rules/global-user-constraints.md` 为准。

安装后首次 `SessionStart` 把约束写入 Qoder 用户级 `rules/`，内容不同则覆盖；当次会话
桥接全文，后续由 Qoder 原生 rules 加载。`SubagentStart` 在未命中原生规则时全文兜底，
`UserPromptSubmit` 每轮提醒；卸载插件不会自动删除 rules，需手动清理。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | Qoder 插件清单 |
| `hooks/hooks.json` | hook 配置，根目录用 `${QODER_PLUGIN_ROOT}` |
| `rules/global-user-constraints.md` | 全局用户约束正文 |
| `skills/` | 十九个通用规范 skill |
| `commands/` | 手动审查命令 |
| `scripts/` | 规则安装、约束与时间注入脚本 |

以上为安装后的自包含结构；源码包只保留清单、hooks 与说明。

- 发布包：使用 `scripts/materialize.sh qoder` 从顶层真源组装。
- 本地市场：先运行 `scripts/assemble.sh qoder` 填充本目录，再交给 Qoder 的 marketplace；生成目录不提交。

## 安装

```bash
qoderclicn plugins install global-user-constraints-qoder-<版本>.zip --scope user
```

安装后开新会话；首次 `SessionStart` 自动写入用户级 rules，内容不同直接覆盖。插件本身
不带安装/卸载生命周期 hook，因此首次写入发生在会话启动时；卸载插件后需手动删除该文件。

## 卸载

Qoder 插件卸载不会删除已经写入的用户 rules；手动删除对应文件：

```bash
rm ~/.qoder-cn/rules/global-user-constraints.md   # CN
rm ~/.qoder/rules/global-user-constraints.md       # 国际版
```

## 命令

`constraints-check` 读取包内 `rules/global-user-constraints.md`，审查当前请求、方案或待执行命令；
只审查，不执行被审查对象。

## 行为

- `SessionStart`：先运行 `install_constraints.py`，把包内规则写入用户级 rules（CN
  `~/.qoder-cn/rules/`，国际 `~/.qoder/rules/`；内容不同直接覆盖），首次或更新时把全文作为
  `additionalContext` 桥接当前会话；随后 `inject_constraints.py` 发现有同源 rules 时跳过，避免
  重复注入。同一事件还会注入当前本地时间、UTC 偏移、时区与星期。
- `SubagentStart`：用户级或项目级已有同源 rules 时，只发送指向该文件的短指针；没有同源
  rules 时才注入全文，避免与原生 rules 重复。
- `UserPromptSubmit`：每次提示提交提醒 `Never violate global user constraints.`，再注入当前时间；长会话与压缩后仍保持提醒。
- 规则缺失、payload 非法、事件不在范围内时静默退出 0。
- 解释器用 `python`（PATH 上需有 3.9+），`-X utf8` 固定 stdio 编码；`timeout` 为 10 秒。

## 安全边界

- hook 会在首次/内容变化时写用户级 rules，并可能直接覆盖同名文件；除该文件外不写盘、不联网、不持久化。
- 注入的约束全文会进入模型上下文；敏感内容不要写进规则正文。
- 安装即执行：只安装可信来源的包，并核对 SHA256 校验和。
