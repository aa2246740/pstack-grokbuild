### Feature

**You own the design. Plan, review, verify.** Delegate implementation; stay in the lead.

1. `how` over the affected subsystem.
2. `architect` for parallel design exploration. Skipping stays as `architect skipped: <reason>`; do not fold the design decision silently into implementation.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target (the **separate-before-serializing-shared-state** principle skill). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. Delegate code-writing with parent-session `task` (`subagent_type: "feature"`, `model` from toml key `feature` per `skills/setup-pstack/references/resolve-model.md`; no toml: send `grok-4.6` (omit if rejected); inherit-parent or `auto` or missing key: omit `model`; effort per `skills/setup-pstack/references/resolve-effort.md`, never send `reasoning_effort` on `task`) and a specific scope (file paths, named data shape and its organizing structure per **principle-model-the-domain** — a state machine over scattered booleans, a table/registry over branching, a typed model over repeated shape assumptions, chosen before the delegate writes logic — and success criteria). Review its diff yourself. Grok Build `MAX_SUBAGENT_DEPTH` is 1, so this parent owns every spawn. The child does not call `task`. When the implementation admits multiple valid shapes, parent-spawn **arena** instead. Independent verify is a second parent `task` with `subagent_type: "independent-verifier"`, toml key `independent-verifier` (no toml: `grok-4.6`; omit `model` when inherit-parent/`auto`/missing key; send it when the toml names a detected slug different from the writer), and `isolation: "worktree"` when the writer still holds the tree. Mandatory: no skip-with-reason escape, and Laziness Protocol does not override it (the gain is review separation, not lines saved). Comments per **Comments**. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit liberally.
5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass; flag it.
6. Rebase into small, ordered commits; stack follow-ups.
   Use the **sequence-verifiable-units** principle skill, building, verifying, and committing each small unit before the next.
7. If the design is contested, `interrogate` before shipping.
8. Run **Opening a PR**.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline; that owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries; spawn a fresh owner rather than chaining interrupts.

**Reply:** what you built, what you chose and why, open decisions. Tables for design alternatives.
