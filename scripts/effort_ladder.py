#!/usr/bin/env python3
"""Three-tier pstack effort split from the live CLI usable set.

Ship-time snapshot is grok 1.0.5 CLI rejection (verbatim):

  unknown effort level 'not-a-real-effort'; use one of: xhigh, high, medium, low

That list is strongest-first. Orient to weak→strong: low, medium, high, xhigh.
Do not use Effort::VALID_VALUES or ReasoningEffort::from_str. Those include
reserved `max` that this CLI rejects. Do not offer `max` unless the live
`use one of:` list named it. `/setup-pstack` re-detects. Spawn skills have
no task.reasoning_effort field.
"""

from __future__ import annotations

import argparse
import re
import sys

# Weak → strong after orienting the grok 1.0.5 `use one of:` list.
# Not Effort::VALID_VALUES. `max` is omitted until a live CLI names it.
SHIP_TIME_ENUM: tuple[str, ...] = ("low", "medium", "high", "xhigh")

# Rank used only to detect strongest-first vs weakest-first among tokens
# the live list actually named. Not a source of which tokens exist.
KNOWN_RANK: dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "xhigh": 3,
    "max": 4,
    "ultra": 5,
}

NOT_USABLE = frozenset({"none", "minimal", "deep"})

MECHANICAL: tuple[str, ...] = (
    "feature",
    "refactoring",
    "how-explorer",
    "why-investigators",
    "swarm-workers",
)
INSTRUCTION: tuple[str, ...] = (
    "bug-fix",
    "perf-issue",
    "hillclimb",
    "reflect-tooling",
)
JUDGMENT: tuple[str, ...] = (
    "judgment-and-prose",
    "hardest-tasks",
    "how-explainer",
    "why-synthesizer",
    "reflect-judgment",
    "independent-verifier",
    "how-critics",
    "arena-runners",
    "arena-cross-judge-pool",
    "architect-runners",
    "interrogate-reviewers",
)

_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_USE_ONE_OF = re.compile(r"use one of:\s*([^\n]+)", re.I)
_NOISE = frozenset(
    {
        "reasoning",
        "effort",
        "unknown",
        "level",
        "levels",
        "one",
        "of",
        "use",
        "invalid",
        "expected",
        "canonical",
        "also",
        "help",
        "flag",
        "cli",
        "value",
        "values",
        "possible",
        "per",
        "model",
        "menu",
        "ids",
        "like",
        "tui",
        "headless",
        "not",
        "a",
        "real",
    }
)


