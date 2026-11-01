# 配置带练与排错

核验日期：2026-11-01。对象是 DeepSeek Harness 的插件配置；示例是独立教学素材，不是 DeepSeek 发布的插件。本文使用实时官方文档接口，不承诺适配所有预览版本。

## 配置从哪里到哪里

用户的 overlay 中的 `config` → 插件导出的 `Config` schema → `apply(ctx, config)` → 工具执行时使用解析后的值。

`ctx` 是服务与注册能力的上下文对象，不是聊天记录。`ignoreWhitespace` 属于插件实例配置，而 `text` 是每次工具调用的输入。改前者改变此实例的计数策略，改后者只改变本次待统计文本。

本例保留原始空白是默认行为；开启选项后仅删除 JavaScript 正则 `\s` 匹配的字符。计数使用 Unicode 码点，组合字符或部分 emoji 序列可能占多个码点；它不声称计算视觉字形数。

## 已有项目的最小使用路径

前提：已有与所用版本匹配的 DeepSeek Harness 源码 checkout，完成该 checkout README 要求的依赖安装与构建。先检查其 `package.json` 的 Node/pnpm 约束；若任务包含环境搭建，依照用户授权准备匹配的运行环境。本示例不附带宿主安装包。

1. 在项目内选择一个新的教学目录，例如 `scratch-plugin-config`。
2. 把 `assets/example/` 里的三个文件复制进去：`plugin.ts`、`text-count.mjs`、`text-count.d.mts`。不要只复制 TypeScript 入口。
3. 在已存在的目录内生成一份新 overlay。以下参数均由执行者替换为实际绝对路径；不要运行未替换的示例路径。

```powershell
python <skill目录>/scripts/write_overlay.py --plugin <仓库目录>/scratch-plugin-config/plugin.ts --output <仓库目录>/scratch-plugin-config/cordis.yml --ignore-whitespace
```

脚本检查入口是否存在，以 JSON 字符串转义路径后写入 YAML，并拒绝覆盖既有文件。不传 `--ignore-whitespace` 会显式写入 `false`。

4. 从 Harness 仓库根目录，用项目自己的启动器运行：

```powershell
pnpm dsh web --patch ./scratch-plugin-config/cordis.yml
```

5. 在 Web UI 配置用户自己的模型路由并选择工作区，然后要求模型“必须调用 `text_count` 统计 `你好 Agent`”。检查记录中的工具名、输入与结果 `7`。

若目的是验证 schema 默认值，备份后只移除该行中的 `ignoreWhitespace`，而不是删掉整个插件行；重新加载后同一输入应为 `8`。已有 profile 的配置可能参与叠加，需同时检查最终配置。

配置页存在使用相对源码路径的片段，而基础插件页明确本地 overlay 不改变 loader 的解析目录。本技能统一生成绝对路径，避免依赖启动位置碰巧正确。

## 三层验证，不混称通过

| 层次 | 怎么验证 | 能说明什么 |
| --- | --- | --- |
| 纯业务逻辑 | 导入 `text-count.mjs` 运行断言 | 计数和空白策略符合例子 |
| 插件加载 | 使用实际 Harness 加载、查看诊断 | import、Config schema、服务依赖已连接 |
| 模型调用 | 查看真实工具调用与结果 | 工具已暴露给所选 Agent 并实际执行 |

本示例交付时纯计数模块可以离线验证；如果缺少 Harness 依赖或模型密钥，应把后两层标为未运行，不能模拟一个 `ctx` 后宣称完整集成通过。

在复制后的示例目录中，可先运行这条不需要 Harness 依赖的检查；输出应为 `7`：

```powershell
node --input-type=module -e "import { countText } from './text-count.mjs'; console.log(countText('你好 Agent', true))"
```

## 排错决策

- 修改 `config` 没有效果：先查是否加载了正确 overlay、是否有后续配置层覆盖、配置行 id 是否匹配；查看最终配置和加载日志，再查 HMR。无法确认热重载时显式重启所启动的开发进程。
- 显式 `false` 却像开启：查是否用了 `||` 默认值；默认值应由 schema 表达。
- 报 Standard Schema 错误：检查导出的运行时 `Config` 是否真是兼容 schema；TypeScript interface 在运行时不存在。
- `ctx.tools` 不可用：核对 `inject` 和当前 profile 是否提供工具服务，不能用静默跳过注册掩盖依赖缺失。
- 类型或 import 不匹配：以用户安装版本的包导出和源码为准，更新示例适配；不要一面采用 master API 一面宣称已发布版本兼容。

## 带练问题

让学习者把忽略空白策略改为“只忽略普通空格、不忽略换行”，先写出 `你 好\nAgent` 的预期值 `8`，再修改纯逻辑并验证。配置字段名和 description 也应反映新的含义，不能只改内部实现而保持误导性的外部契约。

## 官方来源

- [插件配置](https://deepseek-harness.github.io/deepseek-harness/develop/basic/config)：`Config` 类型与 schema、默认值及校验。
- [同页中文源文件](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/config.zh.md)：核对当前导入名和示例导出形式。
- [内置工具插件的 Config 实现](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/tool-subagent/src/index.ts)：运行中的 `Config` 采用 Schemastery schema，并可与同名 TypeScript 类型同时导出；不要照抄其子智能体配置字段。
- [开发一个工具](https://deepseek-harness.github.io/deepseek-harness/develop/basic/tool)：工具参数映射、规范返回值与模型渲染。
- [第一个插件](https://deepseek-harness.github.io/deepseek-harness/develop/basic/)：源码前提、本地绝对路径覆盖层。
- [官方仓库](https://github.com/deepseek-ai/deepseek-harness)：核对实际 checkout 的依赖与命令。
