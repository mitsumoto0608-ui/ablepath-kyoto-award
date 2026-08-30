# Phase 3 HOKO lane status

LANE_ID=HOKO
LANE_STATUS=BLOCKED_CONTRACT
BASE_SHA=372ce8ec37dcc2a263bd6ae28e565f9c03ed9673
HEAD_SHA=PENDING_IMPLEMENTATION_COMMIT
ALLOWED_PATHS_AUDIT=PASS
HOSTED_CI=NOT_RUN
HOSTED_RUN_URL=null
INTEGRATION_RECOMMENDATION=REPORT_ONLY
HUMAN_GATES=["exact sidecar v1 shape", "state/CRS/unit/test expectations", "mapping-contract review required by AI_TASKS/05"]

`HOKONAVI_ADAPTER_PROTOTYPE=true`

This lane provides a deterministic mapping prototype limited to the tracked
`SYNTHETIC` fixture. It does not ingest a ministry dataset, connect M6/M7 to
the runner or UI, certify data exchange, or validate an administrative
workflow. The exact sidecar shape added here is a reviewable proposal; the
brief requires human review of that contract before integration, so the lane
remains `BLOCKED_CONTRACT` and must be used as `REPORT_ONLY`.

## Verification record

- Specification: Ministry of Land, Infrastructure, Transport and Tourism,
  *Pedestrian Space Network Data Development Specification*, July 2024,
  <https://www.mlit.go.jp/sogoseisaku/soukou/content/001757259.pdf>. The
  official landing page was checked on 2026-08-31 and did not identify a newer
  network specification.
- Mapping inventory: 40 fields = FULL 10, PARTIAL 18, SIDECAR_REQUIRED 10,
  UNMAPPED 1, NOT_APPLICABLE 1.
- Synthetic fixture: 5 nodes and 5 links. The source fixture was unchanged;
  `expected_internal.json` was updated to the exact deterministic prototype
  output and is asserted byte-semantically by the adapter tests.
- Targeted/lane tests: `55 passed` (latest combined old/new HOKO contract run:
  `81 passed in 2.83s`).
- Full tests: `554 passed, 1 warning in 115.09s`.
- Runner run 1: `120 runs`; `all_runs.json` SHA-256
  `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
- Runner run 2: `120 runs`; `all_runs.json` SHA-256
  `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
- `src/allocate.py` SHA-256:
  `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`.
  The file was not changed.
- Mutation results: all six injected faults were killed: removal of an exact
  loss ID; direction code `99` mapped to a known direction; ascending and
  descending slope classes swapped; width class substituted for `w_min`; and
  UNKNOWN M7 width replaced with zero; plus a sparse `link2_id` silently
  renumbered to `link1_id`. Each mutation was reverted or fixed before the
  green runs.
- Static/M7 width separation: `clear_width_static_m` is derived only from
  `w_min`, in metres at 0.1 m source resolution. M7
  `remaining_clear_width_m` is accepted only in the AblePath sidecar and never
  overwrites the static field.
- Code `99` / semantic blank / missing: retained as distinct provenance kinds
  (`SOURCE_CODE_99`, `SEMANTIC_BLANK`, `MISSING_ATTRIBUTE`). None becomes zero,
  false, OPEN, PASS, or another known state.
- `maint_date`: retained exactly as the source update date and not interpreted
  as an observation-validity interval.
- Sidecar validation: exact-key validation, schema identity/version,
  edge-reference integrity, sorted unique multi-record keys, separate
  computation/state fields, provenance, finite/non-negative width checks, and
  fail-closed UNKNOWN/not-computed cross-field rules are enforced. Export with
  sidecar disabled rejects information rather than dropping it.
- Revision protection: local ref `integration/realdata-model-map-v1` remains
  `983476e323f1bd03005cc9ac6466e32d6f102aea`; that commit series was not
  changed.
- Main/tag protection: local and origin `main` both remain
  `112dbe9047d803528ee50dab284f6570de937583`; tag
  `v0.2.0-baseline` remains
  `0c3289b9174bf624c95faeaa3c1643664e31c2eb`. No main or tag update was made.

## Exact changed files

