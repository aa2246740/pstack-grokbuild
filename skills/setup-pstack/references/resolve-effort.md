# Resolve reasoning effort

Every pstack skill that spawns `task` uses this rule together with [`resolve-model.md`](resolve-model.md). Read it once, then apply it at the spawn site.

Grok Build's model-facing `task` tool does **not** accept `reasoning_effort`. `TaskToolInput` at grok-build pin `c2ad97f87aea4303b6000a2c22128bc91ee76c9b` (`crates/common/xai-tool-types/src/task.rs`) has `prompt`, `description`, `subagent_type`, `run_in_background`, `isolation`, `resume_from`, `cwd`, `model`. Spawn from `task` sets `SubagentRuntimeOverrides.reasoning_effort` to `None` (`crates/codegen/xai-grok-tools/src/implementations/grok_build/task/mod.rs`).

The runtime that actually sets child sampling effort is `resolve_runtime_config` in `crates/codegen/xai-grok-subagent-resolution/src/definition.rs`:

1. `select_role(subagent_type)` looks up `[subagents.roles.<subagent_type>]` / `~/.grok/roles/<subagent_type>.toml` (`SubagentRole.reasoning_effort`).
2. Then persona (not a `task` field; model-facing spawn sets `persona: None`).
3. Then `AgentDefinition.effort` frontmatter, only if still unset.
4. Then inherit the parent session. `handle_request.rs` writes `effective_sampling_config.reasoning_effort` only when that resolved string parses as `ReasoningEffort`.

Do not send `reasoning_effort` on `task`. Do not put `effort:` on plugin agent frontmatter for these roles: a baked frontmatter value would block inherit-parent.

## Spawn type

Set `subagent_type` to the **pstack role key** for that spawn (`feature`, `how-explainer`, `independent-verifier`, …). Send the **bare** name so it matches `~/.grok/roles/<key>.toml`. Do not send `pstack:<key>` unless the bare name is rejected as unknown; a qualified name does not match the role file stem.

This plugin ships an agent file per role key under `agents/`. `poteto-agent` remains for ad-hoc helpers that have no role key. `/no-comments` stays `comment-sicko`.

If the role agent is unknown this session, fall back to `poteto-agent` (writers), `explore` (read-only), or `general-purpose` (MCP / swarm). That fallback **drops** per-role effort. Prefer the role key.

## Effort values

1. Read `~/.grok/pstack-models.toml` if it exists. Look up `[effort].<role-key>`. Array model keys still have **one** scalar effort.
2. If the file is absent, `[effort]` is absent, the key is missing, or the value is `inherit-parent` or `auto`, do **not** expect a role overlay. Omit any `task` effort field (there isn't one). The child inherits the parent session effort.
3. If the value is `low`, `medium`, `high`, `xhigh`, or `max`, `/setup-pstack` has written `~/.grok/roles/<role-key>.toml` with `reasoning_effort` set to that string. Spawn the matching `subagent_type`. Do not copy the string onto `task`.
4. Never invent a level. Never send `none` or `minimal` from this plugin. Those parse on the CLI but are not `AgentDefinition::Effort::VALID_VALUES` (`low`, `medium`, `high`, `xhigh`, `max`).

This plugin is the Grok Build port. Effort lives in grok-build `SubagentRole.reasoning_effort`, not in a Cursor panel and not on `task`.
