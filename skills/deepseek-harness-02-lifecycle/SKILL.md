---
name: deepseek-harness-02-lifecycle
description: "实现或修复 DeepSeek Harness 插件的依赖加载、资源释放、重复注册和热重载问题，也用于带开发者完成生命周期练习。用于已有 Harness/Cordis 插件，不用于普通 JavaScript 定时器问题或插件打包分发。 / Implement or fix Harness/Cordis plugin dependency loading, cleanup, duplicate registration, and hot reload; also teach lifecycle behavior. Excludes generic JavaScript timer issues and packaging."
---

[中文](#中文) | [English](#english)

## 中文

按用户使用的语言回答；仅按需读取对应语言的参考资料。中英文内容表达同一套工作流。

# DeepSeek Harness 插件生命周期

将插件的资源归属、依赖和卸载行为做成可验证的实现。教学时使用随附示例；处理真实项目时保留其功能和接口，只修改导致生命周期问题的部分。

## 工作方法

1. 确定运行的 DSH 版本、启动方式、profile、插件入口和有效配置。读取目标 checkout 的 `package.json`、锁文件和相关接口。开发者预览的 master 文档不能直接视为任意已发布版本的保证。
2. 列出插件创建的注册、计时器、连接、后台工作与子插件，并标明拥有者。将重复启动、卸载后仍输出、服务缺失等现象归到具体资源；需要细节时读 [操作指南](references/guide.md)。
3. 使用服务前声明实际需要的 `inject`。必需依赖未就绪时应等待；不要用轮询和重试循环绕过依赖加载。可选能力在使用处查询，不要为了统一写法变成必需依赖。
4. 通过当前插件的 `ctx` 注册工具、监听器和其他能力。原生 `setInterval`、连接等外部资源用 `ctx.effect()` 返回释放函数。已被框架管理的注册不再另外保留一套全局注册。
5. 有顺序依赖的异步清理放进同一个释放函数并逐个 `await`。停止产生新工作后，再处理在途工作和关闭依赖资源。不要把“逆序开始调用”理解成“所有异步释放依次完成”。
6. 在有效配置中核对 HMR 和实际监听范围，再验证重载。区分源码重载、配置重载和重启进程；不能用重启后正常来证明热重载正确。

## 示例与验证

- [计时器插件](assets/lifecycle-plugin/pulse.ts)：不需要服务，故没有 `inject`；每次加载创建独立实例。
- [受管理的计时器](assets/lifecycle-plugin/managed-pulse.mjs)：返回幂等释放函数，阻止已经排队的旧回调继续输出。
- [资源测试](assets/lifecycle-plugin/managed-pulse.test.mjs)：无第三方依赖，执行 `node --test <该文件路径>`。它验证资源行为，不模拟或证明 Cordis 的加载实现。
- [类型声明](assets/lifecycle-plugin/managed-pulse.d.mts)：供 TypeScript 插件导入示例辅助模块。

实现任务交付改动、触发条件、验证结果和仍未覆盖的集成行为。教学任务让学习者观察一次加载、一次卸载和一次重新加载，并解释为何旧实例不会留下计时器。不能因为离线测试通过，就声称真实 Harness 的服务消失恢复或 HMR 已验证。

## 依据

官方资料核验于 **2026-11-01**。本 Skill 是学习与开发工作流，不是 DeepSeek 官方发布物。来源、版本核对和运行步骤见 [操作指南](references/guide.md)。

---

## English

Respond in the user's language and read only the relevant language version of a reference. Both sections describe the same workflow.

# DeepSeek Harness Plugin Lifecycle

Make resource ownership, dependencies, and disposal testable. Use the examples for teaching. In a real project, preserve functionality and interfaces while changing the parts responsible for lifecycle problems.

## Workflow

1. Identify the running DSH version, launch method, profile, plugin entrypoint, and effective configuration. Read the target checkout's `package.json`, lockfile, and relevant interfaces. Developer-preview `master` documentation does not guarantee compatibility with every release.
2. Inventory registrations, timers, connections, background work, and child plugins, with an owner for each. Map duplicate startup, post-disposal output, or missing services to specific resources; consult the [guide](references/guide.en.md) as needed.
3. Declare actually required services in `inject` before using them. Wait for required dependencies; do not bypass dependency loading with polling or retry loops. Look up optional capabilities where used rather than making them required for stylistic consistency.
4. Register tools, listeners, and capabilities through the current plugin's `ctx`. Manage native `setInterval`, connections, and other external resources through a disposer returned by `ctx.effect()`. Do not duplicate framework-managed registrations in a global registry.
5. Put asynchronous cleanup with ordering requirements into one disposer and `await` each step. Stop producing work, then handle in-flight work and close its dependencies. Starting disposers in reverse order does not mean all asynchronous disposers complete sequentially.
6. Check HMR and watched paths in the effective configuration before testing reloads. Distinguish source reload, configuration reload, and process restart; a successful restart does not prove HMR correctness.

## Examples and verification

- [Timer plugin](assets/lifecycle-plugin/pulse.ts): uses no service and therefore has no `inject`; each load creates a separate instance.
- [Managed timer](assets/lifecycle-plugin/managed-pulse.mjs): returns an idempotent disposer and prevents already queued callbacks from an old instance from producing output.
- [Resource tests](assets/lifecycle-plugin/managed-pulse.test.mjs): run `node --test <path-to-this-file>` without third-party dependencies. They test resource behavior, not Cordis loading.
- [Type declaration](assets/lifecycle-plugin/managed-pulse.d.mts): lets the TypeScript plugin import its JavaScript helper.

For implementation, deliver changes, triggers, verification results, and uncovered integration behavior. For teaching, observe one load, disposal, and reload, then explain why the old instance leaves no timer behind. Offline tests do not establish real Harness service-loss recovery or HMR behavior.

## Basis

Official materials were checked on **2026-11-01**. This is an unofficial learning and development workflow. See the [guide](references/guide.en.md) for sources, version checks, and execution steps.
