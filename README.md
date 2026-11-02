# DeepSeek Harness 开发 Skill 套装 / Development Skills

简体中文 | [English](README.en.md)

五个独立的 Agent Skill，覆盖从插件配置到 Super-agent 系统设计的开发流程。它们为编码助手提供可按需读取的工作方法、参考资料、原创示例和验收步骤，也可以用于边做边学。

本项目为非官方学习与开发资料，不是 DeepSeek 官方发布物。第五个 Skill 依据 2026-10-31 的技术文章和公开研究原型整理，并明确区分文章设计、原型已实现能力与需要自行扩展的部分。

[中文手册（PDF）](docs/superagent-skill-guide.pdf) · [English guide (PDF)](docs/superagent-skill-guide.en.pdf) · [下载五合一总包](dist/deepseek-harness-skills-all-v2.zip) · [查看验证范围](docs/validation-summary.md)

## 五个 Skill 的使用顺序

| 顺序 | Skill | 主要用途 | 下载 |
| --- | --- | --- | --- |
| 01 | [插件配置](skills/deepseek-harness-01-config/SKILL.md) | 配置字段、Schemastery 校验、本地 overlay 与行为验证 | [ZIP](dist/deepseek-harness-01-config.zip) |
| 02 | [生命周期](skills/deepseek-harness-02-lifecycle/SKILL.md) | 服务依赖、资源清理、卸载与重载验证 | [ZIP](dist/deepseek-harness-02-lifecycle.zip) |
| 03 | [服务与能力组合](skills/deepseek-harness-03-services/SKILL.md) | Service Definition、Provider、Tool Consumer 与替换边界 | [ZIP](dist/deepseek-harness-03-services.zip) |
| 04 | [打包与分发](skills/deepseek-harness-04-packaging/SKILL.md) | Harness bundle、tarball 内容与 profile 激活 | [ZIP](dist/deepseek-harness-04-packaging.zip) |
| 05 | [Super-agent 系统设计](skills/deepseek-harness-05-superagent/SKILL.md) | 常驻协调、事件、上下文召回、异步交互、持久化和恢复 | [ZIP](dist/deepseek-harness-05-superagent.zip) |

学习时建议按编号推进；已有具体开发任务时，可以直接选择对应 Skill，无需先加载其余四个。

## 目录与使用方式

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
```

每个 Skill 以 `SKILL.md` 为入口，`agents/openai.yaml` 提供界面名称和调用提示，`references/` 存放按需读取的实施资料，`assets/` 是可复制示例；部分 Skill 还提供辅助脚本。

所有 `SKILL.md` 均提供中英文说明；参考指南可切换语言，界面提示和演示输出为双语。

下载或克隆后，保持同名 Skill 目录的内部结构，按目标客户端支持的 Skill 加载方式使用。示例调用：

```text
使用 $deepseek-harness-01-config，为我的插件增加 ignoreWhitespace 配置，验证省略、false 和 true 三种行为。
```

```text
使用 $deepseek-harness-05-superagent，为聊天与 CI 驱动的两个并行任务设计协调层、故障恢复和通知验收方案；先做设计，不部署。
```

这些 ZIP 是 **Agent Skill 目录的分发包**，不能直接作为 `dsh plugin add` 的 npm 包安装。Harness 插件素材在对应 `assets/` 中，复制、构建和加载前提见各 Skill 的参考指南。第五个的 Python/SQLite 实验是原创教学模型，不是 DeepSeek 原型的移植。

## 运行 Super-agent 离线实验

使用 Python 3.9 或更高版本，在仓库根目录执行：

```powershell
cd skills/deepseek-harness-05-superagent/assets/superagent-lab
python -X utf8 -m unittest -v test_coordinator.py
python -X utf8 demo.py
```

十项测试覆盖持久去重、订阅后续输入、任务隔离、真正重开数据库、租期恢复、旧执行代际拒绝、progress 静默与稳定 outbox 消息 ID。实验没有网络、模型调用或外部消息发送，不证明真实异步 Agent 循环、跨机迁移或语义 Watchdog 已实现。

其他四个 Skill 的业务逻辑、资源行为和本地打包检查，以及尚未验证的真实宿主行为，见[验证记录](docs/validation-summary.md)。

## 版本与资料

资料核验日期为 **2026-11-01**。Harness 和研究原型处于快速迭代阶段，执行任务时应核对实际 checkout、宿主和依赖要求。不能把某个 Harness master 快照的环境条件视为所有发布版本或原型的要求。

- [官方文章：Super-agent 设计探索](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg)
- [DeepSeek Harness 官方仓库](https://github.com/deepseek-ai/deepseek-harness)
- [Super-agent 原型核验提交 6337fc8](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e)
- [该提交的原型定位说明](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/6337fc823ce20251c8de8085948165c81aaa701e/README.md)

原文和原型代码以链接引用；本仓库提供的 Skill 工作流和离线示例为本次资料制作内容。
