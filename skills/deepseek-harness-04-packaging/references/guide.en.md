# Packaging Practice

[简体中文](guide.md) | English

Sources checked: **2026-11-01**. These original delivery instructions do not guarantee compatibility with a particular release. Inspect the target version's actual interfaces first.

## Choose the deliverable

| Object | Responsibility | Identifying field/file |
| --- | --- | --- |
| Agent Skill | Workflow for a coding assistant | `SKILL.md` |
| Harness plugin module | Register services, tools, events | Exports such as `apply(ctx)` |
| Harness bundle | Distribute code and configuration layers | `package.json` → `dsh.bundle.patch` |
| Harness profile | Compose a launchable application | `dsh.profile.bundles` |

A plugin can load through a local overlay during development. Distribution requires packaging its entrypoint and configuration layer together. npm installation alone does not mean Harness will activate it. [Official bundle tutorial](https://deepseek-harness.github.io/deepseek-harness/develop/basic/publish)

## Minimal working example

Copy `assets/dsh-learning-marker` into your project or teaching directory. It prints load/dispose markers to verify installation and lifecycle without calling a model.

In the copied package directory:

```powershell
npm pack --dry-run --json --ignore-scripts
npm pack --json --ignore-scripts
```

This example already contains JavaScript and has no build script, so skipping lifecycle scripts is appropriate. Real TypeScript packages must complete their required build first; do not skip necessary builds merely to make packing succeed. If the project uses pnpm, consult the installed version's help before using its `pack --dry-run` and `pack --json`. A dry run is for review and does not replace inspecting the final tarball. [npm pack](https://docs.npmjs.com/cli/v11/commands/npm-pack/), [pnpm pack](https://pnpm.io/cli/pack)

The following script path is relative to this skill; arguments point to the copied package. The script reads local files and installs nothing:

```powershell
python /path/to/skill/scripts/inspect_bundle.py /path/to/dsh-learning-marker
python /path/to/skill/scripts/inspect_bundle.py /path/to/dsh-learning-marker --tarball /path/to/dsh-learning-marker-0.1.0.tgz
```

Replace illustrative paths with real paths and quote them in PowerShell where needed. Do not write placeholder paths into user configuration.

## Activate in a separate test profile

Check the target host's CLI help first. Replace the profile name with one exclusive to this task and use the actual tarball path:

```powershell
dsh plugin --profile lesson-package-check add ./dsh-learning-marker-0.1.0.tgz
dsh --profile lesson-package-check --dump-config
dsh --profile lesson-package-check
```

Inspect the composed configuration for the package's row. Runtime should print `[learning-marker] active`, with a corresponding disposal marker when the host exits. If only configuration inspection is needed, do not start a model session.

Remove this installation after the task:

```powershell
dsh plugin --profile lesson-package-check remove dsh-learning-marker
```

This minimal profile does not necessarily include a Web UI. For a browser interface, choose or compose a profile containing a Web application; do not assume every profile listens on one common port. [CLI reference](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/reference/README.zh.md)

## Dependencies and versions

- `files` limits published content, but the actual pack archive is authoritative. Check that entrypoints, patches, and runtime assets are included, without credentials or unrelated project files.
- Declare peer/development dependencies according to official rules for dsh packages sharing a host instance. Use names and version ranges from the target project. Ordinary runtime dependencies cannot exist only in devDependencies.
- The example omits `engines.dsh` because no real host-version matrix was tested. Set compatibility ranges from tested versions for a real delivery, accounting for prerelease semver behavior.
- Git-source installation and prebuilt tarballs have different build paths. For git distribution, check self-contained builds, the package manager's `prepare` behavior, and actual outputs. Do not assume installation runs arbitrary build scripts. [Official bundle tutorial](https://deepseek-harness.github.io/deepseek-harness/develop/basic/publish)

## Troubleshooting order

| Symptom | Inspect first |
| --- | --- |
| Installed package exposes no capability | Bundle manifest, profile bundles, effective patch rows |
| Missing entrypoint | `main` / `exports`, tarball outputs, source versus runtime paths |
| Configuration disappears | A later patch replacing the entire config; dumped effective values |
| Works only for the author | Absolute author paths, workspace dependencies, unpublished build resources |
| Activity remains after removal | Plugin registration/resource ownership through ctx, rather than packaging alone |

## Completion evidence

Keep package name/version, host version, pack file list, tarball checks, relevant dump-config layers, and actual startup/disposal observations. Without a host, deliver a structurally checked package while explicitly marking real installation/integration as unverified.
