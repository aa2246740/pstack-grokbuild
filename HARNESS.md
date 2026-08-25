# Grok Build harness

pstack's 22 playbooks and 21 principles stay. Only harness call sites change.

Sources: official pstack (`cursor/plugins` `pstack/`) and official grok-build (`xai-org/grok-build`). Tool names and fields below are from grok-build source, not from Cursor's `Task` schema and not from third-party ports.

## Verdict

**Yes.** The discipline ports. The Cursor plugin runtime does not.

Install this repo as a Grok Build plugin. Do not keep `.cursor-plugin`, `~/.cursor/rules/*.mdc`, Cursor `Task`, or Cursor Cloud Agents.

The full mapping table and `task` fields live in the local checkout at `/agent/pstack-grokbuild/HARNESS.md` until git credentials can push the complete tree. Canonical spawn tool is `task`. Fields: `prompt`, `description`, `subagent_type`, `run_in_background` (default true), `isolation`, `resume_from`, `cwd`, `model`. Do not send `readonly`, `environment`, `capability_mode`, or `reasoning_effort`.
