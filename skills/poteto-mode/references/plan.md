# Plan Mode

Enter this when the task is large, ambiguous, or has significant architectural trade-offs. Stay here until the parent is ready to implement.

## What you produce

A plan the parent can execute: scope, approach, files, sequencing, risks, and what will not change. Not a design doc for its own sake.

## Steps

1. Read the request and the relevant code. If ownership or layering is unclear, follow `skills/how`.
2. List the decision points. For each, name the options and the constraint that picks one.
3. Write the plan as a numbered sequence of implementation steps, each small enough to verify.
4. Call out tests, migration, and rollback where they apply.
5. Hand the plan to the parent. Do not start implementing unless the parent explicitly switches you to agent mode.

## Model

If `pstack-models.toml` exists, spawn planning children with `task.model` set to `[models.plan]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.
