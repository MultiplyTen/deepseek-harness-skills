# 官方原型与文章设计的对照

简体中文 | [English](prototype-map.en.md)

核验日期：2026-11-01。已核对 [官方公众号原文《Super-agent 设计探索：迈向更自主的 Agent 系统》](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg) 与 [DeepSeek 官方原型仓库](https://github.com/deepseek-ai/dsh-superagent-prototype)。文章发布于 2026-10-31，讨论工程架构而非现有产品功能清单。原型核验提交为 [6337fc8](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e)。

## 已核实的定位

仓库说明它是研究参考原型，服务于一个 GitHub 仓库，可选接入飞书；代码经过公开发布适配，与内部版本及文章所述实现不完全相同。它是 Harness 的 bundle，不是新的底层模型，也不是本 Skill 附带的可直接部署服务。[README](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/README.md)

## 从需求找到代码

| 需求 | 官方入口 | 应检查的边界 |
| --- | --- | --- |
| 构造、启动、停机 | `src/app/runtime.ts`，架构文档 Runtime | 生命周期、状态目录锁、依赖初始化与释放 |
| 任务、判断和分派规则 | `src/core/engine.ts`、`src/core/ports.ts` | Engine 事务、领域对象、可替换端口 |
| 新事件与订阅 | `docs/001-domain.md`、`docs/002-authorization.md` | 去重键、订阅扇出、新工作判断、Mandate |
| 主会话判断与工作会话 | 架构文档 Assessor / Executor、`docs/003-execution.md` | 主会话与任务会话分工、并发槽位、后台任务 |
| 外部投递 | `src/app/outbox.ts`，架构文档 Outbox | 事务后副作用、稳定回执与来源信道 |
| 新增平台来源 | `docs/008-cookbook.md` | 事件映射、范围/身份规则、回复/上下文和轮询 |
| 真实安装和运维 | `SETUP.md`、`docs/006-deployment.md` | 专用 profile、依赖版本、账号与状态目录 |

表是代码导航，不代表所有行都可从独立公共 npm API 直接 import。修改前读取当前提交的实际导出、签名及相邻测试。

## 不能混为一谈的能力

- Router/Worker 角色分离已有主会话和 Executor 会话的具体实现；一般“开多个子代理”不等于相同的常驻协调系统。[执行模型](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/003-execution.md)
- Source、接收规则、订阅与跨来源回复已有领域约束。新增来源优先沿扩展接口，而不是绕过任务/授权状态直接调用外部 CLI。[Source 扩展教程](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/008-cookbook.md)
- 原文称完整异步 ReAct 机制在 Harness 中已实现、尚未默认开启；公开原型可证实的是后台命令、槽位管理和恢复输入等具体行为，不能把两个层面的结论混成“安装原型就默认得到全部异步功能”。
- 文章提出无状态云计算、外置会话存储和端侧执行 daemon 等方向。公开原型的持久 SQLite Store 与独立 Assignment 支持记录和重启恢复，不能据此宣布完整云端/多设备运行环境迁移已经交付。
- 原文的外部 Watchdog 是独立 Session 加定时输入构成的监督回路。原型可确认的是健康状态、恢复路径及运维检查；这些不能代替完整的任务进展与目标偏离判断。没有具体实现证据时标为尚未核实，而非断言不存在。

原型默认的推断接纳模式为 `observe`，只记录会怎样接纳推断任务；显式请求在 `off`、`observe`、`auto` 下仍可处理。订阅传上下文、不扩大授权，这两条应同时保留，不能把直通机制写成任何事件都能启动工作。[授权说明](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/002-authorization.md)

新增 Source 时使用稳定 id，并在 `SourceContext.receive(trigger)` 完成后才前移读取游标。官方 Cookbook 中的 `hookq` 是用于说明契约的虚构 CLI，不是需要安装的官方组件。[Source 教程](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/008-cookbook.md)

## 版本与部署前提

核验时原型 `package.json` 的版本为 `0.1.0`，声明 Node `^22.19.0 || >=24.0.0`，`engines.dsh` 为 `^0.2.1-alpha.2`。部署文档示例使用公开的 `dsh@0.2.1-rc.3`；这与另一个 Harness master 快照的要求不是同一个版本结论。[原型 manifest](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/package.json)、[部署文档](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/006-deployment.md)

真正部署时重新核对以上文件与可用版本。官方部署还涉及 git、Python、tmux、GitHub CLI，飞书为可选项；不能把 Linux shell/tmux 示例原样当成原生 Windows 安装步骤。优先选择符合项目要求的执行环境，再完成具体平台集成。

原型会改变进程环境，运行角色也不是进程沙箱。按其部署文档为它使用独立 profile；既有 profile 不用“首次初始化”命令重置。用户要求的是设计或制作 Skill 时，不进行账户创建、平台消息投递和服务部署。[部署边界](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/006-deployment.md)

运维检查的退出码需要区分：`0` 正常安静，`1` 才进入相应恢复判断，`2` 是组件问题，`3` 是待配置；不要把后三者统一做成不断重启。自动检查应尊重人工停止，例如核对脚本的 `--respect-stop` 行为。这是基础设施恢复边界，不是语义 Watchdog 已全部实现的证据。[运维脚本](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/scripts/dsh-superagent)

## 使用资料的顺序

修改原型时，先读 `000` 的设计原则和 `001` 的领域词汇，再按所改路径读授权、执行、架构与扩展教程。只读需要的章节，不将所有文档塞进每个模型请求。

- [000 Philosophy](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/000-philosophy.md)
- [001 Domain](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/001-domain.md)
- [002 Authorization](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/002-authorization.md)
- [003 Execution](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/003-execution.md)
- [007 Architecture](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/007-architecture.md)
- [008 Cookbook](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/008-cookbook.md)
