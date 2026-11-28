# 本地与 CI 对齐

## 1. 本地与 CI 对齐

- 一条命令构建环境：bootstrap 或构建脚本目标同时供本地与 CI 调用，两条路径读取相同的工具版本、环境变量
  与服务镜像。
- 固定版本：工具链、服务镜像与 fixture 在仓库中固定，禁止 `latest` 浮动；本地通过而 CI 失败属于一致性
  缺陷，先修一致性再加校验。
- 测试数据合成化：使用合成值与 `example.test.invalid` 地址，每次运行分配唯一命名空间并在结束后清理。
- 固定动作与安全边界：第三方 action 固定到完整提交 SHA；工作流最小权限与 fork 隔离归 `security-compliance`，
  发布环境与云凭据（OIDC）归 `release-operations`。
