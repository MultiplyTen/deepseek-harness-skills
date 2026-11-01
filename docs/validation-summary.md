# 验证范围

记录日期：2026-11-01。这里区分格式检查、离线业务验证与真实运行环境联调，避免把演示成功扩大为生产能力声明。

## 五个 Skill 共同检查

- 通过 skill-creator 随附 `quick_validate.py` 格式检查。
- 检查了界面元数据、调用名称、UTF-8 文本和全部内部 Markdown 引用。
- 对涉及的 JSON/YAML 和 Python 文件进行了语法检查。
- 分发 ZIP 已检查归档完整性，缓存和临时数据库未纳入发布目录。

## 示例验证

| Skill | 已完成的检查 | 不应据此推断 |
| --- | --- | --- |
| 01 配置 | 9 条纯计数逻辑断言；overlay 生成的绝对路径、布尔值和拒绝覆盖行为；入口语法检查 | 未验证真实 Harness 的运行时 schema 校验、插件加载或模型调用 |
| 02 生命周期 | 3 项资源行为测试；TypeScript 入口语法检查 | 未验证实际 Cordis 依赖消失恢复或 HMR |
| 03 服务 | 4 项业务契约测试；3 个 TypeScript 文件语法检查 | 未验证实际服务注册、Provider 替换或模型联调 |
| 04 打包 | 实际 npm tarball；manifest、入口和 patch 检查；缺失 bundle、越界路径及归档漏文件检查；模拟加载和幂等释放 | 未运行真实 DSH 安装、profile 激活或移除 |
| 05 Super-agent | 10 项离线不变量测试；数据库真实重开；独立的双任务聊天/CI 架构试用 | 未部署常驻服务，未验证平台鉴权、外部投递、真实异步 Agent 循环、跨机迁移或完整语义 Watchdog |

第五个 Skill 的消息发送只由本地 outbox 模拟，不能承诺外部 exactly-once。测试中的 `start_new=True` 表示调用方已授予的模拟接纳决定，不是自然语言授权判断。

## 资料与实现边界

已核对[官方文章](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg)与[公开原型的固定提交](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e)。文章属于架构探索，公开原型与内部实现不完全相同；第五个 Skill 的具体证据链接已固定到核验提交。

核验时原型自身声明 Node `^22.19.0 || >=24.0.0`、DSH `^0.2.1-alpha.2`。另一个 Harness master 快照声明 Node `>=24.9.0`；两者是不同版本目标，真实集成应同时满足实际安装宿主与原型的要求。随附运维路径也不能未经适配就当作原生 Windows 部署步骤。

本仓库没有执行账户创建、GitHub/飞书消息发送、模型请求或真实 Super-agent 部署。部署与外部写入应属于后续明确任务。
