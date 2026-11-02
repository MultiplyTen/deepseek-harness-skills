# Official Prototype versus Article Design

[简体中文](prototype-map.md) | English

Sources checked: **2026-11-01**. The [official article on Super-agent design](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg) and [official prototype repository](https://github.com/deepseek-ai/dsh-superagent-prototype) were reviewed. Published on 2026-10-31, the article explores engineering architecture rather than listing existing product features. Prototype evidence is pinned to [6337fc8](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e).

## Verified positioning

The repository describes a research reference prototype serving one GitHub repository, optionally connected to Feishu. Its code was adapted for public release and differs from the internal version and article implementation. It is a Harness bundle, not a new foundation model or a deployable service bundled with this skill. [README](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/README.md)

## From requirements to code

| Requirement | Official entrypoint | Boundary to inspect |
| --- | --- | --- |
| Construction, startup, shutdown | `src/app/runtime.ts`; Runtime architecture | Lifecycle, state-directory locking, dependency initialization/disposal |
| Tasks, assessment, dispatch rules | `src/core/engine.ts`, `src/core/ports.ts` | Engine transactions, domain objects, replaceable ports |
| Events and subscriptions | `docs/001-domain.md`, `docs/002-authorization.md` | Deduplication keys, subscription fan-out, new-work assessment, Mandate |
| Main assessment and work sessions | Assessor/Executor architecture; `docs/003-execution.md` | Main/task-session roles, concurrency slots, background work |
| External delivery | `src/app/outbox.ts`; Outbox architecture | Post-commit effects, stable receipts, source channels |
| New platform sources | `docs/008-cookbook.md` | Event mapping, scope/identity, replies/context, polling |
| Installation and operations | `SETUP.md`, `docs/006-deployment.md` | Dedicated profile, dependencies, accounts, state directory |

This table is code navigation, not a promise that every row is importable from an independent public npm API. Read actual exports, signatures, and neighboring tests at the target commit before editing.

## Capabilities that must remain distinct

- Router/Worker separation has concrete main-session and Executor-session implementations. Creating several subagents is not equivalent to the same persistent coordination system. [Execution model](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/003-execution.md)
- Sources, reception rules, subscriptions, and cross-source replies have domain constraints. Extend those interfaces rather than bypassing task/authorization state through external CLIs. [Source extension cookbook](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/008-cookbook.md)
- The article states that a complete asynchronous ReAct mechanism exists in Harness but is not enabled by default. The public prototype provides evidence for specific background-command, slot-management, and recovery-input behavior. These do not establish that installation enables every asynchronous article feature by default.
- The article proposes stateless cloud compute, external session storage, and endpoint execution daemons. The prototype's persistent SQLite Store and separate Assignment support records/restart recovery; this does not establish complete cloud/multidevice runtime migration.
- The article's external Watchdog is a supervisory loop using an independent Session plus timed input. Prototype evidence supports health, recovery, and operations checks. Those do not replace full task-progress/goal-drift judgment. Mark unsupported capabilities as unverified rather than asserting their absence.

The prototype defaults inferred admission to `observe`, recording what would be admitted. Explicit requests can still be handled under `off`, `observe`, and `auto`. Subscriptions convey context without expanding authorization. Preserve both facts; direct routing does not mean any event may initiate work. [Authorization](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/002-authorization.md)

For new Sources, use stable IDs and advance read cursors only after `SourceContext.receive(trigger)` completes. The Cookbook's `hookq` is a fictional CLI illustrating the contract, not an official component to install. [Cookbook](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/008-cookbook.md)

## Version and deployment prerequisites

At verification, prototype `package.json` was `0.1.0`, declaring Node `^22.19.0 || >=24.0.0` and `engines.dsh` `^0.2.1-alpha.2`. Deployment examples use public `dsh@0.2.1-rc.3`. These are distinct from requirements in another Harness `master` snapshot. [Manifest](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/package.json), [deployment guide](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/006-deployment.md)

Recheck these files and available versions for actual deployment. Official setup also involves git, Python, tmux, and GitHub CLI; Feishu is optional. Linux shell/tmux commands are not native Windows instructions without adaptation. Choose an environment meeting project requirements before platform integration.

The prototype changes process environment, and runtime roles are not process sandboxes. Follow its deployment guide with a dedicated profile; do not reset an existing profile using first-initialization commands. If the task is design or skill creation, do not create accounts, send platform messages, or deploy services. [Deployment boundaries](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/006-deployment.md)

Distinguish operations-check exit codes: `0` is healthy/quiet, `1` enters the relevant recovery assessment, `2` is a component issue, and `3` means configuration is pending. Do not turn the latter three into endless restarts. Automated checks should respect human stops, including the script's `--respect-stop` behavior. These are infrastructure-recovery boundaries, not evidence of a complete semantic Watchdog. [Operations script](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/scripts/dsh-superagent)

## Reading order

For prototype changes, read `000` design principles and `001` vocabulary first, then relevant authorization, execution, architecture, and extension sections. Load needed chapters rather than all documents into every model request.

- [000 Philosophy](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/000-philosophy.md)
- [001 Domain](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/001-domain.md)
- [002 Authorization](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/002-authorization.md)
- [003 Execution](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/003-execution.md)
- [007 Architecture](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/007-architecture.md)
- [008 Cookbook](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/docs/008-cookbook.md)
