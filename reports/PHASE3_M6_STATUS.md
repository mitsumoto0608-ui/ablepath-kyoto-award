# Phase 3 M6 status

```text
LANE_ID=M6
LANE_STATUS=BLOCKED_CONTRACT
BASE_SHA=372ce8ec37dcc2a263bd6ae28e565f9c03ed9673
HEAD_SHA=dd2000714e0e4d385a5c9a345ce9b8ea3dd191dd
HEAD_SHA_SEMANTICS=PRE_ATTESTATION_CONTENT_HEAD
ALLOWED_PATHS_AUDIT=PASS
HOSTED_CI=SUCCESS
HOSTED_RUN_URL=https://github.com/mitsumoto0608-ui/ablepath-kyoto-award/actions/runs/33330973039
INTEGRATION_RECOMMENDATION=REPORT_ONLY
HUMAN_GATES=[PROFILE_CATALOGUE_AND_REGISTRY_BINDING,FOUR_STATE_TABLE_WITH_EQUALITY,EVIDENCE_SUFFICIENCY_AND_STALENESS,CLOSURE_PRECEDENCE,EXACT_SCHEMAS_REASON_CODES_PROFILE_VERSION_PROVENANCE,JAPANESE_SOURCE_AND_REGISTRY_RECONCILIATION,RED_EXPECTATIONS,HUMAN_MERGE_REVIEW]
```

`HEAD_SHA` identifies the reviewed content commit containing the contract,
workflow, and handoff. This tracked report is a subsequent report-only
attestation commit and cannot embed its own Git SHA. CONTROL must resolve that
final attestation commit from the feature-branch tip and check its automatic CI
separately.

```text
TASK_ID=PHASE3-M6-CONTRACT-FIRST-V1
M6_STATUS=BLOCKED_CONTRACT
M6_SCOPE=NOT_IMPLEMENTED
M6_CONNECTED=false
PROFILE_SELECTOR_ENABLED=false
PROFILE_RESULT_STATUS=NOT_COMPUTED
M7_CHANGED=false
```

The contract-first review found that the repository can freeze several
fail-closed invariants, but cannot yet produce all four profile states without
inventing policy. `WIDTH_ONLY_PARTIAL` is not implemented because the available
`0.90 m` reference neither defines `CONDITIONAL` nor binds itself to an approved
versioned profile catalogue.

The decision, source trace, RED matrix, blockers, and human gate are recorded in
`docs/review/M6_IMPLEMENTATION_CONTRACT.md`. No runtime code, threshold,
registry value, M7 behavior, selector state, runner output, or KPI was changed.

## Independent review

- LUNA independently returned `BLOCKED_CONTRACT`: the width reference is
  computable, but equality, `CONDITIONAL`, evidence sufficiency/precedence,
  tri-state closure precedence, and versioned profile binding are not frozen.
- TERA independently returned `BLOCKED_CONTRACT`: safe invariants can be listed,
  but executable state expectations, exact schema, strong closure/equality
  mutations, reason codes, provenance shape, and profile version would invent
  policy.
- The agents did not disagree on the outcome. TERA identified one wording
  nuance adopted by MAIN: whether Japanese primary-source rules gate every M6
  computation or only compliance claims remains a human decision because the
  Phase 2 report and registry framing are not identical.

MAIN accepts both reviews and keeps the lane documentation-only.

## Verification

- Full Python suite: `499 passed, 1 warning` on the specified base worktree.
- New/updated executable tests: none; unresolved expected states were not
  encoded as policy.
