# 离线协调实验

简体中文 | [English](lab.en.md)

这是原创的 Python/SQLite 教学模型，用来观察系统不变量。它不是 DeepSeek 原型的移植，也不是能代替 Harness 的 Agent 运行时。

## 运行

使用 Python 3.9 或更高版本，在复制后的 `assets/superagent-lab` 目录运行：

```powershell
python -X utf8 -m unittest -v test_coordinator.py
python -X utf8 demo.py
```

无需安装第三方包、配置模型密钥或连接平台。测试和演示各自在本目录下创建自己的临时数据库目录，完成后清理该目录。不要把此实验目录当成真实服务的长期状态目录。

## 可观察的流程

1. 两个已经获得授权的模拟决定各自创建一个任务；重复投递第一个事件不创建第三个任务。
2. 后续事件通过 `source + thread` 订阅进入对应任务的输入。
3. `claim()` 分配一个带 generation 的执行绑定；任务和输入仍保存在数据库。
4. 用可注入时钟模拟租约过期，经 `recover_expired()` 重排后，真正关闭并重新打开数据库。
5. 新执行绑定可以提交结果，旧绑定的迟到结果被拒绝。
6. 普通 progress 不进入 outbox；result 与 attention 进入持久 outbox。
7. 重开数据库再记录发送尝试，消息 id 保持稳定；`acknowledge()` 只记录本地回执。

## 接口及意义

| 接口 | 教学含义 |
| --- | --- |
| `receive(..., start_new=False)` | 记录与去重事件、按已有订阅分发；`start_new=True` 代表调用方已经授予的模拟决定 |
| `subscribe(ticket_id, source, thread)` | 建立后续事件到任务的关系，不执行权限判断 |
| `context(ticket_id)` | 按任务读取状态和输入；不会自动混入其他任务的私有输入 |
| `claim(ticket_id, lease_seconds)` | 创建新的执行代际，记录该次执行开始时的输入 revision |
| `recover_expired()` | 将租期已过的运行任务重排；不判断语义进展 |
| `report(assignment, kind, text)` | 校验当前执行代际，拒绝旧结果；执行期间新增的输入会使任务保留待处理状态 |
| `pending_messages()` | 读取待交付结果；没有网络发送 |
| `delivery_attempt()` / `acknowledge()` | 模拟至少一次发送尝试和本地回执 |

`start_new` 不是从文字里猜权限的规则。真实原型的推断任务默认先 observe，本例没有 Policy、Mandate、自然语言评估或策略版本。切勿把调用示例解释为所有聊天都能触发自动工作。

## 十项验证覆盖什么

测试覆盖真实重开数据库后的事件去重、相同 event id 在不同来源的隔离、订阅后续输入、未接纳事件的重复处理、过期重派与迟到结果拒绝、progress 静默且不续租、持久 outbox 与稳定重试 id、attention 状态跨实例保留、执行期间新输入不丢失，以及同一幂等键不能换一个结果。

测试时间由可注入时钟推进，不用 sleep 等待，因此故障场景可重复。

## 不能外推的结论

- SQLite 由一个协调器写入；没有多协调节点、分布式锁或跨机调度。
- 模拟的是任务生命周期与执行代际；没有真实 Worker 进程、LLM、异步 ReAct 循环或模型上下文窗口。
- `recover_expired()` 只依据到期时间，不提供语义 Watchdog、心跳续租或有限恢复策略。真实系统还需区分长耗时工作和故障。
- 订阅按本例键匹配；不实现公开原型的全部 follow-up 归属、停止、恢复或再次评估规则。重复事件沿用首次决定。
- progress 在此只演示不发通知，没有完整审计日志；正式系统应保留需要的内部进度记录。
- outbox 没有真实发送器或完整的多信道目标模型。外部接收端是否幂等不在实验中；若发送后回执丢失，真实系统可能重复投递。

通过这些测试只能说明本例的对应不变量成立。正式落地还需验证实际宿主、来源鉴权、平台副作用、后台任务、模型判断和持续运行行为。
