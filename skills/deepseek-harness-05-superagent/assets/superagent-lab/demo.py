"""A local simulation of authorized work. No external messages or model calls."""
from pathlib import Path
from tempfile import TemporaryDirectory

from coordinator import Coordinator, StaleAssignment


def main():
    clock = [0.0]
    # Keep all demo writes beside this copied lab, then clean up its own folder.
    with TemporaryDirectory(prefix='superagent-demo-', dir=Path(__file__).resolve().parent) as folder:
        path = Path(folder) / 'state.sqlite3'
        with Coordinator(path, now=lambda: clock[0]) as runtime:
            first = runtime.receive('github', 'event-1', 'issue-1', '已授权：分析测试失败', start_new=True)[0]
            second = runtime.receive('chat', 'event-2', 'topic-2', '已授权：整理发布说明', start_new=True)[0]
            runtime.receive('github', 'event-1', 'issue-1', '重复投递', start_new=True)
            runtime.receive('github', 'event-3', 'issue-1', '补充：仅检查回归范围')
            old = runtime.claim(first, lease_seconds=3)
            runtime.report(old, 'progress', '本地模拟正在分析')
            print(f'两个独立任务：{first}、{second}；重复事件未创建第三个任务。')
            print(f'后续输入只进入订阅任务：{len(runtime.context(first)["inputs"])} 条。')
            print(f'普通进展保持安静，待发送消息数：{len(runtime.pending_messages())}。')
            clock[0] = 4
            print(f'超时重排任务数：{runtime.recover_expired()}；输入仍在数据库中。')

        with Coordinator(path, now=lambda: clock[0]) as runtime:
            current = runtime.claim(first)
            try:
                runtime.report(old, 'result', '旧工作者迟到的结果')
            except StaleAssignment:
                print('重新打开数据库后，旧 generation 的结果被拒绝。')
            message_id = runtime.report(current, 'result', '已完成本地模拟，供人验收。')
            other = runtime.claim(second)
            runtime.report(other, 'attention', '模拟决策点：请确认发布范围。')
            print(f'任务上下文隔离：第二个任务只有 {len(runtime.context(second)["inputs"])} 条输入。')
            runtime.delivery_attempt(message_id)

        with Coordinator(path, now=lambda: clock[0]) as runtime:
            retried = runtime.delivery_attempt(message_id)
            print(f'重开后沿用消息 ID：{retried["message_id"]}，本地尝试次数：{retried["attempts"]}。')
            print('Outbox 只记录至少一次尝试；真实接收端仍须幂等，本实验没有发送消息。')
            print('本实验不验证模型评估、异步 Agent 循环、跨机迁移或语义 Watchdog。')


if __name__ == '__main__':
    main()
