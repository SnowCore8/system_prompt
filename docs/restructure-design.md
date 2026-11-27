
## JavaScript 统一决策

**决策日期**: 2026-11-27

**决策内容**: 将所有 hook 脚本从 Python 统一为 JavaScript (Node.js ESM)。

**理由**:
- 简化依赖：用户环境已有 Node.js（DSH 必需），无需额外安装 Python
- 统一技术栈：DSH 插件已使用 JavaScript，保持一致性
- 更好的模块支持：ESM 提供更清晰的导入/导出语法
- 性能优势：Node.js 启动速度通常快于 Python

**影响范围**:
- Qoder hook 脚本：`shared/scripts/inject-*.js`
- Qwen hook 脚本：`shared/scripts/inject-*.js`
- 测试文件：`tests/hooks/*.test.js`
- 校验脚本：`scripts/check.sh`（改用 `node --test`）

# global-user-constraints 插件包重构设计规范

## 1. 重构目标

按 Qoder、Qwen Code、DeepSeek Harness 三平台规则重构现有插件包，提升代码质量、平台合规性与可扩展性。

## 2. 现有实现分析

### 2.1 优点
- 真源唯一：`rules/`、`skills/`、`shared/` 不复制第二份
- 三包版本同步：`check.sh` 校验 SemVer 一致性
- 去重逻辑：sha256 比对避免重复注入
- 平台适配：Qwen 用 `constraints/` 避开条件规则限制

### 2.2 待改进
1. **DSH 缺少工具注册**：现有 bundle 只提供 skill provider，未注册新工具
2. **Hook 脚本分散**：Python 脚本逻辑重复（时间注入多处实现）
3. **缺少插件元数据**：图标、详情文档、多语言支持不完整
4. **错误处理**：脚本异常时静默退出，缺少诊断日志
5. **代码组织**：可进一步模块化

## 3. 重构方案

### 3.1 目录结构调整

#### 现有结构
```
plugins/qoder/
├── .qoder-plugin/plugin.json
├── hooks/hooks.json
└── README.md

plugins/qwen/
├── qwen-extension.json
├── hooks/qwen-hooks.json
└── README.md

plugins/dsh/
├── cordis.patch.yml
├── src/index.js
└── README.md

shared/
├── scripts/
│   ├── inject-clock.js
│   ├── inject-constraints.js
│   ├── inject-compact.js
│   └── inject-constraints.js
└── commands/
    └── constraints-check.md
```

#### 重构后结构
```
plugins/qoder/
├── .qoder-plugin/plugin.json
├── hooks/hooks.json
├── scripts/           # 新增：Qoder 专用脚本
│   └── diagnostics.py # 诊断日志工具
├── docs/              # 新增：详情文档
│   └── DETAIL.md
├── locale/            # 新增：多语言支持
│   ├── en.json
│   └── zh.json
├── icon.svg           # 新增：插件图标
└── README.md

plugins/qwen/
├── qwen-extension.json
├── hooks/qwen-hooks.json
├── scripts/           # 新增：Qwen 专用脚本
│   └── diagnostics.py
├── docs/
│   └── DETAIL.md
├── locale/
│   ├── en.json
│   └── zh.json
├── icon.svg
└── README.md

plugins/dsh/
├── cordis.patch.yml
├── src/
│   ├── index.js
│   ├── tools.js       # 新增：工具注册
│   └── diagnostics.js # 新增：诊断日志
├── docs/
│   └── DETAIL.md
├── locale/
│   ├── en.json
│   └── zh.json
├── icon.svg
└── README.md

shared/
├── scripts/
│   ├── common/        # 新增：共享模块
│   │   ├── __init__.py
│   │   ├── time_utils.py
│   │   ├── constraint_utils.py
│   │   └── diagnostics.py
│   ├── inject-clock.js      # 重构：使用共享模块
│   ├── inject-constraints.js
│   ├── inject-compact.js
│   └── inject-constraints.js
└── commands/
    └── constraints-check.md
```

### 3.2 DSH 工具增强

新增两个 DSH 工具，供模型主动调用：

