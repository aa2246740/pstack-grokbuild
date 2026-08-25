# Set up pstack

In this page you install the plugin, pick which models pstack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

```bash
grok plugin install aa2246740/pstack-grokbuild --trust
```

Enable it if it stays off (`grok plugin enable pstack`, or Space in the Plugins tab). `grok inspect` should list pstack skills.

## Pick your models

Run:

```text
/setup-pstack
```

[`/setup-pstack`](../../skills/setup-pstack/SKILL.md) detects slugs your `task` tool accepts, shows each role, and asks with `ask_user_question`. It writes **only** `~/.grok/pstack-models.toml`. It never writes a Cursor rules file.

This repo is the Grok Build port. Official Cursor `/setup-pstack` (in Grok Bot or in Cursor) is a different plugin and still writes `~/.cursor/rules`.

You only override what you care about. A missing key means omit `task.model`; the child inherits the parent. Run `/setup-pstack` again to change it.

Set a role to `inherit-parent` or `auto` and pstack omits `task.model`, so the child inherits the parent. For a panel role the value is an array, and one `task` spawn runs per entry.

## Accept the verification offer, or don't

At the end of setup, `/setup-pstack` looks for a way to prove app behavior, either a `verify-*` skill under `.grok/skills/` or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes `.grok/skills/verify-<app>/`. Say no and setup moves on.

After setup, start a new session. The model file applies.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/poteto-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. The first item is always "read the Principles section". The rest are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/poteto-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `/poteto-mode` is sticky. It stays on for the conversation until you opt out by saying so.

Next: [Route work through `/poteto-mode`](./02-poteto-mode.md).
