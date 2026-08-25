# Resolve `task.model`

Every pstack skill that spawns `task` uses this rule. Read it once, then apply it at the spawn site.

1. Read `~/.grok/pstack-models.toml` if it exists.
2. Look up the role key named at the spawn site (`feature`, `how-explorer`, `arena-runners`, …).
3. If the file is absent, the key is missing, or the value is `inherit-parent` or `auto`, **omit** `task.model`. The child inherits the parent session model.
4. If the value is a real slug, send `model` only when that slug was confirmed this session: a live `task.model` rejection that names valid slugs, `grok inspect` if it actually lists models, or `grok models`. Never invent a slug. Never copy a slug from an example table, another product's panel, or training memory.
5. Array keys (`how-critics`, `arena-runners`, `arena-cross-judge-pool`, `architect-runners`, `interrogate-reviewers`): one `task` spawn per entry. An entry that is `inherit-parent` or `auto` omits `model` on that spawn. If the file or key is absent, spawn **one** child and omit `model`. Do not expand a missing panel into multiple guessed slugs.
6. Architect without a toml may still spawn **two** children with `model` omitted (same parent model twice) when the skill requires two structurally distinct sketches. That is two prompts, not two invented slugs.
7. If `task` rejects a slug, omit `model` or retry only with a slug the error text named that is already in this session's detected set. Do not pick a "closest family equivalent."

Effort is a separate overlay. Never send `reasoning_effort` on `task`. Spawn `subagent_type` equal to the role key and follow [`resolve-effort.md`](resolve-effort.md).

This plugin is the Grok Build port. It writes `~/.grok/pstack-models.toml` and pstack-managed `~/.grok/roles/*.toml`. It does not ship a fallback slug list.
