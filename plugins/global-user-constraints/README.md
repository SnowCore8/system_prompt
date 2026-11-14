# 用户全局约束插件

Qoder 插件与 Qwen Code 扩展双端包。安装后由 `SessionStart` hook 注入约束全文，
并在 `SessionStart` 与 `UserPromptSubmit` 注入当前时间；不再需要手动复制规则，
用户级或项目级已经加载同一份约束时自动跳过，避免重复。

## 结构

| 路径 | 作用 |
|---|---|
| `rules/` | 用户全局约束正文（唯一权威来源，随包分发） |
| `.qoder-plugin/plugin.json` | 插件 manifest |
| `skills/system-prompt-authoring/` | 起草与审查指令文件的 skill |
| `skills/naming-conventions/` | 通用命名规范，覆盖代码、API、数据库、配置与提交等维度 |
| `skills/comment-conventions/` | 代码注释规范，覆盖 doc 注释、行内注释、TODO 标记与注释审查 |
| `skills/documentation-conventions/` | 项目文档规范，覆盖 README、ADR、指南、参考文档、变更日志与文档维护 |
| `skills/code-style-conventions/` | 代码风格规范，覆盖格式化与 lint、目录与模块边界、依赖与配置、错误与日志、生成与第三方代码 |
| `skills/api-and-data-conventions/` | 接口与数据规范，覆盖 API 契约、错误模型、幂等与分页、数据库迁移与数据保留 |
| `skills/testing-and-quality-conventions/` | 测试与质量规范，覆盖测试分层、质量门禁与覆盖率、静态检查、本地开发环境 |
| `skills/vcs-collaboration-conventions/` | 版本控制与协作规范，覆盖 Git 工作流、PR、代码审查、分支保护与代码所有权 |
| `skills/release-operations-conventions/` | 发布与运维规范，覆盖版本与发布、变更管理、CI/CD、可观测性、事故响应与备份恢复 |
| `skills/security-compliance-conventions/` | 安全与合规规范，覆盖安全开发、凭据与密钥、许可证与 SBOM、隐私与漏洞披露 |
| `skills/repository-governance-conventions/` | 仓库治理规范，覆盖必需文件与元数据、仓库卫生、治理流程与打包分发 |
| `commands/constraints-check.md` | 手动触发约束审查 |
| `qwen-extension.json` | Qwen Code 原生扩展清单 |
| `hooks/hooks.json` | Qoder 的 hook 配置（`command` + `args`） |
| `hooks/qwen-hooks.json` | Qwen 的 hook 配置（单条 `command` 字符串） |
| `scripts/inject-constraints.py` | 读取包内约束并输出 `additionalContext`，带去重与降级 |
| `scripts/inject-clock.py` | 注入当前本地时间、UTC 偏移、时区与星期 |
| `scripts/test_inject_constraints.py` | 约束注入的表驱动测试 |
| `scripts/test_inject_clock.py` | 时间注入与双端清单的表驱动测试 |

## 生效方式

Qoder 安装：`qoderclicn plugins install <插件目录或 zip> --scope user`；新会话启动时读取
`${QODER_PLUGIN_ROOT}/rules/global-user-constraints.md` 并注入全文（约 32 KB，实测可完整进入上下文）。

Qwen Code 安装：`qwen extensions install <插件目录或 zip>`；扩展清单是 `qwen-extension.json`，
其中的 `hooks` 指向 `hooks/qwen-hooks.json`，同样注入约束与时间。

注入约束前会比对以下位置的同内容文件，命中则跳过：

- Qoder：`~/.qoder-cn/rules/`（国际版 `~/.qoder/rules/`）、`AGENTS.md`、
  `.qoder/rules/`、`AGENTS.local.md`
- Qwen Code：`~/.qwen/rules/`、`~/.qwen/AGENTS.md`、`.qwen/rules/`、`AGENTS.md`、`QWEN.md`
- 以上都从当前目录向上查到 `.git`

所以已经用规则机制配置过约束的用户不会拿到两份；新用户安装即生效。仍支持手动复制规则，
与 hook 二选一，两者同时存在时 hook 自动跳过。

## 时间感知

- 两个时机注入：`SessionStart` 与会话中的每次 `UserPromptSubmit`，保证首轮和长会话都有时间。
- 文本固定为一行：`当前时间：YYYY-MM-DD HH:MM:SS +HH:MM（Asia/Shanghai，星期六）。` 后接
  「需要日期或时间时以此为准；长会话以最近一次注入为准。」
- 时区依次取 `TZ`、`/etc/timezone`、`/etc/localtime` 的 zoneinfo 路径，最后用 `tzname()` 兜底。
- 设计说明见仓库的 [docs/time-awareness.md](../../docs/time-awareness.md)。

## Hook 行为

- Qoder：`SessionStart` 注册约束与时间两个 hook，`UserPromptSubmit` 注册时间 hook；matcher 留空匹配全部来源。
- Qwen：同一组事件写在 `hooks/qwen-hooks.json`，命令是单条字符串并用 `${CLAUDE_PLUGIN_ROOT}` 替换扩展根。
- 读取 stdin 事件 JSON，只使用 `hook_event_name` 与 `cwd`；输出
  `hookSpecificOutput.hookEventName` 与 `hookSpecificOutput.additionalContext`。
- 约束脚本只认 `SessionStart`，时间脚本认 `SessionStart` 与 `UserPromptSubmit`；其它事件静默退出 0。
- 包内规则缺失、payload 非法时静默退出 0；脚本按自身位置推导包根，宿主环境变量缺失也能工作。
- 正文超过 512 KB 时降级为一行提示，要求模型自行读取规则文件（正常正文约 32 KB，不会触发）。
- 解释器用 `python`（PATH 上需有 3.7+），以 `-X utf8` 启动：Windows 只有 `python.exe`，
  该参数固定 stdin/stdout 编码，避免 ANSI 代码页下中文注入失败；`timeout` 为 10 秒。

## 安全边界

- hook 只读：读包内规则与上述去重候选文件，不写盘、不联网、不持久化任何字段。
- 注入的约束全文会进入模型上下文；这是本插件的设计目的，敏感内容不要写进规则正文。
- 解释器缺失或脚本超时时按 hook 失败处理，不阻断会话，但本会话没有注入。
- 安装即执行：只安装可信来源的插件包，并核对发布包附带的 SHA256 校验和。

## Hook 测试

在插件目录下运行：

```bash
python3 -B -m unittest discover -s scripts -p 'test_*.py'
```

测试覆盖：hook 配置指向脚本、全文注入、Qoder/Qwen 两侧规则与 `AGENTS.md` 去重、
非目标事件与非法 payload 静默、缺少规则文件时静默、时间格式与时区、双端清单版本一致。

## 边界

- 约束生效目录：Qoder 用户级 `~/.qoder-cn/rules`（国际版 `~/.qoder/rules`）、项目级 `.qoder/rules`；
  Qwen Code 用户级 `~/.qwen/rules`、项目级 `.qwen/rules`。
- 不要把插件、约束文件或 zip 上传到公网平台；只走企业内网或已批准的分发通道。
- Hook 不拦截工具调用；约束本身仍要求人工审查与真实输出验证。
