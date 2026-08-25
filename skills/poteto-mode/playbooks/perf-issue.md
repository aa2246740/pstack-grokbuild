# Perf-Issue Playbook

When to use: something is too slow, too expensive, or too large, and the cause is not yet known. Distinct from hillclimb: here you do not yet know the lever.

## 1. Reproduce and measure

Get a number. Latency, allocations, query time, bundle bytes, or whatever the complaint is. A repro without a number is a feeling.

If `pstack-models.toml` exists, spawn that measurement child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 2. Profile

Use the language's profiler, a query planner, a bundle analyzer, or logging around suspect regions. Do not guess the hot path from reading code first — measure, then read the hot path.

If `pstack-models.toml` exists, spawn that profiling child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 3. Explain the cost

Write down why it is expensive: N+1, unbounded work, sync-over-async, huge payload, missing index, algorithm, or layout thrash. The explanation is the deliverable of this step, not a patch.

If `pstack-models.toml` exists, spawn that explanation child with `task.model` set to `[models.plan]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 4. Fix the actual cause

Change the hot path. Do not sprinkle caches on a wrong algorithm. Add a regression test or a benchmark that would have caught this.

If `pstack-models.toml` exists, spawn that fix child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 5. Re-measure

Same method as step 1. Confirm the number moved. If it did not, the diagnosis was wrong — go back to profile, do not add another guess-fix.
