# Service Contracts, Providers, and Consumers

[简体中文](guide.md) | English

Sources checked: **2026-11-01**. These are original implementation notes and examples based on official developer-preview documentation, not a copy of the full manual. Check the target checkout's types, README, and package versions before execution. Distinguish `master`, prereleases, and releases.

## Contracts and composition

Layering means dependency direction, not directory count. A small project can keep the three roles in one package and split them when a backend needs independent replacement or publication.

```text
Provider -- implements/depends on --> Definition <-- depends on -- Consumer (Tool)
                                         |
                           Public contract independent of backend
```

The Definition specifies requests, results, and failure semantics. The Provider decides where and how work executes. The Consumer determines how the model discovers and invokes it. This lets a remote backend replace a local backend while keeping the tool interface stable.

Service names, module names, and plugin-row IDs differ. Here the service is `textMetrics` and the tool is `text_count`. `inject = ['tools', 'textMetrics']` makes the Consumer wait for both required services; putting the Provider row first is no substitute.

Losing a service unloads dependent plugins; restoration reloads them. Do not cache concrete Provider instances at module scope to bypass this lifecycle. Query optional capabilities with `ctx.get()` at the point of use; declare core requirements with `inject`.

## Example files

```text
assets/text-metrics/
  package.json
  definition.ts       # Service, request/result, explicit default resolution
  provider.ts         # Local implementation; depends only on Definition
  consumer.ts         # Model tool; depends only on Definition
  measure.mjs         # Pure business calculation without framework dependencies
  measure.d.mts       # TypeScript declaration for measure.mjs
  measure.test.mjs    # Runs with Node's built-in test runner
```

The contract counts Unicode code points, not UTF-16 units or user-perceived graphemes. With `ignoreWhitespace=true`, remove JavaScript `\s` characters first. Combining sequences and joined emoji may contain multiple code points. Do not reinterpret this example as a general Chinese-word or display-character count.

`resolveTextMetricsRequest()` resolves optional `ignoreWhitespace` into a required boolean, so Providers do not guess defaults. The Consumer receives `{ codePoints }`, returns a number as the canonical tool value, and uses `output.render` for text content.

## Loading and acceptance

### Prerequisites

Use a source checkout installed and built according to its [official README](https://github.com/deepseek-ai/deepseek-harness). Read that checkout's `package.json` and follow its actual engines, packageManager, and build commands. Do not reuse another version's requirements blindly. This example is not a standalone npm plugin package: its `package.json` only supplies ESM metadata and a local test command, without a `dsh.bundle` manifest.

Copy all of `assets/text-metrics` into `scratch-plugin/text-metrics`, retaining relative paths. Inspect and merge any existing same-named directory to preserve user changes.

Add two plugin rows in `scratch-plugin/services.patch.yml`. Replace `C:/dev/deepseek-harness` with the actual absolute repository path using forward slashes:

```yaml
- insert:
    - id: lesson-text-metrics-provider
      name: 'C:/dev/deepseek-harness/scratch-plugin/text-metrics/provider.ts'
    - id: lesson-text-metrics-consumer
      name: 'C:/dev/deepseek-harness/scratch-plugin/text-metrics/consumer.ts'
```

Launch using the source project's command:

```powershell
pnpm dsh web --patch ./scratch-plugin/services.patch.yml
```

Absolute plugin paths avoid treating the patch location as the profile's resolution directory. If the target version cannot load `.ts` directly, build an entrypoint using that version's instructions; do not invent loading flags.

### Credential-free business checks

From the example directory:

```powershell
node --test measure.test.mjs
```

Tests cover empty strings, the whitespace option, supplementary-plane characters, and combining characters. No model API key or dependency installation is required.

### Harness integration

1. Configure existing model credentials in the Web UI and choose a workspace. Do not put keys in example files.
2. Ask: “You must call `text_count` to count `你好 Agent`, first preserving whitespace and then ignoring it.”
3. Calls should pass `ignoreWhitespace=false` and `true`, with canonical results `8` and `7`. Inspect traces; a correct model calculation is not tool-integration evidence.
4. In a disposable development configuration, temporarily remove the Provider and verify that the Consumer waits. Restore it and call again. Use a temporary overlay for existing user configuration rather than rewriting the main file.
5. For a real replacement requirement, add another Provider implementing the same Definition, change only Provider configuration, and rerun the contract checks. Do not install same-named Providers into one service domain and expect automatic selection.

Only one local Provider is included. Step 5 is an acceptance method for later extensions; no remote Provider is included or verified.

## When isolation helps

If two plugin groups require different instances/configurations of a same-named service, use the target version's groups and `isolate`, keeping each Provider and Consumer in its intended service domain. Isolation controls service lookup and instance scope; it is not a process sandbox or filesystem-permission boundary. A single domain is clearer without multiple-instance needs.

## Common fixes

| Symptom | Inspect |
| --- | --- |
| Consumer never loads | `inject` names versus `super(ctx, 'textMetrics')`; Provider activation |
| TypeScript cannot see `ctx.textMetrics` | Definition module augmentation in the type graph; missing import |
| Backend replacement still changes the tool | Concrete Provider imports or private fields exposed in the contract |
| Output error after tool execution | Whether `execute` returns a canonical number rather than content blocks or a string |
| Agents unexpectedly share an instance | Need for isolation and actual Provider/Consumer domains |

## Official sources and date

The following official pages/repository links were checked on 2026-11-01:

- [Three roles of a capability](https://deepseek-harness.github.io/deepseek-harness/develop/practice/): boundaries, dependencies, explicit resolution.
- [Services and dependencies](https://deepseek-harness.github.io/deepseek-harness/develop/framework/service): required/optional services, module augmentation, isolation.
- [Developing a tool](https://deepseek-harness.github.io/deepseek-harness/develop/basic/tool): `defineTool` parameters and outputs.
- [Adding a tool](https://deepseek-harness.github.io/deepseek-harness/reference/cookbook/adding-a-tool): canonical values, model content, cancellation, execution rules.
- [First plugin](https://deepseek-harness.github.io/deepseek-harness/develop/basic/): source loading, absolute paths, patches.