def filter_usable_levels(levels: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for token in levels:
        key = token.strip().lower()
        if not key or key in NOT_USABLE or key in seen or "-" in key:
            continue
        seen.add(key)
        out.append(key)
    return out


def orient_weak_to_strong(tokens: list[str] | tuple[str, ...]) -> list[str]:
    """If the printed list is strongest-first, reverse it."""
    levels = filter_usable_levels(list(tokens))
    ranked = [KNOWN_RANK[t] for t in levels if t in KNOWN_RANK]
    if len(ranked) >= 2 and ranked[0] > ranked[-1]:
        return list(reversed(levels))
    return levels


def parse_use_one_of(text: str) -> list[str]:
    """Parse a live CLI runtime validator. Prefer `use one of:`.

    Does not read `expected one of:` (FromStr / VALID_VALUES, includes reserved max).
    """
    found: list[str] = []
    for match in _USE_ONE_OF.finditer(text):
        for tok in _TOKEN.findall(match.group(1)):
            key = tok.lower()
            if key in NOT_USABLE or key in _NOISE or key in found:
                continue
            found.append(key)
        if found:
            break
    return orient_weak_to_strong(found)


def three_tier(ordered: list[str] | tuple[str, ...]) -> tuple[str, str, str]:
    """Return (judgment, instruction, mechanical).

    Highest available, highest−1, highest−2. Input may be strongest-first
    (`use one of: xhigh, high, medium, low`) or weakest-first. If highest−2
    would be the weakest value and there are ≥3 levels, clamp mechanical to
    the second-weakest. With only two levels, mechanical may sit on the floor.
    """
    levels = orient_weak_to_strong(list(ordered))
    if not levels:
        raise ValueError("no usable effort levels")
    n = len(levels)
    judgment = levels[-1]
    instruction = levels[-2] if n >= 2 else levels[-1]
    if n >= 3:
        mech_idx = n - 3
        if mech_idx == 0:
            mech_idx = 1
        mechanical = levels[mech_idx]
    else:
        mechanical = levels[0]
    return judgment, instruction, mechanical


def role_effort_map(
    ordered: list[str] | tuple[str, ...] | None = None,
) -> dict[str, str]:
    judgment, instruction, mechanical = three_tier(list(ordered or SHIP_TIME_ENUM))
    out: dict[str, str] = {}
    for key in MECHANICAL:
        out[key] = mechanical
    for key in INSTRUCTION:
        out[key] = instruction
    for key in JUDGMENT:
        out[key] = judgment
    return out


def self_check() -> None:
    live = (
        "--effort/--reasoning-effort: unknown effort level 'not-a-real-effort'; "
        "use one of: xhigh, high, medium, low"
    )
    parsed = parse_use_one_of(live)
    if parsed != ["low", "medium", "high", "xhigh"]:
        raise SystemExit(f"parse_use_one_of(live) = {parsed!r}")
    fromstr = (
        "invalid reasoning effort: 'nope' "
        "(expected one of: none, minimal, low, medium, high, xhigh, max)"
    )
    if parse_use_one_of(fromstr) != []:
        raise SystemExit("parse_use_one_of must ignore expected one of / VALID_VALUES")
    if "max" in SHIP_TIME_ENUM:
        raise SystemExit("ship-time enum must not include reserved max")
    cases = [
        (["xhigh", "high", "medium", "low"], ("xhigh", "high", "medium")),
        (["low", "medium", "high", "xhigh"], ("xhigh", "high", "medium")),
        (["max", "xhigh", "high", "medium", "low"], ("max", "xhigh", "high")),
        (["low", "medium", "high"], ("high", "medium", "medium")),
        (["low", "high"], ("high", "low", "low")),
        (["high"], ("high", "high", "high")),
        (["none", "minimal", "xhigh", "high", "medium", "low", "deep"], ("xhigh", "high", "medium")),
    ]
    for enum, expected in cases:
        got = three_tier(enum)
        if got != expected:
            raise SystemExit(f"three_tier({enum!r}) = {got!r}, expected {expected!r}")
    mapping = role_effort_map(SHIP_TIME_ENUM)
    if mapping["feature"] != "medium" or mapping["bug-fix"] != "high":
        raise SystemExit(f"ship-time map wrong: {mapping}")
    if mapping["how-explainer"] != "xhigh" or mapping["independent-verifier"] != "xhigh":
        raise SystemExit(f"ship-time judgment wrong: {mapping}")
    if any(v == "max" for v in mapping.values()):
        raise SystemExit("ship-time map must not assign reserved max")
    if len(mapping) != len(MECHANICAL) + len(INSTRUCTION) + len(JUDGMENT):
        raise SystemExit("role count mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enum",
        help="comma-separated tokens (strongest-first or weakest-first)",
    )
    parser.add_argument(
        "--enum-file",
        help="file with one token per line",
    )
    parser.add_argument(
        "--from-rejection",
        help="parse a CLI stderr/help blob for `use one of:`",
    )
    parser.add_argument(
        "--print-enum",
        action="store_true",
        help="print one weak→strong token per line and exit",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="run built-in examples and exit",
    )
    args = parser.parse_args()
    if args.check:
        self_check()
        print("PASS")
        return
    levels: list[str]
    if args.from_rejection:
        text = open(args.from_rejection, encoding="utf-8").read()
        levels = parse_use_one_of(text)
    elif args.enum_file:
        text = open(args.enum_file, encoding="utf-8").read()
        levels = [line.strip() for line in text.splitlines() if line.strip()]
    elif args.enum:
        levels = [part.strip() for part in args.enum.split(",") if part.strip()]
    else:
        levels = list(SHIP_TIME_ENUM)
    levels = orient_weak_to_strong(levels)
    if args.print_enum:
        if not levels:
            raise SystemExit(1)
        print("\n".join(levels))
        return
    judgment, instruction, mechanical = three_tier(levels)
    print("enum:", " ".join(levels))
    print("judgment:", judgment)
    print("instruction:", instruction)
    print("mechanical:", mechanical)
    mapping = role_effort_map(levels)
    for key in (*MECHANICAL, *INSTRUCTION, *JUDGMENT):
        print(f"{key}={mapping[key]}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
