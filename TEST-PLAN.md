# TEST-PLAN.md

Operator plan for **EDITH** on a real Linux Grok Build CLI.

This file is the test. A Python script is not. A Cloud Agent transcript is not.

## Spec, not folklore

First principles only. Do not treat community pstack ports as the spec.

| Source | Pin | Role |
|---|---|---|
| Official pstack | [cursor/plugins `pstack/`](https://github.com/cursor/plugins/tree/main/pstack) tree `46125561306434d8a1d7745d540d8932ab0cd2a2` | 22 named playbooks, `opening-a-pr.md`, 21 `principle-*` skills, `/poteto-mode` router |
| Official grok-build | [xai-org/grok-build](https://github.com/xai-org/grok-build) commit `c2ad97f87aea4303b6000a2c22128bc91ee76c9b` | Plugin install, inspect JSON, headless flags, live tool ids |
| This port | [HARNESS.md](./HARNESS.md) | Call-site mapping onto those grok-build tools |

User-guide `16-subagents.md` still names `spawn_subagent`, a `background` field defaulting to `false`, and `get_command_or_subagent_output`. **Follow the Rust types, not that table.** Canonical spawn tool is `task` (`TASK_TOOL_NAME`). Wire aliases `Task` and `spawn_subagent` resolve to the same tool. Background field is `run_in_background`, default **true**. Join with `get_task_output` (`task_ids`, optional `timeout_ms`). See `crates/common/xai-tool-types/src/task.rs` `TaskToolInput`.

Plugin name in `plugin.json` is `pstack` (kebab-case, required by `PluginManifest::validate`).

## What this Cloud Agent VM cannot prove

The machine that wrote this plan (`cursor.com/agents/bc-01a0363c-5279-7a80-8c72-07f646d3adf3`) had **no live `grok` CLI and no live `task` tool**. It cannot prove:

- `grok plugin install` / `enable` / `inspect`
- skills appearing in a real session (`init.skills`, slash menu)
- `/setup-pstack` writing only slugs that `task.model` accepts
- `/poteto-mode` copying playbook steps into `todo_write` / `plan`
- a parent `task` spawn of `independent-verifier` on a different `model`
- `/loop` → `scheduler_create`
- `--always-approve` and `--reasoning-effort xhigh` on a real binary

`scripts/verify-harness.py` is a static repo check. **It is not a pass gate.** Do not attach its output as proof. Cola will not accept it. EDITH will not accept it.

## Verdict vocabulary

Every gate is exactly one of:

- **PASS.** The PASS sentence below is true, and the listed evidence files exist.
- **FAIL.** The FAIL sentence below is true, or a required artifact is missing.
- **SKIP.** The gate is out of budget or the primitive is absent. **SKIP is not PASS.**
- **CANNOT-PROVE.** The box lacks a required capability (example: only one `task.model` slug). **CANNOT-PROVE is not PASS.**

Stop on Gate 0 FAIL. Later gates are meaningless without a working CLI.

## Box EDITH is on

Assume:

- Linux
- `grok` on PATH, model `grok-4.6`
- `--always-approve` exists (alias of `--yolo`, same as `--permission-mode bypassPermissions`; grok-build `cli.rs` and `14-headless-mode.md`)
- `--reasoning-effort xhigh` exists (`14-headless-mode.md` canonical levels include `xhigh`)

If a flag is missing, Gate 0 is FAIL. Record `grok --help` and stop.

## Evidence directory

```bash
export EVIDENCE="${HOME}/pstack-edith-evidence/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$EVIDENCE"
echo "$EVIDENCE"
date -u --iso-8601=seconds | tee "$EVIDENCE/started.txt"
grok --version 2>&1 | tee "$EVIDENCE/grok-version.txt"
command -v grok | tee "$EVIDENCE/grok-which.txt"
```

Keep every file this plan names under `$EVIDENCE`. Do not discard streams because they are large. Compress after the run if needed (`gzip -k`).

Shared headless flags (every `grok -p` unless a gate says otherwise). Use bash. Arrays do not export; paste this in the same shell.

```bash
export GROK_MODEL=grok-4.6
GROK_BASE=(-m "$GROK_MODEL" --always-approve --reasoning-effort xhigh)
# streaming-json: NDJSON, one type-tagged object per line (14-headless-mode.md).
# tool_call.toolName is the live tool id. plan.entries is the todo-shaped plan.
GROK_STREAM=(--output-format streaming-json)
GROK_INIT=(--output-format streaming-messages-json)
```

`--max-turns` is per gate. Too small is a false FAIL. Do not reuse a session across gates unless a gate says `-c` / `--resume`.

Slash skills in headless. Put the slash name in the `-p` string (example `/poteto-mode …`). `poteto-mode` has `disable-model-invocation: true`. The model will not auto-enter it. You must invoke it.

`ask_user_question` is interactive. Prefer the TUI for Gate 4. If a headless run blocks on it, kill it, mark that attempt CANNOT-PROVE, and redo Gate 4 in the TUI.

## Trust vs enable (read before Gate 1)

From grok-build `plugin_cmd.rs` at pin `c2ad97f`:

- `grok plugin install <source>` **without** `--trust` prints a trust prompt to stderr and **`exit(1)`**. It does **not** wait for a TUI y/n. The prompt says to re-run with `--trust`.
- `grok plugin install <source> --trust` installs. No confirmation step in this source.
- Plugins stay off until enabled (`09-plugins.md`). Run `grok plugin enable pstack`. `cmd_enable` is non-interactive. It writes `[plugins].enabled` and prints `Enabled plugin: pstack`.
- `grok inspect --json` field `plugins[].enabled` is **`p.trusted`**, not the enabled list. User plugins under `~/.grok/plugins/` are auto-trusted. Skills loading is the enable check, not that boolean.

If EDITH's binary waits on a TUI confirm even with `--trust`, record the exact prompt and keypress. That is a CLI delta vs `c2ad97f`, not a plugin bug.

---

## Gate 0. Preflight

**Commands**

```bash
grok --version 2>&1 | tee "$EVIDENCE/gate0-version.txt"
grok --help 2>&1 | tee "$EVIDENCE/gate0-help.txt"
grep -E 'always-approve|reasoning-effort|output-format' "$EVIDENCE/gate0-help.txt" \
  | tee "$EVIDENCE/gate0-help-flags.txt"

grok -p "Reply with exactly the word pong and stop. Do not call tools." \
  -m "$GROK_MODEL" \
  --always-approve \
  --reasoning-effort xhigh \
  --max-turns 1 \
  --output-format json \
  2>"$EVIDENCE/gate0-ping.err" | tee "$EVIDENCE/gate0-ping.json"
```

**Inspect**

- `$EVIDENCE/gate0-version.txt` is non-empty.
- `$EVIDENCE/gate0-help-flags.txt` contains `always-approve` and `reasoning-effort`.
- `$EVIDENCE/gate0-ping.json` is a JSON object with `text` and `sessionId` (`14-headless-mode.md` `json` format). `stopReason` may be `end_turn` or `max_turns` / `max_turn_requests`. The text contains `pong` (case-insensitive). Exit code 0.

**PASS.** `grok` runs as `grok-4.6` with `--always-approve` and `--reasoning-effort xhigh`, and the ping JSON contains `pong`.

**FAIL.** The binary is missing, a flag is rejected, or the ping does not return JSON containing `pong`.

**Evidence to keep.** The three `gate0-*` files plus stderr.

---

## Gate 1. Install (`grok plugin install`) then enable

**Commands**

Record that omit-`--trust` exits 1 (source contract):

```bash
set +e
grok plugin install aa2246740/pstack-grokbuild \
  >"$EVIDENCE/gate1-install-no-trust.out" \
  2>"$EVIDENCE/gate1-install-no-trust.err"
echo $? | tee "$EVIDENCE/gate1-install-no-trust.exit"
set -e
# Source at c2ad97f prints: To proceed, re-run with --trust:
grep -i trust "$EVIDENCE/gate1-install-no-trust.err" | tee "$EVIDENCE/gate1-install-no-trust-grep.txt"
```

Install with trust (GitHub shorthand). Pin a commit if this box has `GROK_MARKETPLACE_REQUIRE_SHA=1`:

```bash
# Preferred. Public repo.
grok plugin install aa2246740/pstack-grokbuild --trust \
  2>&1 | tee "$EVIDENCE/gate1-install-trust.txt"

# Fallback if git/GitHub is blocked. Clone or copy the plugin tree first.
# grok plugin install /absolute/path/to/pstack-grokbuild --trust
```

Enable (separate from trust):

```bash
grok plugin enable pstack 2>&1 | tee "$EVIDENCE/gate1-enable.txt"
# Expected line: Enabled plugin: pstack
```

Inventory:

```bash
grok plugin list --json 2>&1 | tee "$EVIDENCE/gate1-plugin-list.json"
grok plugin details pstack 2>&1 | tee "$EVIDENCE/gate1-plugin-details.txt"
grok inspect --json 2>&1 | tee "$EVIDENCE/gate1-inspect.json"
```

Extract the installed path and counts:

```bash
jq '.[] | select(.name=="pstack" or .name=="pstack-grokbuild")' \
  "$EVIDENCE/gate1-plugin-list.json" \
  | tee "$EVIDENCE/gate1-plugin-list-pstack.json"

jq '.plugins[] | select(.name=="pstack")' \
  "$EVIDENCE/gate1-inspect.json" \
  | tee "$EVIDENCE/gate1-inspect-plugin.json"

jq -r '.plugins[] | select(.name=="pstack") | .path' \
  "$EVIDENCE/gate1-inspect.json" \
  | tee "$EVIDENCE/PLUGIN_PATH.txt"
export PLUGIN_PATH="$(cat "$EVIDENCE/PLUGIN_PATH.txt")"
```

**Inspect**

- No-trust run. Exit code 1. Stderr contains `re-run with --trust`. Process did not wait for a keypress (unless EDITH's CLI differs; then record it).
- Trust run. Stdout names the installed plugin (`Installed … pstack` or equivalent). Exit 0.
- `gate1-enable.txt` contains `Enabled plugin: pstack`.
- `plugin list --json` has an `installed` entry whose `name` is `pstack`.
- `inspect --json` `plugins[]` has `name: "pstack"`, `provides.skills` ≥ 40 (this tree ships 44 `skills/*/SKILL.md`), `provides.agents` = 3 (`poteto-agent`, `independent-verifier`, `comment-sicko`).
- `PLUGIN_PATH` is a real directory containing `plugin.json` and `skills/poteto-mode/SKILL.md`.

**PASS.** Plugin `pstack` is installed with `--trust`, enabled, and `grok inspect --json` reports it with a non-zero skill count and three agents.

**FAIL.** Install fails, enable fails, inspect has no `pstack` row, or `provides.skills` is 0.

**Evidence to keep.** All `gate1-*` files, `PLUGIN_PATH.txt`, and the no-trust exit code.

**Do not implement port code** if install fails because GitHub is unreachable. Use the local-path fallback. Only add a repo file if a gate is blocked by a missing file in the plugin tree (this plan does not need one).

---

## Gate 2. Skills and agents visible in a live session

`poteto-mode` is `disable-model-invocation: true` (`08-skills.md`). It is slash-only. It should still be **user-invocable**. Headless `streaming-messages-json` `system/init.skills` lists user-invocable skill names. `inspect --json` `skills[]` is the catalog (`name`, `userInvocable`, `disabled`, `invocableAs` on collision).

**Commands**

```bash
jq '[.skills[] | {name, source, userInvocable, disabled, collidesWith, invocableAs}]' \
  "$EVIDENCE/gate1-inspect.json" \
  | tee "$EVIDENCE/gate2-inspect-skills.json"

jq '[.agents[] | {name, source, description}]' \
  "$EVIDENCE/gate1-inspect.json" \
  | tee "$EVIDENCE/gate2-inspect-agents.json"

# Live session advertisement. init.skills is on streaming-messages-json, not streaming-json.
grok -p "Reply with exactly the word pong and stop. Do not call tools." \
  "${GROK_BASE[@]}" "${GROK_INIT[@]}" \
  --max-turns 1 \
  2>"$EVIDENCE/gate2-init.err" | tee "$EVIDENCE/gate2-init.ndjson"

jq -c 'select(.type=="system" and .subtype=="init") | {model, tools, slash_commands, skills, permissionMode}' \
  "$EVIDENCE/gate2-init.ndjson" \
  | tee "$EVIDENCE/gate2-init.json"
```

If a name collides with a built-in, inspect sets `invocableAs` to the qualified form (`pstack:poteto-mode`). Use that form in later gates.

**Inspect**

Required **skill** names (hyphen-normalized, case-insensitive), source tied to plugin `pstack`:

- `poteto-mode` (frontmatter `name: Poteto Mode`; grok normalizes spaces to hyphens)
- `setup-pstack`
- `how`
- `unslop`

Required **agent** names (bare or `pstack:` qualified):

- `poteto-agent`
- `independent-verifier`
- `comment-sicko`

`init.skills` (or `slash_commands`) contains `poteto-mode` / `setup-pstack` unless inspect says they are not user-invocable. `poteto-mode` may be absent from auto-invoke and still present as a slash command.

**PASS.** Inspect lists those four skills and three agents from plugin `pstack`, and the live `init` line advertises `poteto-mode` as invocable (bare or qualified).

**FAIL.** Any required name is missing from inspect after enable, or the live session does not advertise `poteto-mode`.

**Evidence to keep.** `gate2-inspect-skills.json`, `gate2-inspect-agents.json`, `gate2-init.ndjson`, `gate2-init.json`.

---

## Gate 3. No live Cursor tool names

Static grep of the **installed** plugin path (not this Cloud Agent workspace) plus a live stream.

**Commands**

```bash
export PLUGIN_PATH="$(cat "$EVIDENCE/PLUGIN_PATH.txt")"

# Disk. HARNESS.md may mention Cursor names as negatives. Exclude it.
rg -n --hidden \
  -g '!HARNESS.md' -g '!UPSTREAM' -g '!TEST-PLAN.md' -g '!scripts/**' -g '!automations/**' \
  -e 'AskQuestion' -e 'TodoWrite' -e 'generalPurpose' -e 'allow_multiple' \
  -e 'environment:\s*"cloud"' -e "environment:\s*'cloud'" \
  "$PLUGIN_PATH" \
  | tee "$EVIDENCE/gate3-rg-installed.txt"

# Live stream from a later gate also counts. Run a cheap session now:
grok -p "/poteto-mode Reply with one sentence about what a SKILL.md file is. Stay read-only. Do not edit files." \
  "${GROK_BASE[@]}" "${GROK_STREAM[@]}" \
  --max-turns 12 \
  2>"$EVIDENCE/gate3-live.err" | tee "$EVIDENCE/gate3-live.ndjson"

jq -r 'select(.type=="tool_call") | .toolName' "$EVIDENCE/gate3-live.ndjson" \
  | sort | uniq -c | tee "$EVIDENCE/gate3-toolNames.txt"

jq -c 'select(.type=="tool_call") | {toolName, rawInput}' "$EVIDENCE/gate3-live.ndjson" \
  | tee "$EVIDENCE/gate3-tool-calls.jsonl"
```

Forbidden **live** `toolName` values: `AskQuestion`, `TodoWrite`.

Forbidden **live** `task` / `Task` / `spawn_subagent` `rawInput` keys/values:

- `environment` = `"cloud"` (or any cloud agent environment field)
- `capability_mode` (schemars-skipped on `TaskToolInput`; JSON that sends it is ignored, and sending it means the model is still on the Cursor schema)
- `reasoning_effort` on the spawn tool
- `subagent_type` = `generalPurpose` (Cursor). Grok's built-in is `general-purpose`.

Allowed live ids include `task`, `Task`, `spawn_subagent` (aliases), `todo_write`, `ask_user_question`, `get_task_output`, `run_terminal_cmd`, `read_file`, `grep`, `scheduler_create`. Canonical spawn id is `task`.

**PASS.** Installed plugin tree (excluding HARNESS.md / scripts / benny) has no forbidden Cursor call-site identifiers, and the live `toolName` list contains none of `AskQuestion` / `TodoWrite`.

**FAIL.** A live call uses a Cursor tool id, or a live `task` payload includes `environment: "cloud"`, `capability_mode`, `reasoning_effort`, or `generalPurpose`.

**Evidence to keep.** `gate3-rg-installed.txt` (empty is success), `gate3-toolNames.txt`, `gate3-tool-calls.jsonl`, `gate3-live.ndjson`.

Re-run the live `toolName` extract on Gate 5, Gate 6, and Gate 7 streams. One Cursor id in any of them fails Gate 3.

---

## Gate 4. `/setup-pstack` writes only detected slugs

`setup-pstack/SKILL.md` step 1. Enumerate slugs the `task` tool accepts in `model` this session. Prefer `grok inspect --json` if it lists models. A rejected `task.model` error that names valid slugs is also evidence. Never write a slug you have not confirmed. `inherit-parent` and `auto` are always valid and are not slugs. Omit `model` on `task` so the child inherits.

`InspectReport` (`inspect/mod.rs`) has **no models catalog**. Do not pretend inspect listed slugs if the JSON has no such field.

**Commands. Detect first, before setup.**

```bash
# 4a. Inspect has no model list. Prove that.
jq 'keys' "$EVIDENCE/gate1-inspect.json" | tee "$EVIDENCE/gate4-inspect-keys.json"
jq 'has("models")' "$EVIDENCE/gate1-inspect.json" | tee "$EVIDENCE/gate4-inspect-has-models.txt"

# 4b. Parent model is available (Gate 0 already used -m grok-4.6). Record it.
echo "$GROK_MODEL" | tee "$EVIDENCE/gate4-detected-slugs.txt"

# 4c. Rejected slug. Capture the validator's list of valid slugs if the error names them.
grok -p 'Call the task tool exactly once with these fields and then stop:
prompt: Reply pong and stop. Do not edit files.
description: slug probe
subagent_type: explore
run_in_background: true
model: __pstack_probe_not_a_real_model__
Do not retry with a guessed slug. After the tool error, quote the error text verbatim and stop.' \
  "${GROK_BASE[@]}" "${GROK_STREAM[@]}" \
  --max-turns 8 \
  2>"$EVIDENCE/gate4-probe.err" | tee "$EVIDENCE/gate4-probe.ndjson"

jq -c 'select(.type=="tool_call" or .type=="tool_call_update" or .type=="text" or .type=="error")' \
  "$EVIDENCE/gate4-probe.ndjson" \
  | tee "$EVIDENCE/gate4-probe-extract.jsonl"
```

Build the detected set. Union of:

1. Every slug named in the `task.model` rejection text.
2. `$GROK_MODEL` (`grok-4.6`) because Gate 0 used it successfully.
3. Any slug that inspect actually listed (unexpected; keep it if present).

Write the set one slug per line to `$EVIDENCE/gate4-detected-slugs.txt`. If the rejection text does **not** name other slugs, the detected set is **only** `grok-4.6`. Do not add `grok-4.6-fast-xhigh`, `claude-fable-5-thinking-max`, `gpt-5.6-sol-max`, or `claude-opus-5-thinking-xhigh` because they appear in the skill's default TOML.

**Commands. Backup, then run setup.**

```bash
if [ -f "$HOME/.grok/pstack-models.toml" ]; then
  cp -a "$HOME/.grok/pstack-models.toml" "$EVIDENCE/gate4-pstack-models.toml.pre"
fi

# Preferred: TUI. ask_user_question can hang headless.
# In a real grok TUI on this box:
#   /setup-pstack
# Answer every role with a detected slug, or inherit-parent / auto.
# Decline the verify-* skill offer (Gate 6 uses a tiny folder, not an app harness).

# Headless fallback if TUI is unavailable. timeout so a hung ask_user_question cannot eat the night.
timeout 180s grok -p '/setup-pstack
Detected slugs for this machine are listed here. Use only these, or inherit-parent, or auto.
Do not write any other real slug.
DETECTED:
'"$(cat "$EVIDENCE/gate4-detected-slugs.txt")"'
If you would call ask_user_question, do not. Write ~/.grok/pstack-models.toml now with inherit-parent for every role (or the single detected slug). Decline creating .grok/skills/verify-*. Stop after the file is written and print the file path.' \
  "${GROK_BASE[@]}" "${GROK_STREAM[@]}" \
  --max-turns 20 \
  2>"$EVIDENCE/gate4-setup.err" | tee "$EVIDENCE/gate4-setup.ndjson"
echo $? | tee "$EVIDENCE/gate4-setup.exit"
```

If the TUI was used, copy the session transcript or a screenshot plus the resulting file. Headless NDJSON is enough when it actually wrote the file.

```bash
cp -a "$HOME/.grok/pstack-models.toml" "$EVIDENCE/gate4-pstack-models.toml"
cat "$EVIDENCE/gate4-pstack-models.toml"
```

**Validate the file by hand**

Every **real slug** (not `inherit-parent`, not `auto`, not comments) in the TOML must appear in `$EVIDENCE/gate4-detected-slugs.txt`.

```bash
# Extract quoted strings that look like model slugs. Review the list; do not treat this as a parser.
grep -oE '"[^"]+"' "$EVIDENCE/gate4-pstack-models.toml" \
  | tr -d '"' \
  | grep -vE '^(inherit-parent|auto)$' \
  | sort -u \
  | tee "$EVIDENCE/gate4-written-slugs.txt"

# Each written slug must be in the detected set.
while read -r slug; do
  grep -Fxq "$slug" "$EVIDENCE/gate4-detected-slugs.txt" \
    || echo "UNDETECTED: $slug"
done < "$EVIDENCE/gate4-written-slugs.txt" \
  | tee "$EVIDENCE/gate4-undetected.txt"
```

**PASS.** `~/.grok/pstack-models.toml` exists after `/setup-pstack`, and every real slug in it is in the detected set. `gate4-undetected.txt` is empty.

**FAIL.** The file is missing, or it contains a default-panel slug that was never confirmed (`claude-fable-5-thinking-max`, `gpt-5.6-sol-max`, `grok-4.6-fast-xhigh`, `claude-opus-5-thinking-xhigh`, or any other unconfirmed slug).

**CANNOT-PROVE (not PASS).** Headless hung on `ask_user_question` (exit 124) and TUI was not available. Retry in TUI. Do not mark PASS from the hung run.

**Evidence to keep.** Detected-slugs file, probe NDJSON, setup NDJSON or TUI notes, pre/post TOML, written-slugs, undetected (empty).

---

## Gate 5. `/poteto-mode` matches Investigation and copies steps into todos

Lab folder (tiny, local, not DeepSeek Harness):

```bash
export LAB=/tmp/pstack-edith-lab
rm -rf "$LAB"
mkdir -p "$LAB"
cat > "$LAB/hello.py" << 'PY'
#!/usr/bin/env python3
print("hello")
PY
chmod +x "$LAB/hello.py"
python3 "$LAB/hello.py" | tee "$EVIDENCE/gate5-hello-before.txt"
# Must be exactly: hello
```

**Commands**

```bash
grok -p '/poteto-mode How does hello.py work?
Read-only. Do not edit files. Do not open a PR.' \
  "${GROK_BASE[@]}" "${GROK_STREAM[@]}" \
  --cwd "$LAB" \
  --max-turns 40 \
  2>"$EVIDENCE/gate5.err" | tee "$EVIDENCE/gate5.ndjson"
```

**Inspect**

Dump todos from both channels grok actually emits:

```bash
jq -c 'select(.type=="plan")' "$EVIDENCE/gate5.ndjson" \
  | tee "$EVIDENCE/gate5-plan.jsonl"

jq -c 'select(.type=="tool_call" and (.toolName=="todo_write" or .toolName=="TodoWrite")) | .rawInput' \
  "$EVIDENCE/gate5.ndjson" \
  | tee "$EVIDENCE/gate5-todo_write.jsonl"

jq -r 'select(.type=="tool_call") | .toolName' "$EVIDENCE/gate5.ndjson" \
  | sort | uniq -c | tee "$EVIDENCE/gate5-toolNames.txt"
```

Playbook file (installed copy): `$PLUGIN_PATH/skills/poteto-mode/playbooks/investigation.md`.

Required todo contents, in order after the principles item. Copied verbatim or with `skip: <reason>` still present. Silent drop is FAIL.

From `skills/poteto-mode/SKILL.md` (non-negotiables):

1. First todo. Read the Principles section of poteto-mode in full.

From `playbooks/investigation.md`:

2. Route through the **how** skill (Explain mode for this narrow question).
3. `throughput checkpoint: n/a, read-only investigation`
4. Produce the `how`-shaped output (Overview / Key Concepts / How It Works / Where Things Live / Gotchas).
5. Apply the **unslop** skill to the reply.

No PR. Investigation says no Opening a PR.

**PASS.** The first todo is the Principles read, and the Investigation steps appear as todos (skipped ones still listed with `skip:`). The reply has the how-shaped sections. `hello.py` is unchanged.

**FAIL.** The agent writes a bespoke plan that drops named Investigation steps, or it edits `hello.py`, or it never calls `todo_write` / never emits a `plan` with those steps.

**Evidence to keep.** `gate5.ndjson`, plan + todo extracts, `hello.py` copy (`cp "$LAB/hello.py" "$EVIDENCE/gate5-hello.py"`), toolNames.

---

## Gate 6. One real local Feature task with command plus output

Same `$LAB`. Still not DeepSeek Harness. Still not a GitHub PR.

Seed git so Feature step 6 can commit locally:

```bash
git -C "$LAB" init
git -C "$LAB" add hello.py
git -C "$LAB" -c user.email=edith@local -c user.name=EDITH commit -m 'chore(lab): seed hello.py'
```

**Commands**

```bash
grok -p '/poteto-mode Add a --json flag to hello.py.
Default stdout must stay exactly the bytes: hello\n
python3 hello.py --json must print exactly: {"msg":"hello"}\n
Verify by running both commands yourself this session. Keep the command output in your work.
Do not open a PR. Skip opening-a-pr with reason: edith local lab.
Independent verify is still mandatory (Feature step 4). Spawn it from this parent with task.' \
  "${GROK_BASE[@]}" "${GROK_STREAM[@]}" \
  --cwd "$LAB" \
  --max-turns 80 \
  2>"$EVIDENCE/gate6.err" | tee "$EVIDENCE/gate6.ndjson"
```

`--max-turns 80` is the floor. Parent plus `poteto-agent` plus `independent-verifier` plus shell. Raise it rather than false-FAIL.

**Inspect**

Todos must be the Feature playbook (`$PLUGIN_PATH/skills/poteto-mode/playbooks/feature.md`), copied in, first item still Principles:

1. `how` over the affected subsystem.
2. `architect` or `architect skipped: <reason>`.
3. Four throughput-checkpoint todos (Blocking first steps / Independent workstreams / Shared mutable state / Smallest safe decomposition). Unused dimensions stay with `n/a: <reason>`.
4. Parent `task` `subagent_type: "poteto-agent"` (or `pstack:poteto-agent`) **and** parent `task` `subagent_type: "independent-verifier"` (or `pstack:independent-verifier`). Independent verify has **no skip-with-reason escape**.
5. Verify on the matching surface (the two python commands).
6. Commits (local is enough).
7. `interrogate` or `skip: <reason>` (not contested is a valid skip).
8. Opening a PR stays in the list as `skip: edith local lab` (or equivalent). Silent drop is FAIL.

Extract shell evidence:

```bash
jq -c 'select(.type=="tool_call") | {toolName, rawInput}' "$EVIDENCE/gate6.ndjson" \
  | tee "$EVIDENCE/gate6-tool-calls.jsonl"

jq -c 'select(.type=="tool_call_update") | {toolCallId, status, rawOutput}' "$EVIDENCE/gate6.ndjson" \
  | tee "$EVIDENCE/gate6-tool-updates.jsonl"

# After the session, EDITH also runs the binary herself:
python3 "$LAB/hello.py" | tee "$EVIDENCE/gate6-edith-default.txt"
python3 "$LAB/hello.py" --json | tee "$EVIDENCE/gate6-edith-json.txt"
printf 'hello\n' > "$EVIDENCE/gate6-expected-default.txt"
printf '{"msg":"hello"}\n' > "$EVIDENCE/gate6-expected-json.txt"
cmp -s "$EVIDENCE/gate6-edith-default.txt" "$EVIDENCE/gate6-expected-default.txt"
cmp -s "$EVIDENCE/gate6-edith-json.txt" "$EVIDENCE/gate6-expected-json.txt"
cp "$LAB/hello.py" "$EVIDENCE/gate6-hello.py"
```

The **session** stream must contain the same two commands and their stdout, not only EDITH's after-the-fact rerun. Search `rawInput` / `rawOutput` / `content` for `hello.py` and the JSON object.

**PASS.** Feature todos are present (with explicit skips), both python invocations appear **in the session** with the exact stdout above, and EDITH's rerun matches.

**FAIL.** Outputs differ, the agent only *claims* it ran the commands, Feature steps were replaced by a bespoke plan, or Opening a PR ran against GitHub despite the skip instruction.

**Evidence to keep.** `gate6.ndjson`, tool extracts, both expected/actual stdout files, `gate6-hello.py`, git log if commits happened (`git -C "$LAB" log --oneline | tee "$EVIDENCE/gate6-git-log.txt"`).

Independent-verifier spawn is scored in Gate 7 using this same stream when present.

---

## Gate 7. Independent verifier via parent `task` and a different model

Feature step 4. Parent session only (`MAX_SUBAGENT_DEPTH` is 1; a child that calls `task` fails).

Required spawn shape (`HARNESS.md` / `TaskToolInput`):

```text
task
  prompt: <you did not write hello.py. Do not edit. Run python3 hello.py and python3 hello.py --json. Return PASS, PASS+NOTES, or FAIL with commands and output.>
  description: independent verify lab
  subagent_type: independent-verifier   # or pstack:independent-verifier
  run_in_background: true
  model: <a detected slug DIFFERENT from the writer>
  isolation: worktree                   # when the writer still holds the tree; none is acceptable if the child does not write
```

Then parent joins:

```text
get_task_output
  task_ids: [<id>]
  timeout_ms: <positive, e.g. 120000>
```

**Commands if Gate 6 already spawned it**

Reuse `$EVIDENCE/gate6.ndjson`. If it did not spawn the verifier, run a follow-up **in the same lab**, still as the parent (new headless session is a parent):

```bash
# Only if Gate 6 missed the spawn. Writer model is GROK_MODEL.
# OTHER must be a second line from gate4-detected-slugs.txt.
OTHER="$(grep -vx "$GROK_MODEL" "$EVIDENCE/gate4-detected-slugs.txt" | head -n1)"
echo "OTHER=$OTHER" | tee "$EVIDENCE/gate7-other-slug.txt"

if [ -z "$OTHER" ]; then
  echo "CANNOT-PROVE: detected set has only $GROK_MODEL" \
    | tee "$EVIDENCE/gate7-cannot-prove.txt"
else
  grok -p '/poteto-mode Do not edit hello.py.
From this parent session, call task with subagent_type independent-verifier (or pstack:independent-verifier), run_in_background true, model '"$OTHER"', prompt instructing a read-only rerun of python3 hello.py and python3 hello.py --json in '"$LAB"'.
Join with get_task_output. Quote the child verdict. Do not spawn from a child.' \
    "${GROK_BASE[@]}" "${GROK_STREAM[@]}" \
    --cwd "$LAB" \
    --max-turns 40 \
    2>"$EVIDENCE/gate7.err" | tee "$EVIDENCE/gate7.ndjson"
fi
```

**Inspect**

```bash
# Prefer gate6 stream; fall back to gate7.
SRC="$EVIDENCE/gate6.ndjson"
[ -f "$EVIDENCE/gate7.ndjson" ] && SRC="$EVIDENCE/gate7.ndjson"

jq -c 'select(.type=="tool_call" and (.toolName=="task" or .toolName=="Task" or .toolName=="spawn_subagent"))
       | .rawInput' "$SRC" \
  | tee "$EVIDENCE/gate7-task-spawns.jsonl"

jq -c 'select(.type=="tool_call" and (.toolName=="get_task_output" or .toolName=="wait_tasks"))
       | .rawInput' "$SRC" \
  | tee "$EVIDENCE/gate7-joins.jsonl"
```

Checks:

1. At least one spawn has `subagent_type` `independent-verifier` or `pstack:independent-verifier`.
2. That spawn's `model` is set and **≠** the writer slug (`$GROK_MODEL` or the `poteto-agent` child's `model`).
3. Parent called `get_task_output` (or waited until the child finished in-stream).
4. Child verdict is `PASS`, `PASS+NOTES`, or `FAIL`, with commands it ran. A child that only restates the parent's claim without running python is FAIL.
5. Child did not write. `git -C "$LAB" diff` after the verifier matches the post-Gate-6 tree, or the verifier stream has no write tools completing.

**PASS.** Parent `task` spawned `independent-verifier` with a **different** `model`, joined it, and the child returned a verdict with its own command output.

**FAIL.** No such spawn, spawn used the same model as the writer, the child wrote files, or the child skipped running the two python commands.

**CANNOT-PROVE (not PASS).** Detected set has a single slug (`grok-4.6` only). `inherit-parent` vs `grok-4.6` is the same model. Do not mark PASS. Write `gate7-cannot-prove.txt`.

**Evidence to keep.** Task spawn JSON, join JSON, child output (from `tool_call_update` / `get_task_output` rawOutput), `gate7-other-slug.txt` or `gate7-cannot-prove.txt`.

---

## Gate 8. Overnight / loop, only if cheap and deterministic

Full overnight (`/poteto-mode i'm going to bed` + Autonomous run + `/loop until done`) **cannot be proven in under 10 minutes**. **SKIP** that playbook. SKIP is not PASS.

Cheap loop probe (budget **<10 minutes**, aim **<3**). grok-build `/loop` expands to `scheduler_create` with `fire_immediately: true` (`xai-grok-tools-api` `slash_commands.rs`). `interval` minimum is **60s**. Schema default for `fire_immediately` is false. `/loop` instruction sets it true. `recurring` is schemars-skipped; do not send `recurring: false`.

**Commands**

```bash
# Skip immediately if the live tool list has no scheduler_create.
jq -r 'select(.type=="available_commands") | .tools[]?' "$EVIDENCE/gate2-init.ndjson" \
  2>/dev/null | tee "$EVIDENCE/gate8-tools-from-init.txt" || true

PROBE=/tmp/pstack-loop-probe.txt
rm -f "$PROBE"

timeout 180s grok -p '/loop 60s
On each fire, write the single line "loop-ok" to /tmp/pstack-loop-probe.txt using the shell, then call scheduler_delete on the scheduler you just created. Stop after delete. Do not start a second scheduler.' \
  "${GROK_BASE[@]}" "${GROK_STREAM[@]}" \
  --max-turns 20 \
  --cwd "$LAB" \
  2>"$EVIDENCE/gate8.err" | tee "$EVIDENCE/gate8.ndjson"
echo $? | tee "$EVIDENCE/gate8.exit"

jq -c 'select(.type=="tool_call") | {toolName, rawInput}' "$EVIDENCE/gate8.ndjson" \
  | tee "$EVIDENCE/gate8-tool-calls.jsonl"

test -f "$PROBE" && cat "$PROBE" | tee "$EVIDENCE/gate8-probe.txt" || true
```

**PASS.** Stream shows `scheduler_create` with `interval` of at least `60s` and `fire_immediately: true` (or `/loop` clearly issued and the create call matches), the probe file contains `loop-ok`, and `scheduler_delete` ran. Whole gate finished in under 10 minutes.

**FAIL.** Scheduler fired in a destructive way, never deleted, or wrote the wrong path.

**SKIP (not PASS).** `scheduler_create` is not a live tool, `/loop` is missing, `fire_immediately` never happens and waiting a full interval would exceed 10 minutes, or the run hits `--max-turns` before create. Write the skip reason in `$EVIDENCE/gate8-skip.txt`.

Do not treat SKIP as evidence the overnight playbook works.

---

## Optional hygiene (not a pass gate)

```bash
# Static tree check only. Not proof. Do not submit as Gate evidence.
# python3 "$PLUGIN_PATH/scripts/verify-harness.py"
```

If you run it, keep the output under `$EVIDENCE/optional-verify-harness.txt` and label it **not a gate**.

---

## One-page checklist (tick in `$EVIDENCE/CHECKLIST.md`)

Copy this block into `$EVIDENCE/CHECKLIST.md` and tick as you go.

```text
pstack-grokbuild EDITH checklist
Evidence dir:

[ ] Did not use scripts/verify-harness.py (or any Python harness) as proof
[ ] Did not use a Cloud Agent VM transcript as proof
[ ] Gate 0 PASS  grok-4.6 + --always-approve + --reasoning-effort xhigh ping
[ ] Gate 1 PASS  grok plugin install --trust, then grok plugin enable pstack
[ ] Gate 1 note  without --trust: exit 1, no TUI wait (or recorded CLI delta)
[ ] Gate 2 PASS  poteto-mode, setup-pstack, how, unslop visible; 3 agents visible
[ ] Gate 3 PASS  no live AskQuestion / TodoWrite / generalPurpose / environment cloud
[ ] Gate 4 PASS  ~/.grok/pstack-models.toml slugs ⊆ detected set (no default-panel fiction)
[ ] Gate 5 PASS  /poteto-mode matched Investigation; Principles first; steps copied to todos
[ ] Gate 6 PASS  Feature on /tmp/pstack-edith-lab; both python commands + exact stdout in-session
[ ] Gate 7 PASS  parent task independent-verifier + different model + child command evidence
     or [ ] Gate 7 CANNOT-PROVE (only one detected slug). Not ticked as PASS.
[ ] Gate 8 PASS cheap /loop 60s + scheduler_delete in <10 min
     or [ ] Gate 8 SKIP (missing scheduler, or cannot prove in <10 min). Not ticked as PASS.
[ ] Overnight Autonomous run SKIP (cannot prove in <10 min)
[ ] Evidence directory saved (ndjson, toml, hello.py, stdout files)

Final: every required gate is PASS, and Gate 7/8 are PASS or an allowed CANNOT-PROVE/SKIP.
Required: 0, 1, 2, 3, 4, 5, 6. Gate 7 required unless CANNOT-PROVE. Gate 8 optional with SKIP.
```

---

## After the run

Pack evidence:

```bash
tar -C "$(dirname "$EVIDENCE")" -czf "${EVIDENCE}.tar.gz" "$(basename "$EVIDENCE")"
ls -lh "${EVIDENCE}.tar.gz"
```

Hand Cola the tarball plus the ticked checklist. A narrative without the NDJSON is not a result.