#### 3.2.1 constraints-check 工具
```javascript
// src/tools.js
export function registerTools(ctx) {
  ctx.tools.register({
    name: "constraints-check",
    description: "依全局用户约束审查当前请求、建议或待执行命令",
    parameters: {
      type: "object",
      properties: {
        content: {
          type: "string",
          description: "待审查的内容（请求、建议或命令）"
        }
      },
      required: ["content"]
    },
    async execute({ content }) {
      // 读取约束正文
      // 逐条核对 10 项检查点
      // 返回审查结果
    }
  });
}
```

#### 3.2.2 security-scan 工具
```javascript
export function registerSecurityScan(ctx) {
  ctx.tools.register({
    name: "security-scan",
    description: "扫描文件路径，检测敏感文件访问（*.pem, *.key, .env 等）",
    parameters: {
      type: "object",
      properties: {
        paths: {
          type: "array",
          items: { type: "string" },
          description: "待扫描的文件路径列表"
        }
      },
      required: ["paths"]
    },
    async execute({ paths }) {
      // 检查路径是否匹配敏感模式
      // 返回扫描结果与风险提示
    }
  });
}
```

### 3.3 共享脚本模块化

将重复逻辑提取到共享模块：

```python
# shared/scripts/common/time_utils.py
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

def current_time() -> datetime:
    """获取当前时间，支持 TZ 环境变量"""
    tz = os.environ.get("TZ", "").strip().lstrip(":")
    if tz:
        try:
            return datetime.now(ZoneInfo(tz))
        except (ImportError, KeyError, OSError, ValueError):
            pass
    return datetime.now().astimezone()

def timezone_name(now: datetime) -> str:
    """获取 IANA 时区名称"""
    # ... 实现细节
    pass

def timestamp(now: datetime) -> str:
    """格式化为 DSH 风格时间戳"""
    # ... 实现细节
    pass
```

```python
# shared/scripts/common/constraint_utils.py
import hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    """计算文件 sha256"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def should_skip_injection(target: Path, source: Path) -> bool:
    """判断是否应跳过注入（内容已存在）"""
    if not target.is_file():
        return False
    return sha256_file(target) == sha256_file(source)

MAX_BYTES = 40 * 1024

def validate_constraints_size(data: bytes) -> bool:
    """验证约束正文未超过 40 KiB 硬上限"""
    return len(data) <= MAX_BYTES
```

```python
# shared/scripts/common/diagnostics.py
import sys
from typing import Optional

def log_debug(message: str, enabled: bool = False) -> None:
    """调试日志，默认关闭"""
    if enabled:
        print(f"[DEBUG] {message}", file=sys.stderr)

def log_error(message: str, exception: Optional[Exception] = None) -> None:
    """错误日志"""
    print(f"[ERROR] {message}", file=sys.stderr)
    if exception:
        print(f"  {exception}", file=sys.stderr)
```

### 3.4 插件元数据

#### 3.4.1 图标设计
遵循 `references/artwork.md` 规范：
- SVG 格式，256 KiB 以内
- 简洁几何图形，代表"约束"与"安全"
- 配色：深蓝（信任）+ 绿色（合规）

#### 3.4.2 详情文档
```markdown
# docs/DETAIL.md

## 功能

本插件提供三项核心能力：

1. **约束注入**：会话启动时自动注入全局用户约束
2. **时间感知**：注入当前时间，支持时区感知
3. **Skill 加载**：提供 20 个通用规范 skill

## 安装

### Qoder
```bash
qoderclicn plugins install global-user-constraints-qoder-VERSION.zip --scope user
```

### Qwen Code
```bash
qwen extensions install global-user-constraints-qwen-VERSION.zip
```

### DSH
```bash
pnpm dsh plugin --profile PROFILE add @snowcore8/dsh-global-user-constraints@VERSION
```

## 行为

- SessionStart：注入约束与时间
- UserPromptSubmit：刷新时间
- 去重：sha256 比对，避免重复注入

## 限制

- 约束正文硬上限 40 KiB
- Qoder 首次 SessionStart 写入用户级 rules
- Qwen 通过 hook 注入，非原生 rules
```

