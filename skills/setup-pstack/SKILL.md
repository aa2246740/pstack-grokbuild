---
name: setup-pstack
description: Configure which models and reasoning effort pstack uses per role. Detects your available models and writes ~/.grok/pstack-models.toml plus ~/.grok/roles/*.toml. Use for /setup-pstack, "configure pstack models", or changing pstack's model or effort choices.
---

# Setup pstack

Write `~/.grok/pstack-models.toml` (model slugs and `[effort]`) and pstack-managed files under `~/.grok/roles/`. This is an **override layer**. A fresh install with no setup already uses the shipped default: `grok-4.6` plus per-role `effort` on the plugin agents. See [`references/defaults.toml`](references/defaults.toml), [`references/resolve-model.md`](references/resolve-model.md), and [`references/resolve-effort.md`](references/resolve-effort.md).

Skills read the toml for `task.model`. Grok Build applies effort from `~/.grok/roles/<role>.toml` when that overlay exists (`SubagentRole.reasoning_effort`), else from the plugin agent's frontmatter `effort`. Missing override file uses the shipped default. Missing key or `inherit-parent` or `auto` in an existing toml: omit `task.model`; delete the role overlay so frontmatter remains.

The models file is not a grok-build `[subagents.models]` table. That table maps agent types (`explore`, `plan`), not pstack roles. Never send `reasoning_effort` on `task`.

## Ask the human

This section is the only source for `ask_user_question`. Copy the option shape. Do not invent options. Do not quote **Agent only** into the TUI.

The question text, every option `label`, and every option `description` may use `inherit-parent`, `auto`, slugs from this session's detected set, effort levels `low` `medium` `high` `xhigh` `max`, pstack role key names, and plain words that explain those choices (every role, this chat's model, shipped default, grok-4.6, recommended split, mechanical, instruction-following, judgment, how-explainer, independent-verifier, customize per role). Nothing else.

### Models

First question. `questions[].question` is a short how-should-pstack-pick-models line. Options, in this order, and no others:

1. Shipped default (recommended), only if `grok-4.6` is in the detected set: `grok-4.6` for every role. Panel roles get one `grok-4.6` entry each.
2. `inherit-parent` for every role. Children use this chat's model.
3. One option per **other** detected slug. That slug for every role. On this box that is often `grok-4.5`. Use whatever step 1 actually detected. Do not add a slug that was not detected. Do not repeat `grok-4.6` here if it is already option 1.
4. Customize per role.

If `grok-4.6` was not detected, skip option 1. Then option 2 (inherit-parent) is first and recommended.

If they pick customize: follow-up questions, one role at a time or grouped. Each role's options are only `inherit-parent`, `auto`, and each detected slug.

Panel roles (`how-critics`, `arena-runners`, `arena-cross-judge-pool`, `architect-runners`, `interrogate-reviewers`) are arrays. Shipped default is one `grok-4.6` entry. Customize may add more entries. Each entry is still `inherit-parent`, `auto`, or a detected slug. One `task` spawn per entry.

### Effort

Second question, after models. `questions[].question` is a short how-should-pstack-pick-reasoning-effort line. Options, in this order, and no others:

1. Shipped default (recommended). `low` for `feature`, `refactoring`, `how-explorer`, `why-investigators`, `swarm-workers`. `high` for `bug-fix`, `perf-issue`, `hillclimb`, `reflect-tooling`. `xhigh` for `judgment-and-prose`, `hardest-tasks`, `how-explainer`, `why-synthesizer`, `reflect-judgment`, `independent-verifier`, `how-critics`, `arena-runners`, `arena-cross-judge-pool`, `architect-runners`, `interrogate-reviewers`.
2. `inherit-parent` for every role. No `~/.grok/roles` overlay. Plugin agent frontmatter stays.
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

Allowed effort levels are `inherit-parent`, `low`, `medium`, `high`, `xhigh`, `max`. Those last five are `AgentDefinition` `Effort::VALID_VALUES` and `ReasoningEffort` tokens grok-build parses. `inherit-parent` is not sent on `task`: skip the role overlay.

### 2. Load current state

If `~/.grok/pstack-models.toml` exists, read it (top-level model keys and `[effort]`). Otherwise the current state is [`references/defaults.toml`](references/defaults.toml). If `grok-4.6` is not in the detected set, treat every model key as `inherit-parent` while keeping the `[effort]` table from that file. Do not load any other models file.

### 3. Map and confirm

Show every role with its current model and effort. Mark any real slug not in the detected set as needing a choice. Confirm with `ask_user_question` using **Ask the human** above. Ask models first, then effort.

`arena-cross-judge-pool` is an array. Arena picks one value whose family differs from the parent when the file names more than one detected slug. `swarm-workers` is the default for every `/swarm` worker unless a race names a model per arm.

When they pick shipped-default models, write `grok-4.6` in every model key (one-entry arrays). When they pick inherit-parent models everywhere, write inherit-parent. When they pick one detected slug everywhere, write that slug. When they customize, write those choices.

When they pick shipped-default effort, write the `[effort]` table from [`references/defaults.toml`](references/defaults.toml). When they pick inherit-parent effort everywhere, write inherit-parent for every `[effort]` key. When they pick xhigh everywhere or customize, write those `[effort]` values.

### 4. Validate

Every real slug must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen slug is unavailable, ask again with the same allowed options. If they picked shipped-default models but `grok-4.6` is not detected, write inherit-parent for models instead.

Every `[effort]` value must be `inherit-parent`, `auto`, `low`, `medium`, `high`, `xhigh`, or `max`. If not, ask again with the effort options above.

### 5. Write the files

Overwrite `~/.grok/pstack-models.toml` so re-runs stay idempotent.

Pstack-managed role files live at `~/.grok/roles/<role-key>.toml` for the keys in the example. Create `~/.grok/roles/` if needed.

- If `[effort].<key>` is `inherit-parent` or `auto` or missing, **delete** that pstack-managed role file if it exists so a stale overlay cannot pin a different level than the plugin agent.
- If `[effort].<key>` is `low`, `medium`, `high`, `xhigh`, or `max`, write only:

```toml
description = "pstack <role-key> role"
reasoning_effort = "<level>"
```

Do not write `model`, `prompt_file`, `default_capability_mode`, or `default_isolation` into those files. Do not edit `~/.grok/config.toml`. Do not delete role files whose names are not pstack keys.

First run writes the shipped default when they accept it. Copy [`references/defaults.toml`](references/defaults.toml). Replace `grok-4.6` with `inherit-parent` only when `grok-4.6` was not detected this session.

EXAMPLE (shipped default). Same bytes as `references/defaults.toml` when `grok-4.6` is detected:

```toml
# Write only slugs detected this session (task.model rejection, grok inspect, grok models).
# grok-4.6 is the Grok Build shipped default. inherit-parent or auto: omit task.model.
# Missing key in an existing file: same as inherit-parent for models.
# Array keys: one task spawn per entry. Without a toml, skills send grok-4.6 (omit if rejected).
#
# [effort]: inherit-parent or auto or missing key: do not write ~/.grok/roles/<key>.toml.
# low/medium/high/xhigh/max: write ~/.grok/roles/<key>.toml with that reasoning_effort.
# Skills never send reasoning_effort on task. Spawn subagent_type = the role key.
# Plugin agents also ship frontmatter effort so a fresh install needs no setup.

feature = "grok-4.6"
refactoring = "grok-4.6"
bug-fix = "grok-4.6"
perf-issue = "grok-4.6"
hillclimb = "grok-4.6"
judgment-and-prose = "grok-4.6"
hardest-tasks = "grok-4.6"
how-explorer = "grok-4.6"
how-explainer = "grok-4.6"
how-critics = ["grok-4.6"]
why-investigators = "grok-4.6"
why-synthesizer = "grok-4.6"
reflect-tooling = "grok-4.6"
reflect-judgment = "grok-4.6"
arena-runners = ["grok-4.6"]
arena-cross-judge-pool = ["grok-4.6"]
swarm-workers = "grok-4.6"
architect-runners = ["grok-4.6"]
interrogate-reviewers = ["grok-4.6"]
independent-verifier = "grok-4.6"

[effort]
feature = "low"
refactoring = "low"
bug-fix = "high"
perf-issue = "high"
hillclimb = "high"
judgment-and-prose = "xhigh"
hardest-tasks = "xhigh"
how-explorer = "low"
how-explainer = "xhigh"
how-critics = "xhigh"
why-investigators = "low"
why-synthesizer = "xhigh"
reflect-tooling = "high"
reflect-judgment = "xhigh"
arena-runners = "xhigh"
arena-cross-judge-pool = "xhigh"
swarm-workers = "low"
architect-runners = "xhigh"
interrogate-reviewers = "xhigh"
independent-verifier = "xhigh"
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

Do not copy an example table from another product, from older revisions of this skill, or from training memory. The shipped default is `references/defaults.toml`.

Do not offer a menu item that is not in **Ask the human**. Do not mention other products in the TUI. Do not offer to port or mix a mapping from another tool.
