# Global report authority

This index separates the current Phase 4 machine truth from compatibility mirrors, supporting evidence, and retained historical snapshots. Historical files remain useful audit evidence but are not competing truth roots.

## CURRENT_AUTHORITATIVE

- `reports/PHASE4_ANALYSIS_UI_GATE.json` is the **sole current machine truth root** for the three-city data, topology-analysis, candidate-path UI, and explicit-opt-in viewer scope. It also records every preserved false/not-connected boundary.
- `reports/COMPLETION_LEVELS.json` is a current **compatibility mirror**. Tests require its global flags to agree with the Phase 4 truth root; it is not an independent authority.
- `viewer/public/data/maps/map-layers.json` is runtime evidence for the exact three-city VGI `CANDIDATE` artifacts. It is not product-wide safety, model, or administrative authority.
- `reports/PHASE4_REAL_CITY_MAP_CONNECTION.md` is supporting narrative for the three-city explicit-opt-in candidate viewer connection.
- `reports/KNOWN_GAPS.md` and `reports/PUBLIC_RELEASE_GATE.md` are current human-readable gap and release-blocker projections.
- Each city artifact manifest/receipt remains authoritative for that artifact's bytes and provenance within its city pack.
- RC root `RELEASE_MANIFEST.json` exists inside each generated deterministic RC ZIP, not as a tracked checkout-root file. Its source commit and checksums are authoritative only for that archive.

The scoped current truth is: all three cities have source-traceable VGI real-coordinate `CANDIDATE` geometry and deterministic candidate analysis available through explicit viewer opt-in; all three still default to `SYNTHETIC_DEMO`, route continuity is `NOT_ESTABLISHED`, official hazard analysis covers zero cities, M7 ready/computed counts are zero, M6 is `NOT_COMPUTED`, and model/KPI/Hokonavi production/PLATEAU/facility/administrative/public-release connections remain false.

## HISTORICAL_SNAPSHOT

- `reports/PHASE3_MAP_UI_STATUS.md` is historical Phase 3 evidence and contains superseded Kiyomizu-only scope literals.
- `reports/PHASE2_AUTONOMOUS_REALDATA_REPORT.md` and other Phase 2 status reports are historical engineering checkpoints.
- PR #1, PR #2, and PR #3 records and their Hosted runs are historical review vehicles, not current product truth.
- `reports/OVERNIGHT_REPORT.md`
- `reports/TEST_REPORT.txt`
- `reports/RELEASE_CANDIDATE_MANIFEST.json`
- `reports/DATA_ACQUISITION_SUMMARY.csv`
- `reports/DATA_FRESHNESS_MATRIX.csv`
- `reports/GEOSPATIAL_QA_SUMMARY.md`
- `reports/HAZARD_SOURCE_MATRIX.csv`
- `reports/PR_READY.md`
- `reports/DEPENDENCY_AND_LICENSE_REPORT.md` data-inventory statements
- `reports/SECURITY_TRUST_BOUNDARY.md` earlier operational statements
- `reports/ACTION_PINNING_REPORT.md` earlier operational statements
- `reports/BRANCH_MATRIX.md`
- `reports/RESUME_AND_WATCHDOG_REPORT.md`
- prior completion/test counts, branch names, commit IDs, PR numbers, and run IDs embedded in older reports

Where a historical file conflicts with `reports/PHASE4_ANALYSIS_UI_GATE.json`, the Phase 4 root controls. Historical text must not be joined into current-truth consistency checks.

## CURRENT_BUT_PUBLICLY_BLOCKED

- `reports/PUBLIC_RELEASE_GATE.md`
- `reports/LICENSE_DECISION.md`
- `reports/DATA_LICENSE_DECISION_MATRIX.csv`
- `reports/THIRD_PARTY_NOTICE_DRAFT.md`
- `reports/VERSION_DECISION.md`

`PUBLIC_RELEASE_READY=false`. Engineering verification does not close license, attribution/share-alike, safety, public release, administrative validation, or human main-merge gates.
