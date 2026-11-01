---
name: deepseek-harness-01-config
description: 为 DeepSeek Harness 插件设计、实现或修复配置字段、Schemastery 校验和本地配置覆盖层，也用于带练插件配置。用于插件自身配置，不用于模型 API Key 设置或插件分发。
---

# DeepSeek Harness 插件配置

把已有插件中的部署差异变成可验证的配置，使用户能调整行为而无需改源码。按用户要求选择实施、排错或教学；不要只给概念清单。

## 开始前

1. 查看目标插件、实际 Harness 版本或 checkout、已有 overlay 和启动方式；先保留已有字段与配置行。
2. 这是开发者预览框架。依据项目当前依赖和接口核对本技能示例，不能把 `master` 示例当成任意已发布版本的兼容承诺。
3. 没有现有项目时，使用 [配置带练与排错](references/guide.md) 中的源码前提和示例。先区分教学示例与实际环境搭建，按照当前任务授权准备依赖和模型连接。

## 实施流程

- 区分插件配置与工具调用参数：插件配置决定实例行为；`parameters` 定义每次模型调用携带的数据。先写出字段名、类型、默认值及一个行为例子。
- 依照当前官方 API 导出同名的 `Config` 类型与运行时 schema；本技能基线使用 `@deepseek-ai/schemastery`。schema 提供默认值并拒绝无效值，`apply(ctx, config)` 接收解析后的配置。不要用普通对象替代 Standard Schema。
- 只开放真实需要变化的设置。不要把工具输入、服务依赖或凭证内容硬塞进普通配置字段；服务用 `inject` 声明依赖。
- 在业务逻辑中使用解析后的配置。显式的 `false` 必须保留；不要用 `value || true` 吞掉它。工具的返回值仍应符合 `output.schema`，再由 `output.render` 转成模型内容。
- 通过独立 overlay 插入本地插件；本地源码路径写绝对路径。可以运行 [write_overlay.py](scripts/write_overlay.py) 生成本例覆盖层。已有项目中只改目标插件行；改变已有行的 `config` 前核对是否需要重述整行配置，避免丢失其他键。
- 验证默认值、显式覆盖和非法输入。代码计数单元验证不能替代真实 Harness 的 schema 校验与加载验证；分别报告完成了哪些层次。

## 教学与验收

学习模式先用 `ignoreWhitespace` 布尔值演示“同一工具、不同实例行为”，再让用户预测省略、`false`、`true` 三种结果，最后解释为什么 YAML 字符串 `"false"` 应判为无效布尔值。

验收至少覆盖：

- 工具未传配置时保留空白；配置 `ignoreWhitespace: true` 时忽略正则 `\s` 匹配的空白。
- `你好 Agent` 的结果分别为 `8` 与 `7`；`你 好\nAgent` 的结果分别为 `9` 与 `7`。
- 非法布尔配置被运行时 schema 拒绝，或明确记录尚未进行这项集成验证。
- 配置变更后的验证要能看到工具调用记录与工具结果，不能把模型自行算出的回答当成工具已执行的证据。

## 资源与交付

- [guide.md](references/guide.md)：需要启动、排查不生效、教学练习或查官方来源时读取。
- [assets/example/plugin.ts](assets/example/plugin.ts)：按当前 API 编写的可配置工具入口；复制时保留同目录的计数模块和类型声明。
- [scripts/write_overlay.py](scripts/write_overlay.py)：生成绝对路径 overlay；默认拒绝覆盖已有文件，避免改坏现有配置。

交付目标插件改动、配置字段与行为说明、实际验证结果，以及未验证的运行环境或 API 差异。需要发布可安装组合包时转入打包流程；本技能不发布 npm 包。
