#!/usr/bin/env python3
"""Read-only check that this port kept pstack discipline and grok-build harness names.

Does not edit files. Exit 0 on pass.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAYBOOKS = ROOT / "skills" / "poteto-mode" / "playbooks"
SKILL = ROOT / "skills" / "poteto-mode" / "SKILL.md"

NAMED_22 = [
    "investigation",
    "bug-fix",
    "perf-issue",
    "hillclimb",
    "runtime-forensics",
    "trace-forensics",
    "feature",
    "refactoring",
    "prototype",
    "visual-parity",
    "authoring-a-skill",
    "eval",
    "babysit",
    "shipping",
    "autonomous-run",
    "orchestrate",
    "autopilot-full",
    "autopilot-stack",
    "session-pickup",
    "pause-safely",
    "multi-phase-plan",
    "worktree-cleanup",
]

# Cursor harness leftovers that must not remain as call sites in skills/.
# HARNESS.md, scripts/, and automations/benny are allowed to mention them.
FORBIDDEN = [
    r"\bAskQuestion\b",
    r"\bTodoWrite\b",
    r"\bgeneralPurpose\b",
    r'environment:\s*"cloud"',
    r"Cursor's `/loop`",
    r"cloud-sleeper",
    r"nesting works to depth 3",
    r"~/.cursor/rules/",
    r"origin/main:pstack/",
    r"mcps/ directory Cursor",
    r"cloud-agent URL",
]

# Official Cursor panel slugs. Must not appear as skill fallbacks.
# TEST-PLAN.md may name them as FAIL tokens. Skills may not.
CURSOR_MODEL_SLUGS = (
    "grok-4.6-fast-xhigh",
    "gpt-5.6-sol-max",
    "claude-fable-5-thinking-max",
    "claude-opus-5-thinking-xhigh",
)

SKIP_DIRS = {".git", "automations", "scripts"}
SKIP_FILES = {"HARNESS.md", "UPSTREAM", "TEST-PLAN.md"}


def allows_cursor_rules_mention(path: pathlib.Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.name in SKIP_FILES | {"README.md"}:
        return True
    parts = rel.parts
    if parts and parts[0] == "docs":
        return True
    if parts[:2] == ("skills", "setup-pstack"):
        return True
    return False


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    files = {p.stem for p in PLAYBOOKS.glob("*.md")}
    missing = [n for n in NAMED_22 if n not in files]
    extra = sorted(files - set(NAMED_22) - {"opening-a-pr"})
    if missing:
        fail(f"missing named playbooks: {missing}")
    if "opening-a-pr" not in files:
        fail("missing opening-a-pr.md (end of every playbook)")
    if extra:
        fail(f"unexpected playbook files: {extra}")

    principles = sorted(p.name for p in ROOT.joinpath("skills").glob("principle-*") if p.is_dir())
    if len(principles) != 21:
        fail(f"expected 21 principle-* skills, got {len(principles)}: {principles}")

    skill_text = SKILL.read_text(encoding="utf-8")
    for name in NAMED_22:
        if f"playbooks/{name}.md" not in skill_text:
            fail(f"poteto-mode SKILL.md does not route {name}")

    plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    name = plugin.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        fail(f"plugin.json name {name!r} is not grok-build kebab-case")
    if plugin.get("skills") != "./skills/":
        fail("plugin.json skills path must be ./skills/")
    if plugin.get("agents") != "./agents/":
        fail("plugin.json agents path must be ./agents/")

    for required in (
        "agents/poteto-agent.md",
        "agents/comment-sicko.md",
        "agents/independent-verifier.md",
        "agents/feature.md",
        "agents/how-explainer.md",
        "skills/setup-pstack/references/resolve-effort.md",
        "HARNESS.md",
    ):
        if not (ROOT / required).is_file():
            fail(f"missing {required}")

    harness = (ROOT / "HARNESS.md").read_text(encoding="utf-8")
    for token in (
        "TASK_TOOL_NAME",
        "run_in_background",
        "MAX_SUBAGENT_DEPTH",
        "ask_user_question",
        "scheduler_create",
        "get_task_output",
        "isolation",
        "independent-verifier",
        "select_role",
        "SubagentRole",
        "reasoning_effort",
    ):
        if token not in harness:
            fail(f"HARNESS.md missing {token}")

    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".toml", ".json"}:
            continue
        if SKIP_DIRS & set(path.parts) or path.name in SKIP_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        for pat in FORBIDDEN:
            if pat == r"~/.cursor/rules/" and allows_cursor_rules_mention(path):
                continue
            if re.search(pat, text):
                rel = path.relative_to(ROOT)
                hits.append(f"{rel}: /{pat}/")
    if hits:
        fail("leftover Cursor harness call sites:\n  " + "\n  ".join(hits))

    slug_hits: list[str] = []
    skills_root = ROOT / "skills"
    for path in skills_root.rglob("*"):
        if not path.is_file() or path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for slug in CURSOR_MODEL_SLUGS:
            if slug in text:
                slug_hits.append(f"{path.relative_to(ROOT)}: {slug}")
    if slug_hits:
        fail(
            "Cursor panel slugs in skills/ (omit task.model instead):\n  "
            + "\n  ".join(slug_hits)
        )

    role_keys = (
        "feature",
        "refactoring",
        "bug-fix",
        "perf-issue",
        "hillclimb",
        "judgment-and-prose",
        "hardest-tasks",
        "how-explorer",
        "how-explainer",
        "how-critics",
        "why-investigators",
        "why-synthesizer",
        "reflect-tooling",
        "reflect-judgment",
        "arena-runners",
        "arena-cross-judge-pool",
        "swarm-workers",
        "architect-runners",
        "interrogate-reviewers",
        "independent-verifier",
    )
    for key in role_keys:
        path = ROOT / "agents" / f"{key}.md"
        if not path.is_file():
            fail(f"missing role agent agents/{key}.md")
        text = path.read_text(encoding="utf-8")
        fm = text.split("---", 2)
        if len(fm) < 3:
            fail(f"{path.relative_to(ROOT)}: missing frontmatter")
        if re.search(r"(?m)^effort\s*:", fm[1]):
            fail(
                f"{path.relative_to(ROOT)}: frontmatter effort would block inherit-parent; "
                "overlay lives in ~/.grok/roles/"
            )

    agent_files = list((ROOT / "agents").glob("*.md"))
    if len(agent_files) != 22:
        fail(f"expected 22 agents/*.md, got {len(agent_files)}")

    # Not a TEST-PLAN pass gate. Catches the adapter eating "never create
    # ~/.cursor/rules" or rewriting TEST-PLAN FAIL tokens on a second run.
    import importlib.util

    adapt_path = ROOT / "scripts" / "adapt-harness.py"
    spec = importlib.util.spec_from_file_location("adapt_harness", adapt_path)
    adapt = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(adapt)
    leftover = adapt.files_transform_would_change()
    if leftover:
        fail(
            "adapt-harness transform is not a no-op on this tree:\n  "
            + "\n  ".join(leftover)
        )

    print("PASS")
    print(f"playbooks: {len(NAMED_22)} named + opening-a-pr")
    print(f"principles: {len(principles)}")
    print("plugin.json name:", name)


if __name__ == "__main__":
    main()