1. `docs/data/HOKONAVI_2024_INFORMATION_LOSS.md`
2. `docs/data/HOKONAVI_2024_MAPPING.md`
3. `reports/PHASE3_HOKONAVI_STATUS.md`
4. `schemas/hokonavi_2024_mapping.yaml`
5. `schemas/hokonavi_2024_sidecar.schema.json`
6. `src/hokonavi/__init__.py`
7. `src/hokonavi/adapter.py`
8. `tests/fixtures/hokonavi_2024/expected_internal.json`
9. `tests/hokonavi/test_adapter.py`

## Source, class, license, and UNKNOWN truth

- Source/class: only the tracked, explicitly marked `SYNTHETIC` fixture is
  consumed. REAL input is rejected by this prototype.
- License: no external or real dataset was downloaded, copied, or relicensed
  by this lane. The official page/PDF is referenced only as specification
  context.
- UNKNOWN: code 99, semantic blank, and missing attribute remain distinguishable
  and are not converted into a known availability, closure, profile, scenario,
  or safety result.

## Contract blocker and human decision table

| Decision required | Evidence available | Missing authority | Safe lane action |
|---|---|---|---|
| Accept exact AblePath sidecar v1 shape | brief field families, mapping and loss contracts, schema, runtime semantic validator, tests | recorded human approval required by AI_TASKS/05, including edge-keyed observation/evidence associations and schema/runtime acceptance surface | keep BLOCKED_CONTRACT |
| Accept CRS/axis/unit/state expectations | July 2024 contract notes and synthetic round-trip tests | human/Fable review of contract interpretation | do not integrate automatically |
| Permit integration of prototype | full local verification and independent audits | human merge gate for state/safety semantics | REPORT_ONLY until approved |

No missing contract item was filled with real-data, license, provenance, or
administrative claims.

## Limited self-improvement lesson

1. OBSERVE: the default Python and bundled Python lacked `pytest`; an offline
   dependency attempt lacked cached packages; the first full-test attempts used
   an unwritable default temp root or lost the long-running session handle.
2. FINGERPRINT: `PYTEST_ENV_MISSING`,
   `PYTEST_DEFAULT_BASETEMP_PERMISSION_DENIED`, and
   `LONG_PYTEST_SESSION_HANDLE_LOST`, excluding machine paths and timestamps.
3. RETRIEVE: consulted up to three repository playbook lessons: collect before
   full execution, use a unique external/test-local basetemp, and distinguish a
   completed test from a post-result process stall.
4. DIAGNOSE: ENVIRONMENT/PLATFORM, not CODE, DATA, or scientific CONTRACT.
5. PLAN: primary fix was a temporary isolated `uv` environment plus
   `-p no:cacheprovider` and an explicit basetemp; fallback was the already
   created temporary virtual environment. Allowed repository writes remained
   the lane paths; rollback removed test temp/cache directories and restored
   runner-generated tracked outputs to their pre-run HEAD bytes.
6. CHECKPOINT: verified branch, base, status, and exact generated-file diff
   before each retry.
7. ACT: captured the returned session ID and polled that exact session.
8. TARGETED TEST: adapter suite passed.
9. LANE TEST: all 55 HOKO adapter tests passed; the combined old/new HOKO
   contracts passed 81 tests.
10. FULL TEST: all 554 repository tests passed.
11. REFLECT: the diagnosis was correct; repeated offline resolution and a
    quoted compound `-k` expression were wasted work. Next time, reuse the
    verified temporary environment, use one `-k` token, allocate basetemp at
    the first run, and retain the session handle immediately.
12. PERSIST: this lesson is recorded only in this lane report; no shared memory
    file was edited.

## Independent review

- LUNA/Goodall: contract/evidence review; found the exact sidecar to require
  human approval and confirmed the bounded synthetic-only/provenance posture.
- TERA/Linnaeus: tests/invariants/mutation review; identified link-column order
  and sparse-column loss, existing-fixture divergence, and
  multi-record/cross-field risks. Sparse columns are now rejected and the
  tracked internal fixture is an exact implementation oracle.
- Main decision: retain a useful, fail-closed prototype and report it as
  `BLOCKED_CONTRACT` rather than infer missing approval.
- Agent disagreement: none on the blocker or integration recommendation.
