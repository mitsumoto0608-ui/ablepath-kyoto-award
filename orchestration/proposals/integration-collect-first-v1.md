# Proposal: integration collect-only gate before the full suite

- Proposal ID: `integration-collect-first-v1`
- Status: shadow evaluation only; permanent adoption requires human review.
- Observed problem: separately green city lanes introduced same-named pytest modules that collided only after integration.
- Strategy delta: after integrating multiple test roots, run a narrow `--collect-only` gate before the unchanged full suite.
- Expected benefit: detect packaging/collection failures sooner and with a smaller diagnostic surface.
- Primary metric: median failure-detection wall time on the fixed collision replay.
- Risk: a narrow gate cannot replace behavioral or full regression tests.
- Mitigation: the full test suite remains an immutable hard gate after repair.
- Rollback: return to `champion-v1` ordering.
- Protected boundaries: scientific equations, evidence classes, `UNKNOWN` semantics, expected values, main/tag protection, and test coverage are unchanged.
