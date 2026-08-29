# Rollback: integration-collect-first-v1

The candidate changes no product code, test expectation, protected contract, or permanent default. Rollback therefore means:

1. Stop invoking the optional integration `--collect-only` diagnostic.
2. Use `champion-v1`: run the unchanged full suite as the first integration diagnostic.
3. Keep the mandatory full suite, trust-boundary scan, protected-blob checks, and all acceptance gates unchanged.
4. Mark the candidate rejected or expired in orchestration memory; do not delete its audit evidence.

Rollback does not require a main/tag change, dependency change, or weakening of any test. If a future permanent-promotion commit exists, revert only that reviewed strategy/config commit and rerun the full suite.
