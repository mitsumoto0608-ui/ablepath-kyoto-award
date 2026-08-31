# Phase 3 global report authority

This index separates current Phase 3 evidence from retained historical snapshots. A historical file may remain useful evidence, but its commit counts, PR number, Hosted run, capability count, or release values must not be presented as the current Phase 3 state.

## CURRENT_AUTHORITATIVE

- `reports/PHASE2_AUTONOMOUS_REALDATA_REPORT.md`: current reviewed Phase 2 engineering/capability narrative.
- `reports/COMPLETION_LEVELS.json`: current global capability flags with artifact/viewer/model scope separation.
- `reports/KNOWN_GAPS.md`: current product, data, operations, and human-gate gaps.
- `reports/ENVIRONMENT_MANIFEST.json`: current PR #2 reviewed-checkpoint and Hosted-run environment snapshot; the truth-sync feature-run fields remain pending until push.
- `reports/PUBLIC_RELEASE_GATE.md`: current public-release blockers; `PUBLIC_RELEASE_READY=false`.
- `reports/PHASE3_MAP_UI_STATUS.md`: MAP implementation, scoped viewer capability, provenance, fallback, and contract-resolution evidence.
- PR #2 (`integration/realdata-model-map-v1` → `main`): draft technical review vehicle at head `1a62a55b1ff6bd047b433bfd594b0c30e91f9f0d`; pull-request run `33330312591` succeeded.
- PR #3 (`integration/phase3-parallel-v1` → `integration/realdata-model-map-v1`): stacked draft Phase 3 review vehicle. After final verification, its body must record the exact final head, Hosted run, screenshot artifact, deterministic RC SHA, and report-only lanes without changing repository files.
- RC root `RELEASE_MANIFEST.json`: exists inside each generated deterministic RC ZIP, not as a tracked checkout-root file. Its `source_commit` and payload checksums are authoritative only for that archive.
- `cities/kyoto_kiyomizu/realdata/artifact_manifest.v2.json`: hash-bound authority for retained/normalized Kiyomizu real VGI artifacts.
- `cities/kyoto_kiyomizu/realdata/status.json`: per-city capability status; its true geometry flag is scoped only to `CITYPACK_VALIDATED_ARTIFACT_CAPABILITY`.

## HISTORICAL_SNAPSHOT

- `reports/OVERNIGHT_REPORT.md`
- `reports/TEST_REPORT.txt`
- PR #1 records and Hosted runs associated with the earlier overnight integration
- `reports/RELEASE_CANDIDATE_MANIFEST.json` values, including old branch names, commit IDs, test counts, artifact hashes, and PR #1 references
- `reports/DATA_ACQUISITION_SUMMARY.csv`
- `reports/DATA_FRESHNESS_MATRIX.csv`
- `reports/GEOSPATIAL_QA_SUMMARY.md`
- `reports/HAZARD_SOURCE_MATRIX.csv`
- `reports/PR_READY.md`
- `reports/DEPENDENCY_AND_LICENSE_REPORT.md` data-inventory statements
- `reports/SECURITY_TRUST_BOUNDARY.md` PR/run and pre-Phase2 operational statements
- `reports/ACTION_PINNING_REPORT.md` PR/run and pre-Phase2 operational statements
- `reports/BRANCH_MATRIX.md`
- `reports/RESUME_AND_WATCHDOG_REPORT.md`
- prior completion/test counts embedded in older reports

These files are retained for audit history. Reports produced for `overnight-multicity-20260830` and superseded Phase 2 checkpoints are historical unless this index explicitly lists them as current. Where any historical file conflicts with the current authoritative set above, it is not a competing truth root.

## CURRENT_BUT_PUBLICLY_BLOCKED

- `reports/PUBLIC_RELEASE_GATE.md`
- `reports/LICENSE_DECISION.md`
- `reports/DATA_LICENSE_DECISION_MATRIX.csv`
- `reports/THIRD_PARTY_NOTICE_DRAFT.md`
- `reports/VERSION_DECISION.md`

`PUBLIC_RELEASE_READY=false`. Engineering verification does not close license, attribution/share-alike, public release, administrative validation, or human main-merge gates.
