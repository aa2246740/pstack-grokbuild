#!/usr/bin/env python3
"""Three-tier pstack effort split from a weakest→strongest grok-build enum.

Ship-time snapshot is grok-build pin c2ad97f87aea4303b6000a2c22128bc91ee76c9b
`AgentDefinition::Effort::VALID_VALUES` = low, medium, high, xhigh, max
(crates/codegen/xai-grok-agent/src/config.rs). That list is not forever.
`/setup-pstack` re-detects. Spawn skills have no task.reasoning_effort field,
so they cannot apply a newer enum without a setup overlay.
"""

from __future__ import annotations

import argparse
import sys

GROK_BUILD_PIN = "c2ad97f87aea4303b6000a2c22128bc91ee76c9b"

# Official order, weakest → strongest, at the pin above. Not the live enum.
SHIP_TIME_ENUM: tuple[str, ...] = ("low", "medium", "high", "xhigh", "max")

# CLI --reasoning-effort also parses these. They are not AgentDefinition::Effort
# values, so this plugin never ships them or offers them in setup.
# `deep` is a per-model menu id. Clap accepts the string; FromStr does not.
NOT_AGENT_DEFINITION = frozenset({"none", "minimal", "deep"})

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


def filter_agent_definition_levels(levels: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for token in levels:
        key = token.strip()
        if not key or key in NOT_AGENT_DEFINITION or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def three_tier(ordered_weak_to_strong: list[str] | tuple[str, ...]) -> tuple[str, str, str]:
    """Return (judgment, instruction, mechanical).

    Highest available, highest−1, highest−2. If highest−2 would be the
    weakest value and there are ≥3 levels, clamp mechanical to the
    second-weakest. With only two levels, mechanical may sit on the floor.
    """
    levels = filter_agent_definition_levels(list(ordered_weak_to_strong))
    if not levels:
        raise ValueError("no AgentDefinition effort levels")
    n = len(levels)
    judgment = levels[-1]
    instruction = levels[-2] if n >= 2 else levels[-1]
    if n >= 3:
        mech_idx = n - 3
        if mech_idx == 0:
            mech_idx = 1
        mechanical = levels[mech_idx]
    elif n == 2:
        mechanical = levels[0]
    else:
        mechanical = levels[0]
    return judgment, instruction, mechanical


def role_effort_map(
    ordered_weak_to_strong: list[str] | tuple[str, ...] | None = None,
) -> dict[str, str]:
    judgment, instruction, mechanical = three_tier(
        list(ordered_weak_to_strong or SHIP_TIME_ENUM)
    )
    out: dict[str, str] = {}
    for key in MECHANICAL:
        out[key] = mechanical
    for key in INSTRUCTION:
        out[key] = instruction
    for key in JUDGMENT:
        out[key] = judgment
    return out


def self_check() -> None:
    cases = [
        (["low", "medium", "high", "xhigh", "max"], ("max", "xhigh", "high")),
        (
            ["low", "medium", "high", "xhigh", "max", "ultra"],
            ("ultra", "max", "xhigh"),
        ),
        (["low", "medium", "high"], ("high", "medium", "medium")),
        (["low", "high"], ("high", "low", "low")),
        (["high"], ("high", "high", "high")),
        (
            ["none", "minimal", "low", "medium", "high", "xhigh", "max"],
            ("max", "xhigh", "high"),
        ),
        (
            ["none", "minimal", "low", "medium", "high", "xhigh", "max", "deep"],
            ("max", "xhigh", "high"),
        ),
    ]
    for enum, expected in cases:
        got = three_tier(enum)
        if got != expected:
            raise SystemExit(f"three_tier({enum!r}) = {got!r}, expected {expected!r}")
    mapping = role_effort_map(SHIP_TIME_ENUM)
    if mapping["feature"] != "high" or mapping["bug-fix"] != "xhigh":
        raise SystemExit(f"ship-time map wrong: {mapping}")
    if mapping["how-explainer"] != "max" or mapping["independent-verifier"] != "max":
        raise SystemExit(f"ship-time judgment wrong: {mapping}")
    if len(mapping) != len(MECHANICAL) + len(INSTRUCTION) + len(JUDGMENT):
        raise SystemExit("role count mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enum",
        help="comma-separated weakest→strongest tokens (default: ship-time snapshot)",
    )
    parser.add_argument(
        "--enum-file",
        help="file with one token per line, weakest first",
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
    if args.enum_file:
        text = open(args.enum_file, encoding="utf-8").read()
        levels = [line.strip() for line in text.splitlines() if line.strip()]
    elif args.enum:
        levels = [part.strip() for part in args.enum.split(",") if part.strip()]
    else:
        levels = list(SHIP_TIME_ENUM)
    judgment, instruction, mechanical = three_tier(levels)
    print("enum:", " ".join(filter_agent_definition_levels(levels)))
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
