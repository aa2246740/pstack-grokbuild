#!/usr/bin/env python3
"""Rewrite Cursor harness call sites onto grok-build tools.

Principles and playbook steps stay. Only named harness APIs change.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

SKIP_DIRS = {".git", "automations"}
TEXT_SUFFIXES = {".md", ".toml", ".json", ".ts", ".sh"}

REPLACEMENTS: list[tuple[str, str]] = [
    ("~/.cursor/rules/pstack-models.mdc", "~/.grok/pstack-models.toml"),
    ("AskQuestion", "ask_user_question"),
    ("TodoWrite", "todo_write"),
    ('subagent_type: "generalPurpose"', 'subagent_type: "general-purpose"'),
    ("subagent_type: generalPurpose", 'subagent_type: "general-purpose"'),
    ("`generalPurpose`", "`general-purpose`"),
    ("generalPurpose", "general-purpose"),
    ('environment: "cloud"', 'isolation: "worktree"'),
    ('environment: "local"', 'isolation: "none"'),
    ("the Task tool", "the `task` tool"),
    ("The Task tool", "The `task` tool"),
    ("`Task` tool", "`task` tool"),
    ("`Task` calls", "`task` calls"),
    ("`Task` call", "`task` call"),
    ("Task calls", "`task` calls"),
    ("Task call", "`task` call"),
    ("via Task ", "via `task` "),
    ("using the Task ", "using the `task` "),
    ("is_background: true", "background: true"),
    ("Cursor cloud agent", "worktree `task` child"),
    ("Cursor Cloud Agent", "worktree `task` child"),
    ("cursor cloud agent", "worktree `task` child"),
    ("Cursor's built-in babysit skill", "Grok Build's built-in babysit command"),
    ("one Cursor cloud agent per PR", "one worktree `task` child per PR"),
    ("One Cursor cloud agent per PR", "One worktree `task` child per PR"),
    ("each a Cursor cloud agent", "each a worktree `task` child"),
    ('subagent_type: "Comment Sicko"', 'subagent_type: "comment-sicko"'),
    ("`Comment Sicko`", "`comment-sicko`"),
]


def should_skip(path: pathlib.Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    if path.name in {"HARNESS.md", "UPSTREAM", "adapt-harness.py"}:
        return True
    return path.suffix not in TEXT_SUFFIXES and path.name != "SKILL.md"


def transform(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    # Cursor Task `readonly` is not a grok-build task field.
    text = re.sub(
        r"^- `readonly`: `true`.*\n",
        "- read-only: use `subagent_type: \"explore\"`. Do not send `readonly` or `capability_mode` on `task`; grok-build ignores `capability_mode` on the wire.\n",
        text,
        flags=re.M,
    )
    text = re.sub(
        r"^- `readonly`: `false`.*\n",
        "- MCP-backed work: use `subagent_type: \"general-purpose\"` and forbid writes in the prompt. Do not send `readonly` on `task`.\n",
        text,
        flags=re.M,
    )
    text = text.replace("agent mode (readonly strips MCP)", "agent mode (`general-purpose`, MCP inherited)")
    text = text.replace("readonly strips MCP", "`explore` is the read-only type; it is not an MCP sandbox")
    text = text.replace("Readonly/Ask mode strips MCPs", "`explore` is read-oriented; MCP-backed work uses `general-purpose`")
    return text


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        original = path.read_text(encoding="utf-8")
        updated = transform(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(path.relative_to(ROOT))
    print(f"rewrote {changed} files")


if __name__ == "__main__":
    main()
