# M6 contract-first workflow

Goal:
Implement the smallest M6 profile-evaluation contract that remains strictly
separate from M7 physics, or stop at `BLOCKED_CONTRACT` if the existing
authoritative sources cannot freeze every safety-relevant decision.

Success criteria:
- Inputs remain `remaining_clear_width_m`, profile, evidence, and closure.
- Outputs use only `PASS`, `CONDITIONAL`, `FAIL`, and `UNKNOWN`.
- Missing or unknown inputs never become `PASS`.
- `official_closure=True` never becomes `PASS`.
- Constants are obtained through the registry and M7 is unchanged.
- Exact-boundary, invalid-number, exact-schema, provenance, reason-code, and
  mutation-sensitive RED contracts are recorded before implementation.
- If `CONDITIONAL` or evidence/closure precedence is not already frozen, the
  lane stops at `BLOCKED_CONTRACT` without inventing a threshold.

Current context:
- Task: `PHASE3-M6-CONTRACT-FIRST-V1`.
- Base: `372ce8ec37dcc2a263bd6ae28e565f9c03ed9673`.
- Branch: `task/phase3-m6-contract-v1`.
- Scope is limited to the paths listed in the dispatch brief.

Constraints:
- Do not change M7, `src/allocate.py`, or existing registry values.
- Follow test-first discipline and preserve all frozen safety contracts.
- Numeric, unit, state-transition, and safety-boundary decisions require a
  human review gate before merge.

Risks:
- A single required-width constant may be insufficient to distinguish three
  non-UNKNOWN states without an invented `CONDITIONAL` rule.
- Evidence is specified as four orthogonal axes; no precedence or sufficiency
  rule may yet be frozen for M6.
- Closure has tri-state semantics and must fail closed when unknown.

Approval required:
- No destructive action is planned. The only planned external action is a
  non-force push of
  `task/phase3-m6-contract-v1` so Hosted CI and the lane report can serve as the
  CONTROL handoff surface.
- Merge, main/tag changes, force-push, and integration-branch changes remain
  outside this workflow and require a separate human gate.

Work packets:
- LUNA: independent design/evidence/wording/registry contract audit (read-only).
- TERA: independent RED-test, boundary, invalid-input, determinism, and mutation
  audit (read-only).
- MAIN: integrate authoritative findings and own all file edits.

Integration policy:
Accept only rules traceable to repository authorities. Record conflicts and
missing decisions explicitly. Do not convert ambiguity into a default.

Verification:
Run narrow M6 tests if present, then the full Python suite. Run the deterministic
runner twice and record both `all_runs.json` SHA-256 values plus the frozen
`src/allocate.py` SHA-256 even when the lane is BLOCKED and documentation-only.
Audit allowed paths, source/class/license/UNKNOWN truth, unchanged integration
commit `983476e`, unchanged main/tag refs, feature-branch push, and Hosted CI.

Reusable artifacts:
The contract/status review files under `docs/review/` and `reports/` are the
handoff for a later GREEN lane after the human gate.
