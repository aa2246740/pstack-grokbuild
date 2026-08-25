# Effort ladder

Do not handwrite a frozen `medium` / `high` / `xhigh` table. Compute three tiers from the live grok-build effort enum, weakest → strongest.

`scripts/effort_ladder.py` is the same algorithm. Keep the role lists here and there identical.

## Detect the live enum

`/setup-pstack` detects. Spawn skills do not. `TaskToolInput` has no `reasoning_effort` field, so a later `ultra` cannot be applied on spawn without a setup overlay. Document that miss; do not fake a `task` probe.

Try, in this order, until you have an ordered list:

1. Rejected invalid `--reasoning-effort` / `--effort`. Prefer the `expected one of:` list from `ReasoningEffort::from_str` (`crates/codegen/xai-grok-sampling-types/src/types.rs`). That order is official. Clap stores the flag as a free string, so help may not enumerate values; the FromStr error does.
2. `grok --help` / `grok -h`. Take the `--reasoning-effort` / `--effort` parenthetical canonical list **before** any `also` / per-model menu-id clause.
3. Official grok-build `Effort::VALID_VALUES` only if this session can actually read that source. Do not quote a memorized list as live proof.

Drop `none` and `minimal`. They may parse on the CLI but they are not `AgentDefinition::Effort` values. Drop per-model menu ids such as `deep`. This plugin does not ship those or offer them.

Do not add a token the detection text did not name. Do not invent `ultra`.

Do not use the TUI slash menu as the enum. `EFFORT_LEVELS` is strongest-first and omits `max`. `SELECTABLE_REASONING_EFFORTS` is `minimal` through `xhigh` and also omits `max`. Those are menus, not `AgentDefinition::Effort`.

If every probe fails (no `grok` CLI, no rejection text), use the **ship-time snapshot** below and say so in the step 6 confirmation, not in the TUI.

Sort weakest → strongest using that detection source's printed order. At grok-build pin `c2ad97f87aea4303b6000a2c22128bc91ee76c9b` (`crates/codegen/xai-grok-agent/src/config.rs`) `Effort::VALID_VALUES` is `low`, `medium`, `high`, `xhigh`, `max`. CLI help / FromStr list the same tokens after dropping `none` / `minimal`. A new token stays where help or the rejection listed it.

## Three-tier map

Let the detected AgentDefinition levels be `L[0]` weakest … `L[n-1]` strongest.

- **Judgment** (highest): `L[n-1]`
- **Instruction-following** (highest − 1): `L[n-2]` if `n ≥ 2`, else `L[0]`
- **Mechanical** (highest − 2): `L[n-3]` if `n ≥ 3`, else the weakest (`L[0]`) when only one or two levels exist

Floor (Cola rejected shipped mechanical on `low` when a stronger rung exists): if `n ≥ 3` and highest − 2 would be `L[0]`, use `L[1]` (second-weakest) for mechanical instead. Never put shipped mechanical on the absolute floor unless only two levels exist.

### Role lists

**Mechanical.** `feature`, `refactoring`, `how-explorer`, `why-investigators`, `swarm-workers`

**Instruction-following.** `bug-fix`, `perf-issue`, `hillclimb`, `reflect-tooling`

**Judgment / explainer / verifier / panels.** `judgment-and-prose`, `hardest-tasks`, `how-explainer`, `why-synthesizer`, `reflect-judgment`, `independent-verifier`, `how-critics`, `arena-runners`, `arena-cross-judge-pool`, `architect-runners`, `interrogate-reviewers`

### Examples

Check these against `scripts/effort_ladder.py --check`.

| Detected enum (weakest → strongest) | Judgment | Instruction | Mechanical |
|---|---|---|---|
| `low` `medium` `high` `xhigh` `max` | `max` | `xhigh` | `high` |
| same plus `ultra` above `max` | `ultra` | `max` | `xhigh` |
| `low` `medium` `high` only | `high` | `medium` | `medium` (not `low`) |
| `low` `high` only | `high` | `low` | `low` |

## Ship-time snapshot

Plugin agent frontmatter and [`defaults.toml`](defaults.toml) `[effort]` use the snapshot enum `low` `medium` `high` `xhigh` `max`, so out of the box (no setup) the split is judgment `max`, instruction `xhigh`, mechanical `high`.

That snapshot is what this plugin can bake. It is not a claim that the live binary will never grow. `/setup-pstack` re-detects and writes `~/.grok/roles/<key>.toml` for the live split. A later `ultra` is picked that way, without a plugin rewrite, if detection works.

## Apply

Never send `reasoning_effort` on `task`. Write overlays as in [`resolve-effort.md`](resolve-effort.md).
