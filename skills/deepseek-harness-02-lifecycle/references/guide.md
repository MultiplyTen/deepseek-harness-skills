# 生命周期开发与排错指南

这是可执行开发工作流的补充说明，核验日期为 **2026-11-01**。按需要阅读对应部分，无须把整份指南注入每个任务。

## 先确定版本与启动上下文

读取目标仓库或安装包的版本、`engines` 与锁文件，记录实际启动的 profile 和传入的 patch。官方 README 仍将 Harness 标为开发者预览，API 可能破坏兼容。本文核验时，master 的 `package.json` 为 `0.2.2-alpha.2`，要求 Node `>=24.9.0`；这是核验快照，不是每个已发布安装的前提，也不是“最新稳定版”的声明。

如果环境不满足目标 checkout 的要求，报告具体差异。不要替用户升级全局 Node 或改变其他项目的包管理器配置。示例纯 JavaScript 测试不需要安装 Harness；真实集成运行则必须遵循该版本的运行要求。

## 依赖、失败和等待

官方生命周期区分依赖尚未就绪的等待状态、正在执行 `apply`、正常运行、加载失败及卸载。检查插件为何没运行时，先区分“缺少必需服务”和“`apply` 抛错”。

必需服务写进 `inject`，让框架安排加载；依赖消失会使消费插件卸载，恢复后再加载。可选服务在使用处用 `ctx.get()` 查询，并处理不存在的情况。仅在加载时读取一次可选服务，不能假定其引用永远有效。

示例 `pulse.ts` 只使用 `ctx.effect()` 管理本地计时器，不消费服务，因此故意没有 `inject`。在真实工具插件中，需要工具注册表时才声明 `['tools']`。

## 按资源拥有者修复

| 资源 | 建立方式 | 释放责任 |
| --- | --- | --- |
| 工具、监听器等框架注册 | 当前插件的 `ctx` 上的注册方法 | 随该插件作用域撤销 |
| 原生计时器、连接、文件观察器 | Node 或第三方库 | 通过 `ctx.effect()` 返回释放函数 |
| 子插件 | `ctx.plugin()` | 自身作用域；父插件卸载也会带走子插件 |
| 在途异步工作 | 业务代码创建 | 显式停止接收新工作，按实际接口取消或等待 |

不要将原生 `setInterval()` 直接放在模块顶层。模块缓存与插件实例的生命周期不同，文件重载可能再建立一个计时器。也不要声称任意裸计时器会被 Cordis 自动发现。

有顺序依赖的异步资源，在同一个释放函数里依次关闭。例如先停止生产者、等待在途工作结束，最后关闭它们使用的连接。分别注册多个异步释放函数时，逆序开始调用不保证依次完成；不要依靠这种隐含顺序。

## 使用随附示例

将 `assets/lifecycle-plugin` 中四个文件复制到已准备好的 Harness 源码检出下的 `scratch-lifecycle` 目录。不要省略 `.d.mts` 类型声明；它使 TypeScript 插件正确导入 JavaScript 辅助模块。

先执行纯资源测试：

```powershell
node --test ./scratch-lifecycle/managed-pulse.test.mjs
```

它用可控调度器验证取消、幂等释放和替换后无旧输出，不模拟 Cordis。本例的回调是同步的；将它改成网络请求后，需要另行设计在途请求的取消或等待，原有测试不能证明该新行为。

从仓库根目录生成使用真实绝对路径的覆盖层：

```powershell
$lessonPlugin = (Resolve-Path -LiteralPath './scratch-lifecycle/pulse.ts').Path.Replace('\', '/')
$lessonOverlay = @(
  '- insert:'
  '    - id: lifecycle-pulse'
  ('      name: ' + ($lessonPlugin | ConvertTo-Json -Compress))
)
$lessonOverlay | Out-File -LiteralPath './scratch-lifecycle/cordis.yml' -Encoding utf8 -NoClobber
pnpm dsh web --patch ./scratch-lifecycle/cordis.yml
```

此覆盖层的插件路径必须是绝对路径。若 `cordis.yml` 已存在，命令会拒绝覆盖；选择一个新的 overlay 文件名，并同步修改启动参数。源码安装和构建前提按官方 README 完成；本 Skill 不包含 Harness 本身或其依赖。

终端应出现带实例标识的 `loaded` 和后续 `pulse` 日志。通过目标版本支持的插件卸载入口释放实例，检查该实例的 `disposed` 日志以及后续输出停止。重新加载后应仅出现新实例输出。若测试宿主持有 `ctx.plugin()` 的返回值，可以用其 `dispose()` 并等待返回的 Promise 完成。

## 事件与热重载边界

先确认要监听的是运行时 Cordis 事件还是持久化会话事件。`tool/call`、`tool/result` 等会话记录并不自动成为同名 `ctx.on()` 事件；观察记录应使用当前版本支持的会话事件入口并检查类型。事件签名和模式以该 checkout 的声明为准，不根据名称猜参数。

普通观察器不要改变流水线。若使用 waterfall 形式的拦截扩展点，并且要让下游继续，必须委托 `next()`；故意短路才省略委托。

核对有效配置中 HMR 的存在、当前版本是否启用源码监听，以及所改路径是否受其监听。配置更新、源码 HMR 和关闭后重启是三个不同的验证结果；分别记录。无可用重载入口时，交付静态修复和资源测试结果，并明确真实重载尚未验证。

## 最小验收记录

记录触发方式、实例标识和结果：首次加载一次、卸载后旧回调停止、重新加载后仅新实例工作。涉及必需服务时增加依赖缺失与恢复验证。存在异步清理时验证依赖资源不会提前关闭。不要把测试桩的结论扩展到未执行的真实框架行为。

## 官方来源

- [插件与生命周期](https://deepseek-harness.github.io/deepseek-harness/develop/framework/)：依赖加载、资源归属、释放及 HMR 机制。
- [服务与依赖](https://deepseek-harness.github.io/deepseek-harness/develop/framework/service)：必需和可选服务，以及依赖消失后的行为。
- [事件系统](https://deepseek-harness.github.io/deepseek-harness/develop/framework/events)：事件模式、会话事件区别与 waterfall 委托。
- [第一个插件](https://deepseek-harness.github.io/deepseek-harness/develop/basic/)：源码检出前提与绝对路径覆盖层。
- [官方 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.md)：技术预览及源码运行步骤。
- [master package.json](https://github.com/deepseek-ai/deepseek-harness/blob/master/package.json)：核验时的版本和环境约束。
