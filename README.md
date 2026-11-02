# DeepSeek Harness 开发 Skill 套装 / Development Skills

中英双语 · Chinese & English | [English only](README.en.md)

五个独立的 Agent Skill，覆盖从插件配置到 Super-agent 系统设计的开发流程。它们为编码助手提供可按需读取的工作方法、参考资料、原创示例和验收步骤，也可以用于边做边学。

Five independent Agent Skills cover development from plugin configuration to Super-agent system design. They give coding assistants on-demand workflows, references, original examples, and acceptance steps, and support learning while building.

本项目为非官方学习与开发资料，不是 DeepSeek 官方发布物。第五个 Skill 依据 2026-10-31 的技术文章和公开研究原型整理，并明确区分文章设计、原型已实现能力与需要自行扩展的部分。

This is unofficial learning and development material, not a DeepSeek release. Skill 05 draws on the technical article published on 2026-10-31 and a public research prototype, distinguishing article design, implemented prototype behavior, and extensions still needed.

[中文手册 / Chinese guide (PDF)](docs/superagent-skill-guide.pdf) · [英文手册 / English guide (PDF)](docs/superagent-skill-guide.en.pdf) · [下载五合一总包 / Download all five](dist/deepseek-harness-skills-all-v2.zip) · [验证范围（中文）](docs/validation-summary.md) / [Validation scope (English)](docs/validation-summary.en.md)

## 五个 Skill 的使用顺序 / Suggested Order

| 顺序 / Order | Skill | 主要用途 / Main use | 下载 / Download |
| --- | --- | --- | --- |
| 01 | [插件配置 / Plugin configuration](skills/deepseek-harness-01-config/SKILL.md) | 配置字段、Schemastery 校验、本地 overlay 与行为验证<br>Fields, Schemastery validation, local overlays, and behavioral verification | [ZIP](dist/deepseek-harness-01-config.zip) |
| 02 | [生命周期 / Lifecycle](skills/deepseek-harness-02-lifecycle/SKILL.md) | 服务依赖、资源清理、卸载与重载验证<br>Service dependencies, cleanup, and disposal/reload verification | [ZIP](dist/deepseek-harness-02-lifecycle.zip) |
| 03 | [服务与能力组合 / Services and composition](skills/deepseek-harness-03-services/SKILL.md) | Service Definition、Provider、Tool Consumer 与替换边界<br>Service Definition, Provider, Tool Consumer, and replacement boundaries | [ZIP](dist/deepseek-harness-03-services.zip) |
| 04 | [打包与分发 / Packaging and distribution](skills/deepseek-harness-04-packaging/SKILL.md) | Harness bundle、tarball 内容与 profile 激活<br>Harness bundles, tarball contents, and profile activation | [ZIP](dist/deepseek-harness-04-packaging.zip) |
| 05 | [Super-agent 系统设计 / Super-agent system design](skills/deepseek-harness-05-superagent/SKILL.md) | 常驻协调、事件、上下文召回、异步交互、持久化和恢复<br>Persistent coordination, events, recall, asynchronous interaction, persistence, and recovery | [ZIP](dist/deepseek-harness-05-superagent.zip) |

学习时建议按编号推进；已有具体开发任务时，可以直接选择对应 Skill，无需先加载其余四个。

Follow the sequence when learning. For a specific development task, select the relevant skill directly without loading the other four.

## 目录与使用方式 / Layout and Usage

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
  各 Skill 的独立 ZIP、总包和 SHA256SUMS.txt
  Individual ZIPs, combined archive, and SHA256SUMS.txt
