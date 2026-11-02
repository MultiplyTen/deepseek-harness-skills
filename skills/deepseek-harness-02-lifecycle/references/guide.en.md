# Lifecycle Development and Troubleshooting

[简体中文](guide.md) | English

This supplements the executable workflow. Sources checked: **2026-11-01**. Read the relevant sections as needed rather than loading the entire guide into every task.

## Version and launch context

Read the repository or installed package's version, `engines`, and lockfile. Record the actual profile and patch arguments. The official README describes Harness as a developer preview with potentially breaking APIs. At the checked snapshot, `master/package.json` was `0.2.2-alpha.2`, requiring Node `>=24.9.0`. This is a dated snapshot, not a requirement for every release or a claim of a latest stable version.

Report concrete differences when the environment does not meet the target checkout's requirements. Do not upgrade global Node or change other projects' package-manager configuration on the user's behalf. Pure JavaScript example tests need no Harness installation; real integration must satisfy the actual version's requirements.

## Dependencies, failure, and waiting

The official lifecycle distinguishes waiting for dependencies, executing `apply`, running, load failure, and disposal. Diagnose missing required services separately from an exception inside `apply`.

Declare required services in `inject` so the framework schedules loading. Losing a dependency unloads its consumers; restoring it reloads them. Query optional services with `ctx.get()` where used and handle absence. A reference to an optional service captured only at load time is not necessarily valid forever.

`pulse.ts` manages a local timer through `ctx.effect()` and consumes no service, so it intentionally omits `inject`. A real tool plugin declares `['tools']` only when it requires the tool registry.

## Fix resources by owner

| Resource | Created through | Cleanup owner |
| --- | --- | --- |
| Framework tool/listener registrations | Registration methods on the current plugin's `ctx` | Revoked with that plugin scope |
| Native timers, connections, file watchers | Node or third-party libraries | Disposer returned by `ctx.effect()` |
| Child plugins | `ctx.plugin()` | Their own scopes; parent disposal also removes children |
| In-flight asynchronous work | Business code | Stop accepting new work; cancel or await through actual interfaces |

Do not create native `setInterval()` at module scope. Module caching and plugin-instance lifetimes differ; reloading a file can create another timer. Cordis does not automatically discover arbitrary unmanaged timers.

Close asynchronous resources with ordering dependencies sequentially in one disposer. For example, stop the producer, await in-flight work, then close their connection. Separate asynchronous disposers starting in reverse order do not guarantee sequential completion.

## Included example

Copy all four files in `assets/lifecycle-plugin` to `scratch-lifecycle` in a prepared Harness source checkout. Keep the `.d.mts` declaration so TypeScript can import the JavaScript helper correctly.

Run the pure resource tests first:

```powershell
node --test ./scratch-lifecycle/managed-pulse.test.mjs
```

A controlled scheduler verifies cancellation, idempotent disposal, and absence of old output after replacement; it does not simulate Cordis. Example callbacks are synchronous. Replacing them with network requests requires new cancellation/waiting behavior; existing tests do not establish it.

From the repository root, generate an overlay using an actual absolute path:

```powershell
$lessonPlugin = (Resolve-Path -LiteralPath './scratch-lifecycle/pulse.ts').Path.Replace('\', '/')
$lessonOverlay = @(
  '- insert:'
  '    - id: lifecycle-pulse'
  ('      name: ' + ($lessonPlugin | ConvertTo-Json -Compress))
)
$lessonOverlay | Out-File -LiteralPath './scratch-lifecycle/cordis.yml' -Encoding utf8 -NoClobber
pnpm dsh web --patch ./scratch-lifecycle/cordis.yml
```

The plugin path must be absolute. If `cordis.yml` already exists, the command refuses to overwrite it. Choose a new overlay filename and update the launch argument too. Complete source installation/build prerequisites from the official README; Harness and its dependencies are not included.

Expect instance-tagged `loaded` and subsequent `pulse` logs. Dispose the instance using the target version's supported unloading interface. Check its `disposed` log and that further output stops. Reloading should produce output only from the new instance. A test host holding the return value of `ctx.plugin()` can call `dispose()` and await its Promise.

## Events and hot reload

Distinguish runtime Cordis events from persisted session events. Session records such as `tool/call` and `tool/result` do not automatically become same-named `ctx.on()` events. Observe records through the current version's session-event API and inspect types. Follow actual event signatures and modes rather than guessing arguments from names.

Ordinary observers should not alter the pipeline. A waterfall interceptor must delegate to `next()` to continue downstream; omit delegation only for an intentional short circuit.

Check that HMR appears in effective configuration, that the version enables source watching, and that the edited path is watched. Configuration reload, source HMR, and restart are distinct results; record them separately. If no reload interface is available, deliver the static fix and resource-test results while marking real reload as unverified.

## Minimal acceptance record

Record trigger, instance ID, and outcome: one initial load, old callbacks stopping after disposal, and only the new instance working after reload. Add dependency-loss/restoration checks for required services. For asynchronous cleanup, verify dependent resources do not close prematurely. Do not extrapolate test-stub results to unexecuted framework behavior.

## Official sources

- [Plugins and lifecycle](https://deepseek-harness.github.io/deepseek-harness/develop/framework/): dependency loading, ownership, disposal, HMR.
- [Services and dependencies](https://deepseek-harness.github.io/deepseek-harness/develop/framework/service): required/optional services and dependency loss.
- [Events](https://deepseek-harness.github.io/deepseek-harness/develop/framework/events): event modes, session-event distinctions, waterfall delegation.
- [First plugin](https://deepseek-harness.github.io/deepseek-harness/develop/basic/): source prerequisites and absolute-path overlays.
- [Official README](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.md): preview status and source execution.
- [master package.json](https://github.com/deepseek-ai/deepseek-harness/blob/master/package.json): version/environment constraints at verification time.
