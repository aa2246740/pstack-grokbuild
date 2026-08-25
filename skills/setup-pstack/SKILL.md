---
name: setup-pstack
description: Configure which models pstack uses per role. Detects your available models and writes ~/.grok/pstack-models.toml. Use for /setup-pstack, "configure pstack models", or changing pstack's model choices.
---

# Setup pstack

Write `~/.grok/pstack-models.toml`. Skills read it and fall back to their inline defaults when a key is absent. This is an override layer, not a grok-build `[subagents.models]` table. That table maps agent types (`explore`, `plan`), not pstack roles.

## Steps

### 1. Detect available models

Enumerate slugs the `task` tool accepts in `model` this session. Prefer `grok inspect --json` if it lists models. A rejected `task.model` error that names valid slugs is also evidence. Never write a slug you have not confirmed. `inherit-parent` and `auto` are always valid and are not slugs: omit `model` on `task` so the child inherits the parent.

### 2. Load current state

If `~/.grok/pstack-models.toml` exists, read it. Otherwise start from the defaults in step 5.

### 3. Map and confirm

Show every role with its current model. Mark any real slug not in the detected set as needing a choice. Confirm with `ask_user_question` (`questions[].question`, `questions[].options[].label` + `description`). Panel roles are arrays. One `task` spawn per entry. `arena_cross_judge_pool` is also an array. Arena picks one value whose model family differs from the parent when possible. `swarm_workers` is the default for every `/swarm` worker unless a race names a model per arm.

### 4. Validate

Every real slug must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen slug is unavailable, ask again. A file pointing at a model the user cannot use breaks every delegation that reads it.

### 5. Write the file

Overwrite the whole file so re-runs stay idempotent:

```toml
# pstack model configuration. Delete a key to fall back to the skill default.
# inherit-parent or auto: omit task.model so the child inherits the parent.
# Array keys: one task spawn per entry.

feature = "grok-4.6-fast-xhigh"
refactoring = "grok-4.6-fast-xhigh"
bug-fix = "gpt-5.6-sol-max"
perf-issue = "gpt-5.6-sol-max"
hillclimb = "gpt-5.6-sol-max"
judgment-and-prose = "claude-fable-5-thinking-max"
hardest-tasks = "claude-fable-5-thinking-max"
how-explorer = "grok-4.6-fast-xhigh"
how-explainer = "claude-fable-5-thinking-max"
how-critics = ["claude-fable-5-thinking-max", "gpt-5.6-sol-max", "grok-4.6-fast-xhigh", "claude-opus-5-thinking-xhigh"]
why-investigators = "grok-4.6-fast-xhigh"
why-synthesizer = "claude-fable-5-thinking-max"
reflect-tooling = "gpt-5.6-sol-max"
reflect-judgment = "claude-fable-5-thinking-max"
arena-runners = ["claude-fable-5-thinking-max", "gpt-5.6-sol-max", "grok-4.6-fast-xhigh", "claude-opus-5-thinking-xhigh"]
arena-cross-judge-pool = ["claude-fable-5-thinking-max", "gpt-5.6-sol-max", "grok-4.6-fast-xhigh", "claude-opus-5-thinking-xhigh"]
swarm-workers = "grok-4.6-fast-xhigh"
architect-runners = ["claude-fable-5-thinking-max", "gpt-5.6-sol-max", "grok-4.6-fast-xhigh", "claude-opus-5-thinking-xhigh"]
interrogate-reviewers = ["claude-fable-5-thinking-max", "gpt-5.6-sol-max", "grok-4.6-fast-xhigh", "claude-opus-5-thinking-xhigh"]
independent-verifier = "claude-fable-5-thinking-max"
```

### 6. Confirm

Tell the user the file was written. New sessions pick it up. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Look for a `verify-*` skill under `.grok/skills/` or an existing harness. If neither exists, offer once via `ask_user_question` to generate one with `/create-verification-skill`. On yes, write `.grok/skills/verify-<app>/`. On no, move on.
