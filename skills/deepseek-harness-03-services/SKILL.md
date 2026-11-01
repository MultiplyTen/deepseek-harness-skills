---
name: deepseek-harness-03-services
description: 在 DeepSeek Harness 中设计、实现或重构可替换的服务能力，连接 Service Definition、Provider 与模型 Tool Consumer，并验证依赖及提供方替换。适用于服务分层和能力组合；简单工具无需独立替换时保留单插件。
---

# DeepSeek Harness：服务与能力组合

把真实需求变成可复用、可替换的 Agent 能力。也可按用户要求边实现边讲解。面向 Codex 的本 Skill 与 DeepSeek Harness 的运行时插件是两种交付物；不要把本目录直接当成 `dsh` 插件安装。

## 先确定边界

1. 检查目标仓库的包管理器、实际安装版本、已有服务定义和相邻实现。当前资料核验于 **2026-11-01**，Harness 仍属技术预览；发现 API 差异时以目标版本接口为准，不把 `master` 当成最新发布版。
2. 先回答需要替换什么：本地/远程后端、存储实现、不同模型提供方，还是只想增加一个工具。没有独立替换或复用需求时，用一个插件完成；不要为了凑三层强拆三个 npm 包。
3. 服务分层和声明依赖时读 [实现指南](references/guide.md) 的“契约与组合”；需要落地示例时读“示例加载与验收”。示例位于 [assets/text-metrics](assets/text-metrics)。

## 实现能力

- **Definition** 拥有服务名称、Request/Result 类型和行为契约。需要 TypeScript `ctx` 属性时，在这里做模块声明合并。不要让公开契约导入具体 Provider。
- **Provider** 实现契约并注册服务。资源在 Provider 的生命周期内创建和清理；业务消费者只依赖 Definition。
- **Consumer** 将服务公开为模型工具或其他调用入口。通过 `inject` 声明必需服务，使用框架的参数定义和工具执行流水线。不要从 Consumer 直接导入 Provider。
- 参数默认值在明确的 `resolve...()` 步骤完成，让 Provider 接收到已确定的请求。保留用户原有输入语义，不把缺省值散落进各后端。
- `defineTool` 的 `parameters` 是字段映射。`execute` 返回与 `output.schema` 相符的规范值；`output.render` 负责模型可见内容。展示字符串不应成为程序再次解析的业务协议。
- 只有当两个 Agent/插件组确实需要同名服务的不同实例时才使用服务隔离。隔离范围要同时包含相关 Provider 与 Consumer，先检查目标版本的 group 配置语法。

## 验证真实边界

使用仓库已有检查命令。对服务变更优先验证：

1. 业务契约在空值、边界输入、Unicode 或故障情况下仍有明确含义。
2. Consumer 没有对具体 Provider 的运行时导入；替换 Provider 时 Consumer 无需改动。
3. 缺少必需服务时 Consumer 不进入 `apply`，服务恢复后能重新加载；不把 YAML 行顺序当成依赖声明。
4. Tool 的参数、规范返回值和模型渲染分别符合预期；Agent 集成时检查真实工具调用记录。
5. 如使用隔离，验证两组请求不会访问对方的服务实例；没有隔离需求就不引入这项配置。

附带示例的 `node --test` 只验证计数业务契约，不证明 Cordis 加载或模型调用成功。缺少目标依赖、构建产物或模型凭据时，完成能做的本地检查并明确剩余集成步骤，不伪称端到端通过。

## 交付

交付可运行的服务、实现、消费入口与组合配置，并说明契约、替换点、执行过的检查和剩余限制。已有仓库优先遵循其目录与测试规范。只有用户需要分发时再制作 bundle/profile；服务拆分本身不要求发布包。

## 官方依据

- [能力的三种角色设计](https://deepseek-harness.github.io/deepseek-harness/develop/practice/)：分层适用条件、依赖方向、显式解析。
- [服务与依赖](https://deepseek-harness.github.io/deepseek-harness/develop/framework/service)：`Service`、`inject`、生命周期及隔离。
- [工具编写参考](https://deepseek-harness.github.io/deepseek-harness/reference/cookbook/adding-a-tool)：参数与规范结果的执行约定。
