# Grok Build harness

pstack's 22 playbooks and 21 principles stay. Only harness call sites change.

Sources: official pstack (`cursor/plugins` `pstack/`) and official grok-build (`xai-org/grok-build`). Tool names and fields below are from grok-build source, not from Cursor's `Task` schema and not from third-party ports.

## Verdict

**Yes.** The discipline ports. The Cursor plugin runtime does not.

Install this repo as a Grok Build plugin. Do not keep `.cursor-plugin`, `~/.cursor/rules/*.mdc`, Cursor `Task`, or Cursor Cloud Agents.

## Mapping: pstack need → grok-build primitive

| pstack need | grok-build primitive | Source |
|---|---|---|
| Slash skill / playbook router | Plugin `skills/` `SKILL.md`. Invoked as `/name`. Frontmatter: `name`, `description`, `disable-model-invocation`, `user-invocable`. | `crates/codegen/xai-grok-pager/docs/user-guide/08-skills.md` |
| Plugin install | `plugin.json` at repo root (also `.grok-plugin/plugin.json`). `grok plugin install <owner>/<repo> --trust`. Components: `skills/`, `agents/`, `commands/`, `hooks/hooks.json`, `.mcp.json`. | `crates/codegen/xai-grok-agent/src/plugins/manifest.rs`; `09-plugins.md` |
| Spawn a child | Model-facing tool **`task`**. Wire aliases `Task` and `spawn_subagent` resolve to the same tool. Canonical id is `task`. | `xai-grok-tools/.../task/mod.rs` `TASK_TOOL_NAME`; `xai-tool-types/src/task.rs` `TaskToolInput` |
| Background child | `task.run_in_background` (`bool`, **default `true`**). Returns `subagent_id`. Retrieve with `get_task_output`. | `TaskToolInput` |
| Wait for child | `get_task_output` with `task_ids: [id, ...]` and `timeout_ms` > 0 to block, omit/`0` to poll. Cap 20 ids. | `TaskOutputToolInput` |
| Cancel child | `kill_task` with `task_id`. | `kill_task` in `xai-tool-types/src/task.rs` |
| Child role | `task.subagent_type`. Built-ins: `general-purpose` (default), `explore`, `plan`. Plugin agents: pstack role keys (`feature`, `how-explainer`, …), plus `poteto-agent`, `comment-sicko`, `independent-verifier`. Send the **bare** role key so `~/.grok/roles/<key>.toml` matches. Qualified `pstack:<key>` is fallback if the bare name is unknown; it does not match the role file stem. | `TaskToolInput`; `16-subagents.md`; `xai-grok-agent/src/discovery.rs`; `select_role` |
| Per-spawn model | `task.model` (optional slug). Omit to inherit parent. Do not pass with `resume_from`. Invalid slugs fail via `TaskModelValidator`. | `TaskToolInput.model` |
| Per-spawn reasoning effort | **Not on the model-facing `task` schema.** `TaskToolInput` has no `reasoning_effort` field. Spawn from `task` sets `SubagentRuntimeOverrides.reasoning_effort` to `None`. `/setup-pstack` writes `SubagentRole.reasoning_effort` in `~/.grok/roles/<pstack-role>.toml`. `select_role(subagent_type)` in `resolve_runtime_config` applies it. Skills spawn `subagent_type` equal to that role key (bare name). Missing role file / `inherit-parent` / `auto` leaves runtime effort unset, so the child inherits the parent. Plugin agents for these roles omit frontmatter `effort` so inherit works. Levels written: `low`, `medium`, `high`, `xhigh`, `max` (`Effort::VALID_VALUES`; `ReasoningEffort` also parses them). | `xai-tool-types/src/task.rs` `TaskToolInput`; `task/mod.rs` spawn (`reasoning_effort: None`); `xai-grok-subagent-resolution/src/definition.rs` `select_role` / `resolve_runtime_config`; `SubagentRole.reasoning_effort` in `xai-grok-subagent-resolution/src/config.rs`; `handle_request.rs` sampling apply; `~/.grok/roles` discovery in `xai-grok-shell/src/config/mod.rs` `SubagentsConfig::resolve_base_with_sources` |
| Read-only child | **Not `task.capability_mode`.** That field is `#[schemars(skip)]` and JSON that sends it is **ignored**. Use built-in `explore` (or `plan`) whose definition already filters tools. | `TaskToolInput.capability_mode`; `apply_child_tool_policy` |
| Worktree isolation | `task.isolation`: `"none"` (default, shared cwd) or `"worktree"`. Mutually exclusive with `task.cwd`. | `SubagentIsolationMode`; `TaskToolInput.isolation` |
| Resume a finished child | `task.resume_from` = prior `subagent_id`. Same `subagent_type`. | `TaskToolInput.resume_from` |
| Nested spawn | **Forbidden by default.** `MAX_SUBAGENT_DEPTH` is `1`. A child that calls `task` fails. The parent session owns every spawn. Playbook "delegate then how/swarm from the child" is rewritten: parent fans out. | `task/mod.rs` `MAX_SUBAGENT_DEPTH` |
| Todo list | `todo_write` with `merge` (default true) and `todos: [{id, content?, status?}]`. Status: `pending`, `in_progress`, `completed`, `cancelled`. | `xai-grok-tools/.../todo/mod.rs` |
| Ask the human (product/preference only) | `ask_user_question` with `questions: [{question, options: [{label, description, preview?}], multi_select?}]`. Not Cursor `AskQuestion`. | `ask_user_question/mod.rs` tool id `ask_user_question`; `AskUserQuestionInput` |
| Recurring overnight loop | Slash `/loop` expands to **`scheduler_create`**. Fields: `interval` (`5m`/`2h`/`1d`, min 60s), `prompt`, `durable?`, `foreground?`, `fire_immediately` (default false; `/loop` instruction sets true). Update in place with `task_id`. Cancel with `scheduler_delete` `{id}`. One-shot delayed work is `sleep && cmd` in a background shell, not the scheduler. | `xai-grok-tools-api/src/slash_commands.rs`; `scheduler/create.rs`; `scheduler/delete.rs` |
| Watch a process / PR | `monitor` with `command`, `description`, `timeout_ms?` (default 10h), `persistent?`. Kill with `kill_task`. Do not poll. | `monitor/tool.rs`; `monitor/types.rs` `MonitorInput` |
| Model per pstack role | `~/.grok/pstack-models.toml`, written by `/setup-pstack`. Skills read it. Absent file, missing key, `inherit-parent`, or `auto`: omit `task.model`. Never write Cursor rules files. Optional extra: `[subagents.models]` in `~/.grok/config.toml` only maps **agent types** (`explore`, `plan`), not pstack roles. | `setup-pstack/SKILL.md`; grok-build `[subagents.models]` in `16-subagents.md` |
| Effort per pstack role | Same skill writes `[effort]` in that toml and, for a real level, `~/.grok/roles/<key>.toml` (`description` + `reasoning_effort` only). Skills spawn the role key and do not send `task.reasoning_effort`. | `setup-pstack/SKILL.md`; `resolve-effort.md` |
| Independent verify | Parent calls `task` with `subagent_type: "independent-verifier"` (bare name so the role overlay matches). Send a **different** `model` when toml `independent-verifier` is a detected slug ≠ the writer; otherwise omit `model`. Effort comes from `~/.grok/roles/independent-verifier.toml` when setup wrote a level; otherwise inherit parent. `isolation: "worktree"` when the child must not touch the writer's tree. The verifier does not write the diff. Not a Cursor Cloud Agent. | this file; `agents/independent-verifier.md`; `resolve-effort.md` |
| Cursor Cloud `environment: "cloud"` | Dropped. Use `isolation: "worktree"` plus `run_in_background: true`. | `TaskToolInput.isolation` |
| Graphite `gt` / `graphite-base` | Optional if `gt` is on PATH. Otherwise `gh` + git. Playbook steps stay; the CLI is not assumed. | playbooks, rewritten call sites |
| `cursor-team-kit` (`deslop`, `control-ui`, `control-cli`) | Not in this plugin. `/unslop` and `/no-comments` remain. Drive the real app yourself (browser, CLI, tests). | pstack README "not shipped here" |
| Benny automations | Cursor automation pack. Grok equivalent is plugin `hooks/` + workflows. Not registered as slash skills. Left under `automations/benny/` as source, not a Grok automation runtime. | pstack `automations/benny/`; grok `hooks/hooks.json` |

