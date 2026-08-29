# Proposal: integration collect-only diagnostic

Proposal ID: `integration-collect-first-v1`
Status: current-run diagnostic only; permanent promotion requires human review

## Observed failure

Individually green city lanes contained same-named pytest modules. Their first joint collection produced an import-file-mismatch failure. The failure was packaging/collection-specific and occurred before behavioral tests could run.

## Bounded change

For integrations that combine multiple Python test roots, run the existing city/integration `--collect-only` command before the unchanged full test suite. The diagnostic may fail earlier with a smaller surface, but it never replaces any acceptance, safety, mutation, or full-regression gate.

## Fixed replay result

- Champion full-suite-first median detection: 3.022530 seconds.
- Challenger collect-only-first median detection: 1.063199 seconds.
- Both strategies matched the expected failure fingerprint in 2/2 attempts.
- The unchanged full suite passed with 314 tests after every replay repair (4/4).

This was one fixed Windows replay, with champion attempts run first. Cache/order bias is not excluded, and the result is not a general performance claim.

## Decision

The challenger was used only as an extra non-safety diagnostic during this run. Permanent reuse remains blocked on human review and two reproducible evaluations under the repository policy.

Evidence: `champion_score.json`, `challenger_score.json`, `safety_gate_report.json`, `reproducibility_report.json`, and the immutable evaluator artifacts under `evals/immutable/` and `orchestration/evals/`.
