# Offline Coordination Lab

[简体中文](lab.md) | English

This original Python/SQLite teaching model makes system invariants observable. It is neither a port of DeepSeek's prototype nor an agent runtime that replaces Harness.

## Run

Using Python 3.9 or later, from the copied `assets/superagent-lab` directory:

```powershell
python -X utf8 -m unittest -v test_coordinator.py
python -X utf8 demo.py
```

No third-party packages, model credentials, or platform connections are required. Tests and demo each create a temporary database directory locally and remove it afterward. Do not use the lab directory as a real service's durable-state directory. Demo messages are bilingual Chinese/English.

## Observable flow

1. Two simulated, already authorized decisions create two tasks. Redelivering the first event creates no third task.
2. Follow-up events enter the corresponding task through `source + thread` subscriptions.
3. `claim()` creates a generation-bearing execution assignment; tasks and inputs remain in the database.
4. An injectable clock simulates lease expiry. After `recover_expired()` requeues the task, the database is actually closed and reopened.
5. The new assignment can submit a result; a late result from the old one is rejected.
6. Ordinary progress does not enter the outbox; result and attention messages enter its durable records.
7. After reopening, delivery attempts retain the message ID. `acknowledge()` records a local receipt only.

## Interfaces and teaching purpose

| Interface | Meaning |
| --- | --- |
| `receive(..., start_new=False)` | Record/deduplicate events and route existing subscriptions; `start_new=True` represents a simulated decision already authorized by the caller |
| `subscribe(ticket_id, source, thread)` | Relate follow-ups to a task; does not decide permissions |
| `context(ticket_id)` | Read task state/input without automatically including another task's private input |
| `claim(ticket_id, lease_seconds)` | Create a new generation and record input revision at assignment start |
| `recover_expired()` | Requeue running tasks with expired leases; no semantic-progress judgment |
| `report(assignment, kind, text)` | Validate current generation and reject stale results; input arriving during execution keeps the task pending |
| `pending_messages()` | Read pending results; no network transmission |
| `delivery_attempt()` / `acknowledge()` | Simulate at-least-once attempts and local receipts |

`start_new` does not infer permission from text. The real prototype defaults to observing inferred admissions. This example has no Policy, Mandate, natural-language assessment, or policy versioning. It does not mean every chat can trigger automatic work.

## Ten-test coverage

Tests cover event deduplication after actually reopening the database; source isolation for equal event IDs; subscribed follow-ups; repeated handling of unadmitted events; expired reassignment and stale-result rejection; quiet progress without lease renewal; durable outbox/stable retry IDs; attention state surviving across instances; input preservation during execution; and refusing a different result for the same idempotency key.

An injectable clock advances time without sleeps, making failure scenarios repeatable.

## Limits

- One coordinator writes SQLite. There are no multiple coordinating nodes, distributed locks, or cross-machine scheduling.
- The model simulates task lifecycles/generations, without real Worker processes, LLMs, asynchronous ReAct loops, or model context windows.
- `recover_expired()` checks expiry only. It supplies no semantic Watchdog, heartbeat renewal, or bounded recovery policy. Real systems must distinguish slow work from failure.
- Subscriptions match this example's keys. They do not implement every prototype follow-up ownership, stopping, resumption, or reassessment rule. Duplicates keep their first decision.
- Progress only demonstrates quiet notifications; there is no complete audit log. Production systems should retain necessary internal progress records.
- The outbox has no real sender or complete multichannel destination model. Receiver idempotency is outside the lab; receipt loss after delivery can cause real duplicates.

Passing tests establishes only the corresponding example invariants. Real deployment additionally needs actual-host, source-authentication, platform-side-effect, background-task, model-assessment, and sustained-operation verification.