```

每个 Skill 以 `SKILL.md` 为入口，`agents/openai.yaml` 提供界面名称和调用提示，`references/` 存放按需读取的实施资料，`assets/` 是可复制示例；部分 Skill 还提供辅助脚本。

Each skill starts at `SKILL.md`. `agents/openai.yaml` supplies interface labels and prompts; `references/` contains on-demand implementation guides; `assets/` contains reusable examples. Some skills also include helper scripts.

所有 `SKILL.md` 均提供中英文说明；参考指南可切换语言，界面提示和演示输出为双语。

Every `SKILL.md` contains Chinese and English sections. References have language links, and interface prompts and demo output are bilingual.

下载或克隆后，保持同名 Skill 目录的内部结构，按目标客户端支持的 Skill 加载方式使用。示例调用：

Keep each skill directory's internal structure intact after downloading or cloning, then use the loading method supported by your target client. Example requests:

```text
使用 $deepseek-harness-01-config，为我的插件增加 ignoreWhitespace 配置，验证省略、false 和 true 三种行为。

Use $deepseek-harness-01-config to add ignoreWhitespace configuration to my plugin and verify omitted, false, and true behavior.
```

```text
使用 $deepseek-harness-05-superagent，为聊天与 CI 驱动的两个并行任务设计协调层、故障恢复和通知验收方案；先做设计，不部署。

Use $deepseek-harness-05-superagent to design coordination, failure recovery, and notification acceptance for two parallel tasks driven by chat and CI. Deliver the design first; do not deploy.
```

这些 ZIP 是 **Agent Skill 目录的分发包**，不能直接作为 `dsh plugin add` 的 npm 包安装。Harness 插件素材在对应 `assets/` 中，复制、构建和加载前提见各 Skill 的参考指南。第五个的 Python/SQLite 实验是原创教学模型，不是 DeepSeek 原型的移植。

ZIP files distribute **Agent Skill directories**; they cannot be installed as npm packages with `dsh plugin add`. Harness plugin examples live in the corresponding `assets/` directories. See each skill's guide for copying, building, and loading prerequisites. The fifth skill's Python/SQLite lab is an original teaching model, not a port of DeepSeek's prototype.

## 运行 Super-agent 离线实验 / Run the Offline Super-agent Lab

使用 Python 3.9 或更高版本，在仓库根目录执行：

With Python 3.9 or later, run from the repository root:

```powershell
cd skills/deepseek-harness-05-superagent/assets/superagent-lab
python -X utf8 -m unittest -v test_coordinator.py
python -X utf8 demo.py
```

十项测试覆盖持久去重、订阅后续输入、任务隔离、真正重开数据库、租期恢复、旧执行代际拒绝、progress 静默与稳定 outbox 消息 ID。实验没有网络、模型调用或外部消息发送，不证明真实异步 Agent 循环、跨机迁移或语义 Watchdog 已实现。

Ten tests cover durable deduplication, subscribed follow-ups, task isolation, actual database reopening, lease recovery, stale-generation rejection, quiet progress, and stable outbox IDs. The lab uses no network, models, or external messaging. It does not establish a real asynchronous agent loop, cross-machine migration, or semantic Watchdog.

其他四个 Skill 的业务逻辑、资源行为和本地打包检查，以及尚未验证的真实宿主行为，见[验证记录](docs/validation-summary.md)。

See the [validation record](docs/validation-summary.en.md) for the other four skills' business, resource, and local-packaging checks and real-host behavior still unverified.

## 版本与资料 / Versions and Sources

资料核验日期为 **2026-11-01**。Harness 和研究原型处于快速迭代阶段，执行任务时应核对实际 checkout、宿主和依赖要求。不能把某个 Harness master 快照的环境条件视为所有发布版本或原型的要求。

Technical sources were checked on **2026-11-01**. Harness and the research prototype evolve quickly; verify the actual checkout, host, and dependencies when executing a task. Requirements from one Harness `master` snapshot do not apply automatically to all releases or the prototype.

- [官方文章：Super-agent 设计探索 / Official Super-agent design article](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg)
- [DeepSeek Harness 官方仓库 / Official DeepSeek Harness repository](https://github.com/deepseek-ai/deepseek-harness)
- [Super-agent 原型核验提交 6337fc8 / Verified prototype commit](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e)
- [该提交的原型定位说明 / Prototype positioning at that commit](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/README.md)

原文和原型代码以链接引用；本仓库提供的 Skill 工作流和离线示例为本次资料制作内容。

The article and prototype code are linked as sources. Skill workflows and offline examples in this repository were authored for these learning materials.
