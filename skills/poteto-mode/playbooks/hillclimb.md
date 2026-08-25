# Hillclimb Playbook

When to use: the metric is known, the direction is known, and the work is iterative improvement rather than a one-shot rewrite. Latency, conversion, cost, error rate, bundle size, query time.

This playbook is a loop. Stop when the metric moves enough, time runs out, or the next change is larger than the remaining budget.

## 1. Baseline

Measure the current value. Write it down with the method (which endpoint, which query, which build). Without a number, hillclimb is just tinkering.

If `pstack-models.toml` exists, spawn that measurement child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 2. Hypothesize

List the plausible levers, ranked by expected impact over effort. One page. Do not implement yet.

If `pstack-models.toml` exists, spawn that hypothesis child with `task.model` set to `[models.plan]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 3. Change one thing

Implement the top remaining lever. Keep the change small enough to attribute. If two things move, you do not know which one worked.

If `pstack-models.toml` exists, spawn that implementation child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 4. Measure again

Same method as baseline. Record the new number and the delta. If it got worse, revert and try the next lever. If it got better, keep it and continue.

If `pstack-models.toml` exists, spawn that measurement child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 5. Stop or continue

Compare remaining budget to remaining levers. If the next change is a rewrite, switch to the feature or refactoring playbook. If the metric is good enough, stop and write what you learned (what moved the number, what did not).
