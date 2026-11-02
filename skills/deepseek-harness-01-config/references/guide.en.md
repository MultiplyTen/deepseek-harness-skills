# Configuration Exercises and Troubleshooting

[简体中文](guide.md) | English

Sources checked: **2026-11-01**. This guide covers DeepSeek Harness plugin configuration. The example is original teaching material, not a plugin released by DeepSeek. It follows the official documentation interfaces checked on that date and does not promise compatibility with every preview version.

## Configuration flow

Overlay `config` → exported plugin `Config` schema → `apply(ctx, config)` → parsed values used during tool execution.

`ctx` provides services and registration capabilities; it is not chat history. `ignoreWhitespace` configures a plugin instance, while `text` is an input to each tool call. The former changes the instance's counting strategy; the latter changes only the text being counted.

Whitespace is preserved by default. Enabling the option removes only characters matched by JavaScript `\s`. Counting uses Unicode code points: combining characters and some emoji sequences may contain multiple code points. This is not a count of visible glyphs.

## Minimal path in an existing project

Prerequisite: a DeepSeek Harness source checkout matching the intended version, with installation and build steps from its README completed. Check its Node/pnpm constraints in `package.json` first. If setup is part of the task, prepare a matching environment within the user's authorization. The host installer is not included here.

1. Choose a new teaching directory in the project, such as `scratch-plugin-config`.
2. Copy all three files from `assets/example/`: `plugin.ts`, `text-count.mjs`, and `text-count.d.mts`. Do not copy only the TypeScript entrypoint.
3. Generate a new overlay inside an existing directory. Replace every placeholder below with an actual absolute path before running it:

```powershell
python <skill-directory>/scripts/write_overlay.py --plugin <repository-directory>/scratch-plugin-config/plugin.ts --output <repository-directory>/scratch-plugin-config/cordis.yml --ignore-whitespace
```

The script checks that the entrypoint exists, escapes the path as a JSON string in YAML, and refuses to overwrite an existing file. Omitting `--ignore-whitespace` writes explicit `false`.

4. From the Harness repository root, use that project's launcher:

```powershell
pnpm dsh web --patch ./scratch-plugin-config/cordis.yml
```

5. Configure the user's own model route in the Web UI and select a workspace. Ask the model: “You must call `text_count` to count `你好 Agent`.” Inspect the recorded tool name, input, and result `7`.

To test schema defaults, back up the overlay and remove only `ignoreWhitespace` from the row, keeping the plugin row itself. After reload, the same input should produce `8`. An existing profile can contribute additional configuration; inspect the effective result too.

The configuration page contains a relative-source-path snippet, while the basic plugin page says local overlays do not change the loader's resolution directory. This skill generates absolute paths consistently so success does not depend on the launch directory.

## Three verification layers

| Layer | Check | What it establishes |
| --- | --- | --- |
| Business logic | Import `text-count.mjs` and run assertions | Counting and whitespace behavior match the examples |
| Plugin loading | Load with the actual Harness and inspect diagnostics | Imports, Config schema, and service dependencies connect |
| Model invocation | Inspect actual tool calls and results | The selected agent can discover and execute the tool |

The counting module can be verified offline. If Harness dependencies or model credentials are unavailable, mark the last two layers as unexecuted; a mocked `ctx` does not establish full integration.

In the copied example directory, run this check without Harness dependencies; it should print `7`:

```powershell
node --input-type=module -e "import { countText } from './text-count.mjs'; console.log(countText('你好 Agent', true))"
```

## Troubleshooting

- **Changing `config` has no effect:** check the loaded overlay, later overriding layers, and row IDs. Inspect effective configuration and loading logs before investigating HMR. If hot reload cannot be confirmed, explicitly restart the development process you launched.
- **Explicit `false` behaves like enabled:** look for `||` defaults. Defaults belong in the schema.
- **Standard Schema error:** verify that the runtime `Config` export is a compatible schema. A TypeScript interface does not exist at runtime.
- **`ctx.tools` unavailable:** inspect `inject` and whether the current profile supplies the tool service. Silently skipping registration hides a missing dependency.
- **Type/import mismatch:** follow the installed version's package exports and source, adapting the example. Do not use `master` APIs while claiming release compatibility.

## Exercise

Change the policy to ignore ordinary spaces but preserve newlines. First predict `8` for `你 好\nAgent`, then change the pure logic and verify it. Update the field name and description to reflect the new meaning; an internal change must not leave a misleading public contract.

## Official sources

- [Plugin configuration](https://deepseek-harness.github.io/deepseek-harness/develop/basic/config): `Config` types, schemas, defaults, and validation.
- [Chinese source of that page](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/config.zh.md): current imports and export forms.
- [Built-in tool plugin Config](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/subagent/tool-subagent/src/index.ts): a Schemastery runtime schema and same-named TypeScript type; do not copy its subagent-specific fields.
- [Developing a tool](https://deepseek-harness.github.io/deepseek-harness/develop/basic/tool): parameters, canonical results, and rendering.
- [First plugin](https://deepseek-harness.github.io/deepseek-harness/develop/basic/): source prerequisites and absolute-path overlays.
- [Official repository](https://github.com/deepseek-ai/deepseek-harness): actual checkout dependencies and commands.
