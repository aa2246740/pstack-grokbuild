# Refactoring Playbook

When to use: the behavior must stay the same, the structure must change. If behavior is supposed to change, use the feature or bug-fix playbook instead.

## 1. Characterize current behavior

Read the tests, the types, and the call sites. Write down what must not change: inputs, outputs, error cases, timing assumptions, public API. If tests are thin, add characterization tests before touching production code.

If `pstack-models.toml` exists, spawn that characterization child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 2. Name the structural change

One paragraph: what moves where, and why the current shape is in the way. If you cannot name it, you are not ready to refactor.

If `pstack-models.toml` exists, spawn that design child with `task.model` set to `[models.plan]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 3. Refactor behind tests

Change structure in small steps. Run tests after each step. Do not mix behavior changes into the refactor. If a behavior change is required to make the structure work, stop and treat it as a feature with an explicit spec.

If `pstack-models.toml` exists, spawn that implementation child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 4. Verify equivalence

Run the full relevant test suite and typecheck. If the refactor touches a public API, grep for remaining call sites of the old shape.

If `pstack-models.toml` exists, spawn that verification child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 5. Review the blast radius

Spawn a child to read the diff specifically for accidental behavior change, missed call sites, and tests that were deleted or weakened to make the refactor pass.

If `pstack-models.toml` exists, spawn that review child with `task.model` set to `[models.review]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.
