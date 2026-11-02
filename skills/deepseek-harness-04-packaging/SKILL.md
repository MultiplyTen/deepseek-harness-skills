---
name: deepseek-harness-04-packaging
description: "为 DeepSeek Harness 插件制作可安装的 bundle、检查 npm 打包内容、组合 profile，或排查安装成功却未激活的问题。适用于插件交付与相关教学；普通 Codex Skill 打包不使用此流程。 / Build installable Harness bundles, inspect npm archives, compose profiles, or diagnose installed-but-inactive plugins. Supports delivery and teaching; excludes ordinary Codex Skill packaging."
---

[中文](#中文) | [English](#english)

## 中文

按用户使用的语言回答；仅按需读取对应语言的参考资料。中英文内容表达同一套工作流。

# DeepSeek Harness 04：打包与分发

把已实现的 Harness 插件交付为能安装、激活、移除的组合包。用户要求学习时，用一个完整小包解释流程；用户要求交付时，完成本地制包与检查。无需先调用本系列其他 Skill。

## 确定目标与运行环境

- 确认输入是 Harness 插件源码，交付目标是本地 `.tgz`、已有 profile 的安装，还是公开发布。只执行用户任务已授权的操作；制作包不意味着要发布到 npm。
- 检查项目自身的 `package.json`、锁文件、实际 `dsh --version` 与 `dsh plugin --help`。源码工作区使用其已构建的 `pnpm dsh`，独立安装使用 `dsh`；不要混用不同版本的启动器。
- 这套资源于 **2026-11-01** 对照官方在线文档核验，框架仍是技术预览。以目标 checkout 或安装版本的 CLI 与类型为准，不把 master 版本称作稳定版。

## 实施路径

1. 读取 [打包实践](references/guide.md)，明确 bundle 是可分发包，profile 是用户启动的插件组合。
2. 检查包入口、运行产物、依赖、`files` 与 `dsh.bundle.patch`。TypeScript 入口先构建为可交付的 JavaScript；不要分发只能在作者仓库解析的 `workspace:` 依赖或绝对源码路径。
3. 将 patch 中的插件引用写为发布包名或包公开的子路径。使用稳定且不冲突的配置行 id；覆盖已有行时保留完整的必要 config，因为覆盖不是深合并。
4. 可用 [最小组合包](assets/dsh-learning-marker/package.json) 演示包结构。它的入口不依赖第三方库，便于分离“包结构错误”和“运行依赖错误”；真实业务插件应保留其实际依赖。
5. 用 `python <本Skill目录>/scripts/inspect_bundle.py <包目录>` 做只读结构检查，再用项目已有的包管理器执行 pack dry-run。核对真正进入归档的文件，而不只看源码目录。
6. 创建本地 tarball，并执行 `python <本Skill目录>/scripts/inspect_bundle.py <包目录> --tarball <实际tgz路径>`。脚本不解析 Cordis YAML 语义、不验证 semver，也不证明宿主兼容性。
7. 若用户任务包括集成验证，在约定的测试 profile 中安装同一 tarball，用 `--dump-config` 核对组合层，再运行并检查插件行为；只删除本次添加的插件和测试资源。已有 profile 不重置。

## 验收与交付

- 交付实际 `.tgz` 路径、包名和版本、目标宿主版本、包内关键文件清单。
- 分开报告：结构检查、实际打包、profile 激活、业务行为、移除清理。未运行的阶段明确标为未验证。
- 安装成功但不激活，先查 `dsh.bundle` 与 profile 的 bundles 列表；入口找不到则查 exports、构建输出和 tarball 内容。不要先反复重装整个宿主。
- 对开发者教学，给出安装、验证和移除命令，并让学习者解释 `dsh.bundle` 与 `dsh.profile` 各负责什么。

实际命令与来源见 [打包实践](references/guide.md)。本 Skill 本身是 Agent Skill 目录；`assets/dsh-learning-marker` 才是示例 Harness 插件包，两者安装机制不同。

---

## English

Respond in the user's language and read only the relevant language version of a reference. Both sections describe the same workflow.

# DeepSeek Harness 04: Packaging and Distribution

Deliver implemented Harness plugins as bundles that can be installed, activated, and removed. For learning, explain the workflow with a complete small package. For delivery, build and inspect the local package. Other skills in this series need not be invoked first.

## Target and environment

- Confirm that the input is Harness plugin source and whether the target is a local `.tgz`, installation into an existing profile, or public publication. Perform actions authorized by the task; making a package does not imply npm publication.
- Inspect the project's `package.json`, lockfile, actual `dsh --version`, and `dsh plugin --help`. Use the built workspace's `pnpm dsh` for source checkouts or `dsh` for standalone installations; avoid mixing versions.
- Materials were checked against official online documentation on **2026-11-01**. The framework is a technical preview. Follow the target checkout or installed version's CLI and types; do not call `master` stable.

## Implementation

1. Read the [packaging guide](references/guide.en.md): a bundle is distributable; a profile composes the plugins the user launches.
2. Check entrypoints, runtime outputs, dependencies, `files`, and `dsh.bundle.patch`. Build TypeScript into distributable JavaScript first. Do not distribute `workspace:` dependencies or absolute source paths that resolve only in the author's checkout.
3. Reference published package names or public subpaths in the patch. Use stable, nonconflicting row IDs. Preserve all necessary configuration when overriding a row because overrides are not deep merges.
4. The [minimal bundle](assets/dsh-learning-marker/package.json) demonstrates structure without third-party runtime libraries, separating package errors from dependency errors. Real plugins retain their actual dependencies.
5. Run `python <skill-directory>/scripts/inspect_bundle.py <package-directory>` for a read-only structural check, then use the project's package manager for a pack dry run. Inspect files that actually enter the archive, not just the source tree.
6. Create a local tarball and run `python <skill-directory>/scripts/inspect_bundle.py <package-directory> --tarball <actual-tgz-path>`. This script does not interpret Cordis YAML semantics, validate semver, or prove host compatibility.
7. If integration testing is in scope, install that tarball into the agreed test profile, inspect composition using `--dump-config`, then run and check behavior. Remove only resources added for this task; do not reset an existing profile.

## Acceptance and delivery

- Deliver the actual `.tgz` path, package name and version, target host version, and key archive files.
- Report structural inspection, actual packing, profile activation, business behavior, and removal separately. Mark unexecuted stages as unverified.
- If installation succeeds without activation, inspect `dsh.bundle` and the profile's bundles list. If the entrypoint is missing, inspect exports, build outputs, and tarball contents before reinstalling the host.
- For teaching, provide installation, verification, and removal commands, and ask the learner to explain `dsh.bundle` versus `dsh.profile`.

See the [guide](references/guide.en.md) for commands and sources. This directory is an Agent Skill; only `assets/dsh-learning-marker` is an example Harness plugin package. Their installation mechanisms differ.
