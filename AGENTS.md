# AblePath agent map

## Mission and truth boundary

AblePath evaluates evidence-backed walking-graph constraints for Kyoto Kiyomizu, Kyoto Arashiyama, and Fujisawa Enoshima. It is `PARTIAL_COMPLETE`: default geometry is `SYNTHETIC_DEMO`; Kiyomizu alone has an explicit opt-in, source-traceable real-coordinate `CANDIDATE` viewer. It is not a safety guarantee, model result, M6/M7 result, or administrative validation. Missing KPI evidence is `null` with a reason; M6 is `NOT_COMPUTED`.

## Before editing

Read `README.md`, `docs/reference/DESIGN.md`, the assigned `AI_TASKS/` brief, and relevant `docs/reference/RESEARCH_LEDGER.md`. Keep work on the assigned task branch; never merge, tag, release, or push without the assigned authority.

## Non-negotiable safety contract

- `src/allocate.py` is frozen. Do not weaken dense edge states, `fire_safe`, uniqueness/referential checks, negative-value rejection, synthetic inspection, `plaza_status_gating`, or `--forbid-synthetic`.
- Preserve `PASS` / `CONDITIONAL` / `FAIL` / `UNKNOWN`; never turn `UNKNOWN` into pass/open.
- Numeric external evidence requires A1 registry review. Do not hard-code it or use web/AI summaries as values.
- Use only staged external inputs and never add Dropbox absolute paths, Kyoto road-ledger values, or disguised synthetic data.
- Do not describe an output as a “safe evacuation route,” a prediction, or people saved.

## Minimal sufficient engineering

Default to one writer. Add a sub-agent only for independent audit, isolated read-only research, or a proven critical-path reduction; never use delegation merely to select a model. Keep no unneeded framework, wrapper, adapter, configuration layer, or future extension. The default feature test budget is one normal path plus one fatal failure; scientific, UNKNOWN, provenance, security, and determinism changes need a recorded reason for more. If tests outweigh the implementation, record `OVERDESIGN_REVIEW` rather than silently deleting them.

Details and receipts: `docs/operations/MINIMAL_SUFFICIENT_ENGINEERING.md`.

## Validation and handoff

Write tests first. Python test docstrings begin with a listed test-class label. Run the relevant targeted tests and always run `python -m pytest tests/ -q` for acceptance; if the environment cannot run it, the acceptance result is blocked/unverified, never optional. Preserve deterministic runner/SHA checks when a change can affect outputs. Report changed files, decisions, tests, mutation relevance, SHA results where applicable, unresolved issues, and human gates. Formula/unit/state/privacy/security changes require human review before merge.