- Runner run 1: `120 runs`; `all_runs.json` SHA-256
  `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
- Runner run 2: `120 runs`; `all_runs.json` SHA-256
  `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`.
- Generated `results/all_runs.json` and `results/summary.md` were byte-logically
  identical to HEAD after Git filters; the checkout representation was restored
  after evidence capture and neither file is part of this lane diff.
- Frozen `src/allocate.py` SHA-256:
  `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`
  (`MATCH=true`).
- Hosted CI for the content commit: SUCCESS. Linux Python, Windows newline and
  determinism, and static viewer/Node jobs all passed in run
  `33330973039`.
- Mutation execution: not applicable in the blocked lane. The prospective
  mutation gates are recorded in the RED matrix.

## Completion protocol audit

```text
BRANCH=task/phase3-m6-contract-v1
WORKTREE_CLEAN=true
FEATURE_BRANCH_PUSHED=true
FORCE_PUSHED=false
MAIN_CHANGED=false
TAG_CHANGED=false
INTEGRATION_983476E_CHANGED=false
M7_CHANGED=false
ALLOCATE_CHANGED=false
CONSTANTS_REGISTRY_CHANGED=false
```

Exact changed files from base through the final report attestation:

1. `AI_TASKS/06_M6_CONTRACT_FIRST.md`
2. `docs/review/M6_IMPLEMENTATION_CONTRACT.md`
3. `docs/review/M6_WORKFLOW.md`
4. `reports/PHASE3_M6_STATUS.md`

All four paths are inside the dispatch brief's allowed paths. No `src/m6/`,
`tests/m6/`, M7, allocation, registry, data, schema, viewer, generated result,
main, tag, or integration-branch file is changed.

Protected-ref evidence before and after the lane content commit:

- local `main` and `origin/main`:
  `112dbe9047d803528ee50dab284f6570de937583` unchanged;
- `v0.2.0-baseline` target:
  `0c3289b9174bf624c95faeaa3c1643664e31c2eb` unchanged;
- local `integration/realdata-model-map-v1`:
  `983476e323f1bd03005cc9ac6466e32d6f102aea` unchanged.

The M6 lane is based on `372ce8e`, not on the integration commit. No claim is
made that `origin/integration/realdata-model-map-v1` points at `983476e`.

## Source, class, license, and UNKNOWN truth

- Source: no new external source or data was added. The existing `0.90 m`
  comparator remains an Italian reference only. The runtime registry labels it
  A2/ADAPT while the ledger says A1-promoted; this mismatch remains a human
  reconciliation gate. No Japanese-compliance source was approved here.
- Class: this is a documentation-only `BLOCKED_CONTRACT` lane. M6 remains
  `NOT_IMPLEMENTED` / `NOT_COMPUTED`; no city, geometry, evidence, hazard, or
  accessibility class was promoted.
- License: no third-party code or data was added. Root-license selection and
  public-distribution authorization remain unresolved/false; this lane does not
  close a release gate.
- UNKNOWN: preserved. No UNKNOWN value becomes PASS or OPEN. The profile
  selector stays disabled, and M6-dependent KPI values remain `null` with a
  non-empty reason.

## Limited self-improvement record

No scientific equation, numeric constant, evidence class, UNKNOWN semantics,
official-data interpretation, expected value, human gate, or protected ref was
changed. Improvements are limited to command order, environment selection,
review order, and checkpoint discipline.

### Lesson M6-L1 — pytest runtime selection

- OBSERVE: command=`python -m pytest tests/ -q`; exit=1; stdout=empty;
  stderr=`No module named pytest`; changed files=none; elapsed=7.02s;
  environment=Windows, uv-managed CPython 3.12 selected outside the project
  venv.
- FINGERPRINT: `ENV|PYTEST_MODULE_MISSING|DEFAULT_PYTHON`.
- RETRIEVE: the Phase 2 autonomous report's isolated-worktree/runtime lessons
  and the existing Hosted-CI locked-environment workflow were consulted.
- DIAGNOSE: `ENVIRONMENT`, not product code or contract.
- PLAN: primary=use the known project venv; fallback=Hosted CI; allowed
  paths=none; rollback=no file action.
- CHECKPOINT: documentation diff unchanged and no generated output present.
- ACT: invoked pytest through the project venv under the approved boundary.
- TARGETED TEST: the project venv launched pytest successfully. LANE TEST: no
  executable `tests/m6/` exists because the contract is blocked, so the full
  repository suite is the narrowest executable acceptance test. FULL TEST:
  `499 passed, 1 warning`.
- REFLECT: discover the project venv before the first pytest invocation in a new
  worktree. Do not retry the same missing-module command.
- PERSIST: recorded as `M6-L1` in this lane report.

### Lesson M6-L2 — Windows generated-output representation

- OBSERVE: command=project-venv `python -m src.runner data/` twice; exits=0/0;
  stdout=`OK: 120 runs` twice; stderr=the existing
  `plaza_status_gating=false` warning; changed files reported by status=
  `results/all_runs.json` and `results/summary.md`; elapsed=23.02s/19.76s;
  environment=Windows, project CPython 3.14 venv, `core.autocrlf=true`, runner
  output LF. Both output SHA values matched the expected baseline and filtered
  `git diff --quiet` exited 0.
- FINGERPRINT: `GIT_PLATFORM|RUNNER_LF_VS_CHECKOUT_CRLF|HASH_IDENTICAL`.
- RETRIEVE: the Phase 2 report's hash-bound CRLF checkout-drift lesson and the
  Windows newline Hosted-CI gate were consulted.
- DIAGNOSE: `GIT` / `PLATFORM`, not data nondeterminism.
- PLAN: primary=preserve SHA/diff evidence then restore only the two checkout
  representations; fallback=Windows Hosted-CI newline job; allowed paths=
  ephemeral `results/all_runs.json` and `results/summary.md`; rollback=
  `git restore --worktree` for only those runner-owned files.
- CHECKPOINT: reviewed content was staged separately; generated files were not
  staged.
- ACT: restored the two checkout representations after evidence capture.
- TARGETED TEST: generated-output diff cleared. LANE TEST: runner completed 120
  runs twice with identical expected SHA. FULL TEST: local `499 passed` and the
  hosted Windows/Linux quality gates passed.
- REFLECT: on Windows, capture both hashes and filtered diff evidence before
  restoring generated outputs; do not misclassify newline representation as a
  deterministic-output failure.
- PERSIST: recorded as `M6-L2` in this lane report.

### Lesson M6-L3 — addendum-aware pre-commit review

- OBSERVE: command/event=independent read-only pre-commit documentation review;
  result=BLOCK; stdout-equivalent=Critical 0, High 2, Medium 1, Low 0;
  stderr=none; changed files under review=the three M6 content Markdown files;
  elapsed=not emitted by the sub-agent runner; environment=isolated read-only
  review packet. Findings were stale “push outside workflow” wording,
  conditional runner/SHA wording, and a registry-A2 versus ledger-A1 metadata
  mismatch.
- FINGERPRINT: `CONTRACT|COMPLETION_ADDENDUM_NOT_REFLECTED_IN_WORKFLOW`.
- RETRIEVE: the completion addendum, prior Phase 2 M6 blocked report, and public
  release gate were consulted.
- DIAGNOSE: `CONTRACT` documentation drift.
- PLAN: primary=update only the M6 workflow/contract documentation then
  re-review; fallback=stop without commit; allowed paths=the three M6 content
  Markdown files; rollback=reverse only the documentation patch.
- CHECKPOINT: no content commit existed and all science/runtime files were
  unchanged.
- ACT: corrected push/runner requirements and exposed the metadata mismatch as
  a human gate.
- TARGETED TEST: final pre-commit review returned Critical 0, High 0, Medium 0,
  Low 0, PASS. LANE TEST: allowed-path and frozen-file diffs passed. FULL TEST:
  `499 passed, 1 warning`; Hosted CI later passed all three jobs.
- REFLECT: apply completion-protocol deltas before staging and code review, not
  after the first commit.
- PERSIST: recorded as `M6-L3` in this lane report.

No fingerprint exceeded three attempts, and no identical failed fix was
repeated.
