# 第三方声明

维护者：SnowCore8；何时阅读：增删开发依赖或发布前核对声明时。

本仓库运行时不依赖第三方代码；插件包只包含本仓库自己的规则、skill、命令与 hook 脚本。

开发与 CI 校验使用四项第三方依赖：

| 依赖 | 版本 | 许可证 | 用途 |
| --- | --- | --- | --- |
| markdown-it-py | 4.2.0 | MIT | `skills/system-prompt-authoring/scripts/check.py` 的 Markdown 格式校验 |
| ruff | 0.17.5 | MIT | `scripts/check.sh` 的 Python lint 与格式校验 |
| coverage | 7.17.3 | Apache-2.0 | `scripts/check.sh` 的分支覆盖率门禁 |
| pip-audit | 2.10.1 | Apache-2.0 | `scripts/check.sh` 的 Python 依赖漏洞审计 |

这些依赖不随插件包分发，也不进入任何制品。其余涉及的外部工具（Qoder、Qwen Code、
DeepSeek Harness）由使用者自行安装，其许可证与安全策略由各自项目负责。

本仓库自身的双许可证范围见 [LICENSE](LICENSE)，全文见
[LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt) 与 [LICENSE-MIT.txt](LICENSE-MIT.txt)。
