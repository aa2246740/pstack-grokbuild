---
name: setup-pstack
description: Configure which models pstack uses per role. Detects your available models and writes ~/.grok/pstack-models.toml. Use for /setup-pstack, "configure pstack models", or changing pstack's model choices.
---

# Setup pstack

This plugin is the **Grok Build port**. Write **only** `~/.grok/pstack-models.toml`. Never create `~/.cursor/rules/pstack-models.mdc` or any file under a Cursor rules directory.

Skills read that toml. Missing file, missing key, `inherit-parent`, or `auto` means omit `task.model` so the child inherits the parent. There is no inline Cursor slug fallback. This file is an override layer, not a grok-build `[subagents.models]` table. That table maps agent types (`explore`, `plan`), not pstack roles.

Spawn-site resolution is in [`references/resolve-model.md`](references/resolve-model.md).

## Host

Proceed only on Grok Build: live `task` tool (grok-build fields such as `run_in_background` and `isolation`), and/or `grok` CLI (`grok inspect`, `grok models`).

If this session is Cursor, Grok Bot running the official Cursor pstack plugin, or any host that would write Cursor rules paths, **stop**. Do not write Cursor paths. Tell the user this plugin is the Grok Build port. Official Cursor `/setup-pstack` is a different plugin and still writes `~/.cursor/rules`.

## Steps

### 1. Detect available models

Enumerate slugs the `task` tool accepts in `model` this session.

- Probe with an invalid `task.model` and read the rejection text for valid slugs.
- Run `grok models` if the CLI exposes it.
- Use `grok inspect --json` only if that JSON actually lists models. `InspectReport` often has no models field. Do not invent a catalog from inspect keys.

Never write a slug you have not confirmed this session. Do not copy an example table from Cursor pstack, from this skill's older revisions, or from training memory. `inherit-parent` and `auto` are always valid and are not slugs: omit `model` on `task` so the child inherits the parent.

### 2. Load current state

If `~/.grok/pstack-models.toml` exists, read it. Otherwise start from `inherit-parent` for every role (the example in step 5).

### 3. Map and confirm

Show every role with its current value. Mark any real slug not in the detected set as needing a choice. Confirm with `ask_user_question` (`questions[].question`, `questions[].options[].label` + `description`). Include `inherit-parent` as an option on every role. Without a toml, the panel is one `inherit-parent` entry, not a multi-model Cursor panel.

Panel roles are arrays. One `task` spawn per entry. `arena-cross-judge-pool` is also an array. Arena picks one value whose model family differs from the parent when possible. `swarm-workers` is the default for every `/swarm` worker unless a race names a model per arm.

When the user accepts defaults, write the step 5 example (`inherit-parent` everywhere), or substitute only slugs from this session's detected set.

### 4. Validate

Every real slug must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen slug is unavailable, ask again. A file pointing at a model the user cannot use breaks every delegation that reads it.

### 5. Write the file

Overwrite the whole file so re-runs stay idempotent. Write only to `~/.grok/pstack-models.toml`.

EXAMPLE (accept-defaults). Every role `inherit-parent`. Replace a value with a real slug only when that slug was detected this session:

```toml
# Write only slugs detected this session (task.model rejection, grok inspect, grok models).
# inherit-parent or auto: omit task.model; child inherits the parent.
# Missing key: same as inherit-parent. Do not invent slugs.
# Array keys: one task spawn per entry. Without a toml, skills spawn one child and omit model.

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
```

### 6. Confirm

Tell the user the file was written. New sessions pick it up. Re-running this skill updates it. Confirm `~/.cursor/rules/pstack-models.mdc` was not created.

### 7. Offer a verification skill (optional)

Look for a `verify-*` skill under `.grok/skills/` or an existing harness. If neither exists, offer once via `ask_user_question` to generate one with `/create-verification-skill`. On yes, write `.grok/skills/verify-<app>/`. On no, move on.
