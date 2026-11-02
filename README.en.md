# DeepSeek Harness Development Skills / 开发 Skill 套装

[简体中文](README.md) | English

Five independent Agent Skills cover development from plugin configuration to Super-agent system design. They give coding assistants on-demand workflows, references, original examples, and acceptance steps, and support learning while building.

This is unofficial learning and development material, not a DeepSeek release. Skill 05 draws on the technical article published on 2026-10-31 and a public research prototype, distinguishing article design, implemented prototype behavior, and extensions still needed.

[English guide (PDF)](docs/superagent-skill-guide.en.pdf) · [中文手册 (PDF)](docs/superagent-skill-guide.pdf) · [Download all five](dist/deepseek-harness-skills-all-v2.zip) · [Validation scope](docs/validation-summary.en.md)

## Suggested order

| Order | Skill | Main use | Download |
| --- | --- | --- | --- |
| 01 | [Plugin configuration](skills/deepseek-harness-01-config/SKILL.md#english) | Fields, Schemastery validation, local overlays, behavioral verification | [ZIP](dist/deepseek-harness-01-config.zip) |
| 02 | [Lifecycle](skills/deepseek-harness-02-lifecycle/SKILL.md#english) | Service dependencies, cleanup, disposal/reload verification | [ZIP](dist/deepseek-harness-02-lifecycle.zip) |
| 03 | [Services and composition](skills/deepseek-harness-03-services/SKILL.md#english) | Service Definition, Provider, Tool Consumer, replacement boundaries | [ZIP](dist/deepseek-harness-03-services.zip) |
| 04 | [Packaging and distribution](skills/deepseek-harness-04-packaging/SKILL.md#english) | Harness bundles, tarball contents, profile activation | [ZIP](dist/deepseek-harness-04-packaging.zip) |
| 05 | [Super-agent system design](skills/deepseek-harness-05-superagent/SKILL.md#english) | Persistent coordination, events, recall, asynchronous interaction, persistence/recovery | [ZIP](dist/deepseek-harness-05-superagent.zip) |

Follow the sequence when learning. For a specific development task, select the relevant skill directly without loading the other four.

## Layout and usage

```text
skills/
  deepseek-harness-01-config/
  deepseek-harness-02-lifecycle/
  deepseek-harness-03-services/
  deepseek-harness-04-packaging/
  deepseek-harness-05-superagent/
docs/
  superagent-skill-guide.pdf
  superagent-skill-guide.en.pdf
  validation-summary.md
  validation-summary.en.md
dist/
  Individual ZIPs, combined archive, and SHA256SUMS.txt
```

Each skill starts at `SKILL.md`. `agents/openai.yaml` supplies interface labels/prompts; `references/` contains on-demand implementation guides; `assets/` contains reusable examples. Some skills also include helper scripts.

Every `SKILL.md` contains Chinese and English sections. References have language links, and interface prompts and demo output are bilingual. Keep each skill directory's internal structure intact after downloading or cloning, then use the loading method supported by your target client. Example requests:

```text
Use $deepseek-harness-01-config to add ignoreWhitespace configuration to my plugin and verify omitted, false, and true behavior.
```

```text
Use $deepseek-harness-05-superagent to design coordination, failure recovery, and notification acceptance for two parallel tasks driven by chat and CI. Deliver the design first; do not deploy.
```

ZIP files distribute **Agent Skill directories**; they cannot be installed as npm packages with `dsh plugin add`. Harness plugin examples live in the corresponding `assets/` directories. See each skill's guide for copying, building, and loading prerequisites. The fifth skill's Python/SQLite lab is an original teaching model, not a port of DeepSeek's prototype.

## Run the offline Super-agent lab

With Python 3.9 or later, from the repository root:

```powershell
cd skills/deepseek-harness-05-superagent/assets/superagent-lab
python -X utf8 -m unittest -v test_coordinator.py
python -X utf8 demo.py
```

Ten tests cover durable deduplication, subscribed follow-ups, task isolation, actual database reopening, lease recovery, stale-generation rejection, quiet progress, and stable outbox IDs. The lab uses no network, models, or external messaging. It does not establish a real asynchronous agent loop, cross-machine migration, or semantic Watchdog.

See the [validation record](docs/validation-summary.en.md) for the other four skills' business/resource/local-packaging checks and real-host behavior still unverified.

## Versions and sources

Technical sources were checked on **2026-11-01**. Harness and the research prototype evolve quickly; verify the actual checkout, host, and dependencies when executing a task. Requirements from one Harness `master` snapshot do not apply automatically to all releases or the prototype.

- [Official Super-agent design article](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg)
- [Official DeepSeek Harness repository](https://github.com/deepseek-ai/deepseek-harness)
- [Verified prototype commit 6337fc8](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e)
- [Prototype positioning at that commit](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/README.md)

The article and prototype code are linked as sources. Skill workflows and offline examples in this repository were authored for these learning materials.
