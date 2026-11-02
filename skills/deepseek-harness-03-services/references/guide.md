# 服务契约、提供方与消费方

简体中文 | [English](guide.en.md)

核验日期：**2026-11-01**。这是针对官方开发者预览文档整理的原创实施说明和示例，不复制完整手册。执行前仍需核对目标 checkout 的类型接口、README 和包版本；`master`、预发布版本和发布版本不应混称。

## 契约与组合

分层首先是依赖方向，不等于目录数量。一个小项目可以在一个包里放三类模块，等到后端需要独立替换或发布时再分包。

```text
Provider ──实现/依赖──▶ Definition ◀──依赖── Consumer（Tool）
                              ▲
                    对外约定不依赖具体后端
```

Definition 约定“请求什么、返回什么、失败意味着什么”。Provider 决定“在哪执行、怎样执行”。Consumer 决定“模型如何发现和调用”。这使远程后端替换本地后端时，工具接口可以保持稳定。

服务名、模块名和插件行 id 是不同的标识。示例中服务名是 `textMetrics`，工具名是 `text_count`。`inject = ['tools', 'textMetrics']` 让 Consumer 等待两个必需服务；把 Provider 的配置行放在前面不能代替这一声明。

服务消失时，依赖它的插件会被卸载，服务恢复后重新加载。不要在模块级缓存具体 Provider 实例，绕过这套依赖生命周期。可选能力才在使用点通过 `ctx.get()` 查询；核心业务必需能力应声明 `inject`。

## 示例文件

```text
assets/text-metrics/
├── package.json
├── definition.ts           # 服务、请求/结果、显式缺省解析
├── provider.ts             # 本地实现；只依赖 Definition
├── consumer.ts             # 模型工具；只依赖 Definition
├── measure.mjs             # 无框架依赖的纯业务计算
├── measure.d.mts           # measure.mjs 的 TypeScript 声明
└── measure.test.mjs        # 可用 Node 内置测试运行
```

计数定义：按 Unicode 码点计数，不按 UTF-16 单元，也不按用户感知字素计数。`ignoreWhitespace=true` 时先去除 JavaScript `\s` 匹配的空白字符。组合字符和连接 emoji 可能包含多个码点。这是示例的明确契约，不应在其他业务中默认为“中文字数”或“显示字符数”。

`resolveTextMetricsRequest()` 将可选的 `ignoreWhitespace` 解析为必需布尔值。Provider 不再猜测默认值。Consumer 获得 `{ codePoints }` 后，工具的规范值直接返回数字；`output.render` 才把它转换为文本内容。

## 示例加载与验收

### 前提

已有按 [官方 README](https://github.com/deepseek-ai/deepseek-harness) 完成安装和构建的源码 checkout。先读取该 checkout 的 `package.json`，按其实际 engines、packageManager 和构建命令操作，不固定沿用其他版本的要求。本示例不是独立 npm 插件包，`package.json` 仅提供 ESM 标识及本地业务测试命令，没有 `dsh.bundle` manifest。

将整个 `assets/text-metrics` 目录复制到该仓库的 `scratch-plugin/text-metrics`，保留文件间的相对路径。现有同名目录应先检查内容并合并，避免覆盖用户修改。

在 `scratch-plugin/services.patch.yml` 中新增两行插件。以下 `C:/dev/deepseek-harness` 是需要替换的示例仓库路径，实际值应使用正斜杠表示的绝对路径：

```yaml
- insert:
    - id: lesson-text-metrics-provider
      name: 'C:/dev/deepseek-harness/scratch-plugin/text-metrics/provider.ts'
    - id: lesson-text-metrics-consumer
      name: 'C:/dev/deepseek-harness/scratch-plugin/text-metrics/consumer.ts'
```

使用当前官方源码启动方式：

```powershell
pnpm dsh web --patch ./scratch-plugin/services.patch.yml
```

本地插件名使用绝对路径，避免把 patch 文件位置误当成 profile 的模块解析目录。若目标版本不直接加载 `.ts`，按该版本的构建/插件说明生成入口，不自行发明加载参数。

### 无凭据的业务检查

在示例目录执行：

```powershell
node --test measure.test.mjs
```

测试检查空串、空白开关、补充平面字符和组合字符。它不需要模型 API Key，也不会安装依赖。

### Harness 集成检查

1. 在 Web UI 配置已有模型凭据并选择工作区；不要在示例文件中写入密钥。
2. 请求：“必须调用 `text_count`，统计 `你好 Agent`，先保留空白，再忽略空白。”
3. 工具调用的参数应分别携带 `ignoreWhitespace=false` 和 `true`；规范结果应为 `8` 和 `7`。检查调用轨迹，不能以模型自行算对替代工具集成验收。
4. 在一次性开发配置中临时移除 Provider，验证 Consumer 等待服务；恢复 Provider 后再调用。对用户已有配置使用临时 overlay 验证，不重写其主配置。
5. 为真实替换需求添加另一个实现同一 Definition 的 Provider，只更改 Provider 配置，再跑同一契约测试。不要同时将同名 Provider 装入同一服务域，期待框架自动选择。

示例提供一个本地 Provider。第 5 步是业务扩展时的验收方法，不代表包内已经存在或验证了远程 Provider。

## 隔离何时值得引入

当两组插件需要同名服务的不同实例或配置时，使用目标版本的插件 group 和 `isolate`，让每组中的 Provider 与 Consumer 共享自己的服务域。隔离解决服务查找与实例范围，不自动建立进程沙箱或文件权限边界。没有多实例需求时，单服务域更清晰。

## 常见修复

| 现象 | 检查位置 |
| --- | --- |
| Consumer 一直未加载 | `inject` 名字是否与 `super(ctx, 'textMetrics')` 一致，Provider 是否成功激活 |
| TS 看不到 `ctx.textMetrics` | Definition 的模块声明合并是否进入类型图，import 是否丢失 |
| 切换后端还需改工具 | Consumer 是否导入具体 Provider 或把其私有字段写入契约 |
| 工具执行后报输出错误 | `execute` 返回的是规范数字，还是误返回了内容块或字符串 |
| 不同 Agent 意外共用实例 | 是否真的需要服务隔离，Provider 与 Consumer 是否位于同一预期服务域 |

## 来源与时效

以下均为 DeepSeek 官方站点或官方仓库链接，核验于 2026-11-01：

- [能力的三种角色设计](https://deepseek-harness.github.io/deepseek-harness/develop/practice/)：角色边界、依赖关系和显式参数解析。
- [服务与依赖](https://deepseek-harness.github.io/deepseek-harness/develop/framework/service)：必需/可选服务、声明合并和隔离。
- [开发一个工具](https://deepseek-harness.github.io/deepseek-harness/develop/basic/tool)：`defineTool` 的参数与输出。
- [工具编写参考](https://deepseek-harness.github.io/deepseek-harness/reference/cookbook/adding-a-tool)：规范值、模型内容与取消等执行规则。
- [第一个插件](https://deepseek-harness.github.io/deepseek-harness/develop/basic/)：源码加载、本地绝对路径和 patch。
