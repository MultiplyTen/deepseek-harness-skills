# 打包实践

核验日期：2026-11-01。以下是面向交付任务的原创操作说明，不是某个发布版的兼容性保证。实施前检查目标版本的实际接口。

## 选择交付对象

| 对象 | 负责的事 | 识别字段或文件 |
| --- | --- | --- |
| Agent Skill | 给编码助手提供任务工作流 | `SKILL.md` |
| Harness 插件模块 | 注册服务、工具、事件等能力 | `apply(ctx)` 等导出 |
| Harness bundle | 分发代码及配置层 | `package.json` 中的 `dsh.bundle.patch` |
| Harness profile | 组合可启动应用 | `dsh.profile.bundles` |

一个插件可以在开发期通过本地 overlay 加载；对他人分发时，需要把入口和配置层一起装进包。单纯能被 npm 安装，不代表 Harness 会启用它。[官方组合包教程](https://deepseek-harness.github.io/deepseek-harness/develop/basic/publish)

## 可操作的最小示例

将 `assets/dsh-learning-marker` 复制到自己的项目或教学目录。该包只打印加载和卸载标记，用来验证安装与生命周期，不调用模型。

在复制后的包目录中执行：

```powershell
npm pack --dry-run --json --ignore-scripts
npm pack --json --ignore-scripts
```

此示例已是 JavaScript 且没有构建脚本，因此可以跳过生命周期脚本。实际 TypeScript 包必须先完成项目规定的构建；不要为了 pack 成功跳过必要构建。若项目使用 pnpm，可以改用其 `pack --dry-run` 与 `pack --json`，先看当前版本帮助。dry-run 只用于审阅，不能代替检查最终 tarball。[npm pack](https://docs.npmjs.com/cli/v11/commands/npm-pack/)、[pnpm pack](https://pnpm.io/cli/pack)

`scripts/inspect_bundle.py` 的路径相对于本 Skill；参数应指向复制后的包目录。脚本只读本地文件，不安装任何包：

```powershell
python /path/to/skill/scripts/inspect_bundle.py /path/to/dsh-learning-marker
python /path/to/skill/scripts/inspect_bundle.py /path/to/dsh-learning-marker --tarball /path/to/dsh-learning-marker-0.1.0.tgz
```

PowerShell 中把示意路径替换成真实路径并按需加引号。不要把这些示意路径原样写入用户配置。

## 在独立测试 profile 激活

先用目标宿主的帮助确认 CLI。以下 profile 名应换成此次任务独占的名字，tarball 路径使用真实路径：

```powershell
dsh plugin --profile lesson-package-check add ./dsh-learning-marker-0.1.0.tgz
dsh --profile lesson-package-check --dump-config
dsh --profile lesson-package-check
```

检查组合结果包含该包贡献的配置行，运行时出现 `[learning-marker] active`。退出宿主时应出现对应释放标记。只需要配置检查时，不启动模型会话。

任务完成后移除本次安装：

```powershell
dsh plugin --profile lesson-package-check remove dsh-learning-marker
```

这个最小测试 profile 不保证附带 Web UI。需要浏览器界面时，应选择或组合带有 Web 应用的 profile，而不是假设任何 profile 都监听同一个端口。[CLI 行为参考](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/reference/README.zh.md)

## 依赖与版本

- `files` 限定发布内容，但最终以 pack 得到的归档为准；检查入口、patch、运行时资源均在包内，且没有带入凭据或无关项目文件。
- 需要共享宿主实例的 dsh 包按官方依赖规则声明 peer 与开发依赖；实际包名和版本范围来自目标工程。普通运行依赖不能只出现在 devDependencies。
- 示例未声明 `engines.dsh`，因为它没有经过真实宿主版本矩阵验证。正式交付应根据已测试版本设置兼容范围，并注意 semver 对 prerelease 的处理。
- 源码 git 安装与预构建 tarball 的构建路径不同。若从 git 分发，核对自包含构建、包管理器对 prepare 的处理以及实际产物，不能假设 install 会替你执行任意 build 脚本。[官方组合包教程](https://deepseek-harness.github.io/deepseek-harness/develop/basic/publish)

## 修复顺序

| 现象 | 优先检查 |
| --- | --- |
| 包已安装但无能力 | bundle manifest、profile bundles、patch 行是否生效 |
| 加载找不到入口 | `main` / `exports`、tarball 产物、源码与运行路径 |
| 配置项意外消失 | 后层 patch 是否替换整个 config，dump 后的实际值 |
| 本地能跑、别人不能 | 作者目录绝对路径、workspace 依赖、未发布的构建资源 |
| 卸载后仍有活动 | 插件是否通过 ctx 管理注册与资源，而非打包本身 |

## 完成证据

保留包名、版本、宿主版本、pack 文件列表、tarball 校验结果、dump-config 中相关层，以及实际启动/卸载观察。没有宿主环境时可以交付结构已检查的包，但不要写“已完成真实安装联调”。