#### 3.4.3 多语言支持
```json
// locale/en.json
{
  "meta": {
    "title": "Global User Constraints",
    "description": "Enforces global user constraints across Qoder, Qwen Code, and DSH sessions.",
    "detail": "docs/DETAIL.md"
  }
}
```

```json
// locale/zh.json
{
  "meta": {
    "title": "全局用户约束",
    "description": "在 Qoder、Qwen Code 与 DSH 会话中执行全局用户约束。",
    "detail": "docs/DETAIL.md"
  }
}
```

### 3.5 错误处理增强

所有 hook 脚本增加诊断日志：

```python
# 示例：inject-clock.js 重构后
import sys
from common.diagnostics import log_debug, log_error
from common.time_utils import current_time, timestamp, timezone_name

def main():
    try:
        log_debug("Starting inject_clock hook")
        now = current_time()
        zone = timezone_name(now)
        text = format_time_block(now, zone)
        output = build_output(text)
        sys.stdout.buffer.write(json.dumps(output).encode("utf-8"))
        log_debug("Successfully injected time")
    except Exception as e:
        log_error("Failed to inject time", e)
        # 静默退出 0，不阻断会话
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 4. 迁移策略

### 4.1 向后兼容
- 保持现有 hook 事件与输出格式
- 保持 `constraints-check` 命令签名
- 保持 skill 目录结构

### 4.2 渐进式迁移
1. **阶段 1**：重构共享脚本，提取共享模块
2. **阶段 2**：重构三包 hook 脚本，使用共享模块
3. **阶段 3**：添加 DSH 工具注册
4. **阶段 4**：添加插件元数据（图标、详情、多语言）
5. **阶段 5**：验证与测试

### 4.3 版本管理
- 重构后版本号升至 `0.45.0`（minor 版本，表示新功能）
- CHANGELOG 记录重构变更
- 三包版本保持同步

## 5. 验收标准

1. **功能验收**
   - [ ] 约束注入正常工作（Qoder/Qwen/DSH）
   - [ ] 时间注入正常工作
   - [ ] 20 个 skill 正常加载
   - [ ] `constraints-check` 命令可用（Qoder/Qwen）
   - [ ] DSH 新增工具可用

2. **代码质量**
   - [ ] `scripts/check.sh` 全部通过
   - [ ] 无 shellcheck 告警
   - [ ] 无 ruff 告警
   - [ ] 零软链、零重复代码

3. **平台合规**
   - [ ] Qoder 插件通过 `plugins validate`
   - [ ] Qwen 扩展正常加载
   - [ ] DSH bundle 正常安装

4. **文档完整性**
   - [ ] 三包 README 更新
   - [ ] CHANGELOG 记录变更
   - [ ] 设计规范文档完成

## 6. 待确认事项

在实施前，需要确认以下事项：

1. **DSH 工具增强**：是否同意新增 `constraints-check` 与 `security-scan` 两个工具？
2. **图标设计**：是否由我按 `artwork.md` 规范生成 SVG 图标？
3. **多语言范围**：是否只支持中英文，还是需要更多语言？
4. **迁移时机**：是否立即开始重构，还是等待其他变更合并后？

## 卸载行为

本插件采用"干净卸载"策略，确保卸载后不留任何残留文件：

| 平台 | 卸载行为 | 说明 |
|------|---------|------|
| Qoder | 无残留 | 通过 hook 注入约束，不修改用户文件系统 |
| Qwen | 无残留 | 通过 hook 注入约束，不修改用户文件系统 |
| DSH | 无残留 | 通过 systemPrompt.section 注入，不修改用户文件系统 |

**对比旧方案**：旧方案会安装约束文件到 `~/.qoder/rules/` 等用户级目录，卸载后需手动删除。
新方案完全通过 hook 或插件机制在运行时注入，卸载即生效，无需任何清理操作。

**去重机制**：如果项目级 `AGENTS.md` 或 `QWEN.md` 已包含同内容约束，hook 会自动跳过注入，避免重复。
