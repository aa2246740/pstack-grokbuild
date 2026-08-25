# Feature Playbook

When to use: adding new functionality, not debugging or refactoring existing code.

## 1. Scope and spec

Read the request. Identify the user-visible change, the files/modules that will own it, and the acceptance criteria. If the request is vague, spawn a child to draft a one-page spec before writing code.

If `pstack-models.toml` exists, spawn that spec child with `task.model` set to `[models.plan]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 2. Design before code

For anything beyond a few lines, spawn a child to propose the design: types, module boundaries, error paths, and what will not change. Parent reviews. Then implement.

If `pstack-models.toml` exists, spawn that design child with `task.model` set to `[models.plan]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 3. Implement

Write the feature in the existing architecture. Match neighboring code. Do not invent a parallel pattern. Leave the codebase better than you found it for the next person who touches this area.

If `pstack-models.toml` exists, spawn implementation children with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 4. Verify

Run tests and the typechecker. Add tests for the new behavior. If the feature has a UI, use a browser or the platform's equivalent and click through it — a green unit test is not the same as a working feature.

If `pstack-models.toml` exists, spawn that verification child with `task.model` set to `[models.fast]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.

## 5. Review

Before handing back, spawn a child to read the diff as a reviewer: bugs, missing tests, scope creep, accessibility, and security. Fix what it finds.

If `pstack-models.toml` exists, spawn that review child with `task.model` set to `[models.review]`. If the toml is missing, a key is missing, or the value is `inherit-parent` or `auto`, omit `task.model` so the child uses the host default. Do not use Cursor Auto, Composer 1.5, or GPT-5.2 Codex as fallbacks.
