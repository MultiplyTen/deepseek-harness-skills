# Validation Scope

[简体中文](validation-summary.md) | English

Original record: **2026-11-01**. Format checks, offline business checks, and real-environment integration are distinguished so demo success is not presented as production capability.

## Shared checks for all five skills

- Passed skill-creator's `quick_validate.py` format check.
- Checked interface metadata, invocation names, UTF-8 text, and internal Markdown links.
- Checked syntax of applicable JSON/YAML and Python files.
- Checked ZIP integrity; caches and temporary databases were excluded from distribution.

## Example validation

| Skill | Completed checks | Does not establish |
| --- | --- | --- |
| 01 Configuration | Nine pure-counting assertions; overlay absolute paths, booleans, overwrite refusal; entrypoint syntax | Real Harness runtime schema validation, plugin loading, or model invocation |
| 02 Lifecycle | Three resource-behavior tests; TypeScript entrypoint syntax | Actual Cordis dependency-loss recovery or HMR |
| 03 Services | Four contract tests; syntax of three TypeScript files | Actual registration, Provider replacement, or model integration |
| 04 Packaging | Actual npm tarball; manifest, entrypoint, patch; missing-bundle, escaping-path, and missing-archive-file checks; simulated loading/idempotent disposal | Real DSH installation, profile activation, or removal |
| 05 Super-agent | Ten offline invariant tests; actual database reopening; an independent chat/CI two-task architecture exercise | Persistent deployment, platform authentication/delivery, a real asynchronous agent loop, cross-machine migration, or a complete semantic Watchdog |

Skill 05 simulates delivery through a local outbox and cannot promise external exactly-once behavior. `start_new=True` represents an already authorized simulated admission by the caller, not natural-language authorization assessment.

## Sources and implementation boundaries

The [official article](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg) and [pinned public-prototype commit](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e) were checked. The article explores architecture; the public prototype differs from the internal implementation. Skill 05 pins detailed evidence links to that commit.

At verification, the prototype declared Node `^22.19.0 || >=24.0.0` and DSH `^0.2.1-alpha.2`. A different Harness `master` snapshot declared Node `>=24.9.0`. These are different version targets. Real integration must satisfy both the actual host and prototype requirements. Operations examples also require adaptation before use as native Windows deployment instructions.

This repository's original work did not create accounts, send GitHub/Feishu messages, make model requests, or deploy a real Super-agent. Deployment and external writes belong to a later explicit task.

## Bilingual update verification (2026-11-02)

- All five `SKILL.md` files retain the Chinese workflow and add English. Seven references, the README, and validation summary have linked Chinese/English versions. Interface metadata, tool descriptions, and demo output are bilingual.
- All five skills passed `quick_validate.py` again. Checks covered Chinese/English internal links, interface fields, UTF-8, JSON/YAML/Python syntax, and syntax of both edited TypeScript examples.
- Reran nine configuration-counting assertions, three lifecycle tests, four service-contract tests, ten coordinator tests, and the bilingual demo; all passed.
- Added a five-page English PDF and inspected rendered versions of every page. The original Chinese PDF is retained.
- Regenerated five individual ZIPs, the combined archive, file manifests, and SHA-256 sums. Checked archive integrity, byte-for-byte source parity, and exclusion of caches/temporary databases.

This update covers language and distribution materials. It does not reverify upstream versions or add real Harness/model-integration claims. The technical-source verification date above remains 2026-11-01.
