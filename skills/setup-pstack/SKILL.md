---
name: setup-pstack
description: Configure which models and reasoning effort pstack uses per role. Detects your available models and writes ~/.grok/pstack-models.toml plus ~/.grok/roles/*.toml. Use for /setup-pstack, "configure pstack models", or changing pstack's model or effort choices.
---

# Setup pstack

Write `~/.grok/pstack-models.toml` (model slugs and `[effort]`) and pstack-managed files under `~/.grok/roles/`. Skills read the toml for `task.model`. Grok Build applies effort from the role files when `task.subagent_type` matches the file stem. Missing file, missing key, `inherit-parent`, or `auto` means omit `task.model` and omit the role overlay so the child inherits the parent. Spawn-site resolution: [`references/resolve-model.md`](references/resolve-model.md) and [`references/resolve-effort.md`](references/resolve-effort.md).

The models file is an override layer, not a grok-build `[subagents.models]` table. That table maps agent types (`explore`, `plan`), not pstack roles. Effort is `SubagentRole.reasoning_effort` in `~/.grok/roles/<role>.toml`, not a `task` field.

## Ask the human

This section is the only source for `ask_user_question`. Copy the option shape. Do not invent options. Do not quote **Agent only** into the TUI.

The question text, every option `label`, and every option `description` may use `inherit-parent`, `auto`, slugs from this session's detected set, effort levels `low` `medium` `high` `xhigh` `max`, pstack role key names, and plain words that explain those choices (every role, this chat's model, this chat's effort, recommended split, mechanical, swarm, judgment, how-explainer, independent-verifier, customize per role). Nothing else.

### Models

First question. `questions[].question` is a short how-should-pstack-pick-models line. Options, in this order, and no others:

1. `inherit-parent` for every role (recommended). Children use this chat's model.
2. One option per detected slug. That slug for every role. On this box that is often `grok-4.6` and `grok-4.5`. Use whatever step 1 actually detected. Do not add a slug that was not detected.
3. Customize per role.

If they pick customize: follow-up questions, one role at a time or grouped. Each role's options are only `inherit-parent`, `auto`, and each detected slug.

Panel roles (`how-critics`, `arena-runners`, `arena-cross-judge-pool`, `architect-runners`, `interrogate-reviewers`) are arrays. Default one `inherit-parent` entry. Customize may add more entries. Each entry is still `inherit-parent`, `auto`, or a detected slug. One `task` spawn per entry.

### Effort

Second question, after models. `questions[].question` is a short how-should-pstack-pick-reasoning-effort line. Options, in this order, and no others:

1. `inherit-parent` for every role (recommended). Children use this chat's effort.
2. Recommended split. `low` for mechanical and swarm workers (`feature`, `refactoring`, `bug-fix`, `perf-issue`, `hillclimb`, `swarm-workers`, `arena-runners`, `how-explorer`, `how-critics`). `xhigh` for judgment, how-explainer, and independent-verifier (`judgment-and-prose`, `hardest-tasks`, `how-explainer`, `independent-verifier`, `reflect-judgment`, `interrogate-reviewers`, `arena-cross-judge-pool`). `inherit-parent` for every other role.
3. `xhigh` for every role.
4. Customize per role.

If they pick customize: follow-up questions, one role at a time or grouped. Each role's options are only `inherit-parent`, `low`, `medium`, `high`, `xhigh`, `max`. Effort is one scalar per role even when the model key is an array.

Do not add an option for `none` or `minimal`.

## Steps

### 1. Detect available models

Enumerate slugs the `task` tool accepts in `model` this session.

- Probe with an invalid `task.model` and read the rejection text for valid slugs.
- Run `grok models` if the CLI exposes it.
- Use `grok inspect --json` only if that JSON actually lists models. `InspectReport` often has no models field.

Never write a slug you have not confirmed this session. `inherit-parent` and `auto` are always valid and are not slugs: omit `model` on `task`.

Allowed effort levels are `inherit-parent`, `low`, `medium`, `high`, `xhigh`, `max`. Those last five are `AgentDefinition` `Effort::VALID_VALUES` and `ReasoningEffort` tokens grok-build parses. `inherit-parent` is not sent anywhere: skip the role overlay.

### 2. Load current state

If `~/.grok/pstack-models.toml` exists, read it (top-level model keys and `[effort]`). Otherwise every model role starts as `inherit-parent` and every `[effort]` key starts as `inherit-parent` (the example in step 5). Do not load any other models file.

### 3. Map and confirm

Show every role with its current model and effort. Mark any real slug not in the detected set as needing a choice. Confirm with `ask_user_question` using **Ask the human** above. Ask models first, then effort.

`arena-cross-judge-pool` is an array. Arena picks one value whose family differs from the parent when the file names more than one detected slug. `swarm-workers` is the default for every `/swarm` worker unless a race names a model per arm.

When they pick inherit-parent models everywhere, write the step 5 model keys. When they pick one detected slug everywhere, write that slug in every model key. When they customize, write only those choices.

When they pick inherit-parent effort everywhere, write the step 5 `[effort]` table. When they pick the recommended split or xhigh everywhere or customize, write those `[effort]` values.

### 4. Validate

Every real slug must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen slug is unavailable, ask again with the same allowed options.

Every `[effort]` value must be `inherit-parent`, `auto`, `low`, `medium`, `high`, `xhigh`, or `max`. If not, ask again with the effort options above.

### 5. Write the files

Overwrite `~/.grok/pstack-models.toml` so re-runs stay idempotent.

Pstack-managed role files live at `~/.grok/roles/<role-key>.toml` for the keys in the example. Create `~/.grok/roles/` if needed.

- If `[effort].<key>` is `inherit-parent` or `auto` or missing, **delete** that pstack-managed role file if it exists so a stale overlay cannot pin effort.
- If `[effort].<key>` is `low`, `medium`, `high`, `xhigh`, or `max`, write only:

```toml
description = "pstack <role-key> role"
reasoning_effort = "<level>"
```

Do not write `model`, `prompt_file`, `default_capability_mode`, or `default_isolation` into those files. Do not edit `~/.grok/config.toml`. Do not delete role files whose names are not pstack keys.

EXAMPLE (inherit-parent models and inherit-parent effort). Replace a model value with a real slug only when that slug was detected this session. Replace an `[effort]` value with `low` / `medium` / `high` / `xhigh` / `max` only when the human picked that level.

```toml
# Write only slugs detected this session (task.model rejection, grok inspect, grok models).
# inherit-parent or auto: omit task.model; child inherits the parent.
# Missing key: same as inherit-parent. Do not invent slugs.
# Array keys: one task spawn per entry. Without a toml, skills spawn one child and omit model.
#
# [effort]: inherit-parent or auto or missing key: do not write ~/.grok/roles/<key>.toml.
# low/medium/high/xhigh/max: write ~/.grok/roles/<key>.toml with that reasoning_effort.
# Skills never send reasoning_effort on task. Spawn subagent_type = the role key.

feature = "inherit-parent"
refactoring = "inherit-parent"
bug-fix = "inherit-parent"
perf-issue = "inherit-parent"
hillclimb = "inherit-parent"
judgment-and-prose = "inherit-parent"
hardest-tasks = "inherit-parent"
how-explorer = "inherit-parent"
how-explainer = "inherit-parent"
how-critics = ["inherit-parent"]
why-investigators = "inherit-parent"
why-synthesizer = "inherit-parent"
reflect-tooling = "inherit-parent"
reflect-judgment = "inherit-parent"
arena-runners = ["inherit-parent"]
arena-cross-judge-pool = ["inherit-parent"]
swarm-workers = "inherit-parent"
architect-runners = ["inherit-parent"]
interrogate-reviewers = ["inherit-parent"]
independent-verifier = "inherit-parent"

[effort]
feature = "inherit-parent"
refactoring = "inherit-parent"
bug-fix = "inherit-parent"
perf-issue = "inherit-parent"
hillclimb = "inherit-parent"
judgment-and-prose = "inherit-parent"
hardest-tasks = "inherit-parent"
how-explorer = "inherit-parent"
how-explainer = "inherit-parent"
how-critics = "inherit-parent"
why-investigators = "inherit-parent"
why-synthesizer = "inherit-parent"
reflect-tooling = "inherit-parent"
reflect-judgment = "inherit-parent"
arena-runners = "inherit-parent"
arena-cross-judge-pool = "inherit-parent"
swarm-workers = "inherit-parent"
architect-runners = "inherit-parent"
interrogate-reviewers = "inherit-parent"
independent-verifier = "inherit-parent"
```

### 6. Confirm

Tell the user `~/.grok/pstack-models.toml` was written and that matching files under `~/.grok/roles/` were added or removed. New sessions pick them up. Re-running this skill updates them. Name those grok paths. Do not name other paths.

### 7. Offer a verification skill (optional)

Look for a `verify-*` skill under `.grok/skills/` or an existing harness. If neither exists, offer once via `ask_user_question` to generate one with `/create-verification-skill`. That question is yes or no. On yes, write `.grok/skills/verify-<app>/`. On no, move on.

## Agent only. Do not quote this section

Do not put any sentence from this section into `ask_user_question`, option labels, option descriptions, or the step 6 confirmation.

Write **only** `~/.grok/pstack-models.toml` and pstack-managed files under `~/.grok/roles/`. Do not create `~/.cursor/rules/pstack-models.mdc` or any file under a Cursor rules directory.

Do not read `~/.cursor/rules/pstack-models.mdc`. If that file exists on disk, ignore it. It is not a source of defaults on Grok Build.

Proceed only on Grok Build: live `task` tool (`run_in_background`, `isolation`) and/or `grok` CLI. If this session would write Cursor rules paths, stop. Do not write those paths. Do not discuss that stop in the TUI. This plugin is the Grok Build port.

Do not copy an example table from another product, from older revisions of this skill, or from training memory.

Do not offer a menu item that is not in **Ask the human**. Do not mention other products in the TUI. Do not offer to port or mix a mapping from another tool.