## Docs vs source

Grok Build's user guide `16-subagents.md` still names `spawn_subagent`, a `background` field defaulting to `false`, and `get_command_or_subagent_output`. The Rust types this port follows are different:

- Canonical tool id is `task` (`TASK_TOOL_NAME`). Wire aliases `Task` and `spawn_subagent` resolve to the same tool.
- Background field is `run_in_background`, default **true**.
- Join with `get_task_output` (`task_ids`, optional `timeout_ms`). `wait_tasks` exists as compatibility; prefer `get_task_output`.
- `scheduler_create.recurring` is `#[schemars(skip)]`. Sending `recurring: false` is rejected; one-shot delay is background `sleep && cmd`.

Copy fields from `TaskToolInput` / `SchedulerCreateInput`, not from that user-guide table.

## `task` fields the model may send

From `TaskToolInput` in `crates/common/xai-tool-types/src/task.rs`:

- `prompt` (string, required)
- `description` (string, required, 3–5 words)
- `subagent_type` (string, default `general-purpose`)
- `run_in_background` (bool, default **true**)
- `isolation` (`none` \| `worktree`, optional)
- `resume_from` (string, optional)
- `cwd` (string, optional; not with `isolation: worktree`)
- `model` (string, optional)

Do not send `readonly`, `environment`, `capability_mode`, or `reasoning_effort` on `task`. They are not model-facing fields. `capability_mode` on the struct is skipped in JSON and ignored if present. Per-role effort is `SubagentRole.reasoning_effort` on a role whose name equals `subagent_type`, written as `~/.grok/roles/<key>.toml`.

## Default spawn shape

Parent session only:

```text
task
  prompt: <full brief, file pointers not inlined dumps>
  description: <3-5 words>
  subagent_type: <pstack role key, e.g. feature | how-explainer | independent-verifier> | poteto-agent | comment-sicko
  run_in_background: true
  model: <slug from ~/.grok/pstack-models.toml when that key is a detected slug; omit if the file/key is absent or inherit-parent/auto>
  isolation: none | worktree
```

Do not send `reasoning_effort` on that call. Effort is the matching `~/.grok/roles/<subagent_type>.toml` when setup wrote a level.

Then `get_task_output` with `task_ids` and a positive `timeout_ms` when the parent must join.

Code-writing delegates: the playbook role key (`feature`, `bug-fix`, …). Ad-hoc helpers with no role key: `poteto-agent`.
Read-only codebase walks: `how-explorer` / `how-explainer` / `how-critics` (not the built-in `explore`, so role effort can apply).
MCP-backed `why` investigators: `why-investigators` / `why-synthesizer`. Instruct no writes in the prompt. Posture, not a sandbox.
`/no-comments`: `comment-sicko`.
Independent verify: `independent-verifier` plus toml `independent-verifier` when that key is a detected slug different from the writer; otherwise omit `model`. Effort from `~/.grok/roles/independent-verifier.toml` when present.
