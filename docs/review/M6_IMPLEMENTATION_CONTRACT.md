# M6 contract-first decision

```text
TASK_ID=PHASE3-M6-CONTRACT-FIRST-V1
M6_STATUS=BLOCKED_CONTRACT
M6_SCOPE=NOT_IMPLEMENTED
M7_SEPARATION=PRESERVED
PROFILE_RESULT_STATUS=NOT_COMPUTED
```

## Decision

The repository does not yet contain enough approved semantics to implement a
deterministic mapping from
`remaining_clear_width_m + profile + evidence + closure` to all four frozen
states. This lane therefore stops before GREEN. It does not add a threshold,
profile binding, state transition, or executable expectation that would make a
new safety decision.

`WIDTH_ONLY_PARTIAL` is also blocked. The available `0.90 m` reference can
support one comparison, but it cannot by itself distinguish `PASS`,
`CONDITIONAL`, and `FAIL`, and it is not bound to a frozen versioned M6 profile.

## Frozen statements that a later RED suite may enforce

| ID | Frozen statement | Authority |
|---|---|---|
| M6-F01 | M6 consumes M7 physical output but M7 does not perform profile evaluation. | `docs/reference/DESIGN.md:43-44`; `AI_TASKS/03_残存幅モデルとQAコード.md:11,32-44` |
| M6-F02 | Missing/UNKNOWN hazard or required evidence cannot become `PASS`; documented UNKNOWN input produces `UNKNOWN`. | `AI_TASKS/03_残存幅モデルとQAコード.md:43`; `docs/reference/DESIGN.md:43,50-52,95` |
| M6-F03 | `official_closure=True` cannot become `PASS`. | Dispatch brief; M7/common-state rule in `docs/reference/DESIGN.md:44` and `AI_TASKS/03_残存幅モデルとQAコード.md:39` |
| M6-F04 | Numeric inputs must reject bool-as-number, negative width, NaN, and infinity. | Dispatch brief; repository fail-closed numeric discipline |
| M6-F05 | Numeric constants used by M6 must be read through `tools.registry.get_constant(..., module="M6")`; `PRESENTATION_ONLY` values cannot be used for computation. | `tools/registry.py:4-18,73-92` |
| M6-F06 | `WIDTH_REQ_WHEELCHAIR_M=0.90 m` is an Italian reference comparator, not Japanese legal compliance. The runtime registry currently classifies it A2/ADAPT, while the ledger says the source value was promoted to A1; this metadata mismatch must be reconciled rather than silently normalized. | `data/constants_registry.yaml:86-93`; `docs/reference/RESEARCH_LEDGER.md:131-133,146-152`; `docs/reference/DESIGN.md:245` |
| M6-F07 | Exact equality must be explicitly tested once its expected state is approved; changing `>=` to `>` must be mutation-detectable. | `docs/reference/DESIGN.md:92-95`; `AI_TASKS/03_残存幅モデルとQAコード.md:47` |
| M6-F08 | Inputs must not be mutated and output must be deterministic with a closed schema. | Dispatch brief and repository determinism/safety contract |

These statements are necessary but not sufficient to implement the evaluator.

## RED contract matrix

The following is the test-first handoff. `FROZEN` rows can be encoded after the
schema is approved. `BLOCKED` rows cannot receive an expected four-state value
without a human contract decision.

| Case | Expected invariant or unresolved question | Status |
|---|---|---|
| hazard/evidence status is explicitly UNKNOWN | state must be `UNKNOWN`, never `PASS` | FROZEN |
| required input is absent | fail closed; exact error-vs-UNKNOWN policy and reason code are not frozen | BLOCKED |
| `official_closure=True` | result must not be `PASS`; `FAIL` vs `UNKNOWN` precedence is not frozen | BLOCKED |
| `official_closure=False` | false alone must not prove accessibility; remaining evidence rules are not frozen | BLOCKED |
| `official_closure=None` | meaning of “not supplied” vs “unknown” and its reason code are not frozen | BLOCKED |
| remaining width is below required width | width comparison is known; resulting `FAIL` vs `CONDITIONAL` rule is not frozen | BLOCKED |
| remaining width equals required width | exact `PASS`/`CONDITIONAL`/`FAIL` state is not frozen | BLOCKED |
| remaining width exceeds required width | evidence/closure may still prevent `PASS`; sufficiency rule is not frozen | BLOCKED |
| remaining width is `True`/`False`, negative, NaN, or infinity | reject | FROZEN |
| profile or evidence has an extra/missing key | reject under a closed schema, but the exact schema is not frozen | BLOCKED |
| registry lookup is bypassed | mutation must fail | FROZEN |
| UNKNOWN is mutated to PASS | mutation must fail | FROZEN |
| equality comparator is mutated `>=` to `>` | mutation must fail after equality state is approved | BLOCKED |
| closure gate is bypassed | mutation must fail after closure precedence is approved | BLOCKED |

No executable RED test is added in this blocked lane: encoding an unresolved
expected state, field set, or reason code would silently turn a question into
policy and would leave the branch intentionally failing the repository-wide
acceptance gate.

## Blocking contract gaps

1. No M6-enabled, versioned profile catalogue binds a profile ID to
   `required_width_m`, its unit, allowed transfer, and evidence version.
2. No approved rule distinguishes `PASS`, `CONDITIONAL`, and `FAIL` for the
   width-only comparator. In particular, exact equality is unresolved.
3. The four evidence axes are defined for traceability, but M6 sufficiency and
   precedence rules by `authority_scope` are not defined. The documented
   `evidence_policy_v0` weights and expiry are product assumptions, not an
   approved M6 state-transition contract.
4. Closure is tri-state, but the precedence of `True`, `False`, and `None`
   against unknown/stale evidence and physical width is not frozen.
5. The exact input schema, exact output schema, reason-code vocabulary,
   profile-version field, and provenance surface are not frozen.
6. Required widths for current non-wheelchair profiles are absent. Ohtsu values
   are ASSISTED-only speeds and do not establish width thresholds.
7. The runtime registry labels the `0.90 m` entry `evidence_status: A2` while the
   ledger says the source value is A1-promoted. The runtime entry remains the
   computational authority, but the provenance metadata needs human
   reconciliation before GREEN.

## Human gate required before GREEN

- Approve the first M6 profile catalogue and registry bindings.
- Define the complete state table, including exact equality and closure/evidence
  precedence.
- Define per-attribute evidence sufficiency and stale/expired behavior.
- Freeze exact schemas, reason codes, profile version, and provenance fields.
- Approve the RED expectations before implementation.
- Reconcile the ledger A1 statement with the registry A2/ADAPT metadata without
  changing the numeric value or weakening its non-Japanese-reference wording.
- Decide whether applicable Japanese primary-source rules are a prerequisite
  for every M6 computation or only for Japanese-compliance language, then
  A1-verify and register them as required. Existing Phase 2 reporting treats
  this as a general M6 gate, while the registry permits `0.90 m` only as an
  A2/ADAPT non-Japanese reference; narrowing that gate requires human approval.

Until those decisions are approved, selectors remain disabled, profile output
remains `NOT_COMPUTED`, and dependent KPI values remain `null` with a non-empty
reason. This status is not evidence that a route is accessible or inaccessible.
