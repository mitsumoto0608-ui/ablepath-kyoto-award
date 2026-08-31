# Phase 2 M6 status

`M6_STATUS=BLOCKED_CONTRACT`

`M6_CONNECTED=false`

`PROFILE_SELECTOR_ENABLED=false`

`PROFILE_RESULT_STATUS=NOT_COMPUTED`

## Decision

M6 was reviewed contract-first and was not implemented. The current design and
registry do not define enough information to produce the frozen four-state
vocabulary without inventing a safety boundary.

## What is available

- `remaining_clear_width_m` is a profile-independent M7 physical output.
- `official_closure=True` must never produce `PASS`.
- missing or `UNKNOWN` evidence/hazard data must produce `UNKNOWN`, never
  `PASS` or an open-route claim.
- `WIDTH_REQ_WHEELCHAIR_M=0.90 m` is retrievable only with `module="M6"`.
  Its registry status is `A2` / `ADAPT`; it is an Italian reference value and
  must not be presented as Japanese legal compliance.

## Contract gaps that block implementation

1. The M6-enabled versioned profile set and its `required_width_m` binding are
   not frozen. Existing `data/profiles.csv` supplies profile IDs, but it does
   not carry a required-width field or a width-evidence version.
2. The repository does not define the numerical meaning of `CONDITIONAL` for
   the width-only comparison. Treating equality as `PASS`, `CONDITIONAL`, or
   `FAIL` would be a new safety decision.
3. Required widths for the current non-wheelchair profiles are absent from the
   registry. Ohtsu speed values are ASSISTED-only and do not establish width
   thresholds.
4. The exact M6 input/output schema, reason-code vocabulary, profile version,
   and provenance surface are not frozen.
5. The original Japanese accessibility standard remains an A1 acquisition and
   human-review requirement before any Japanese-compliance wording can be used.

## Required human/A1 gate

- verify and register the applicable Japanese primary-source width rules;
- approve the versioned profile catalogue and allowed transfers;
- define exact `PASS` / `CONDITIONAL` / `FAIL` boundaries, including equality;
- freeze missing-input, closure, and hazard reason codes plus exact schema;
- approve the RED test expectations before implementation.

Until that gate is complete, the viewer must keep the profile selector disabled
and return `NOT_COMPUTED`. KPI readiness that depends on M6 remains `null` with
a non-empty reason. No profile state is inferred from M7, OSM, PLATEAU, a map
overlay, or a Hokonavi rank.

This blocked result is not evidence that any route is accessible or
inaccessible, and it is not an administrative or legal validation.
