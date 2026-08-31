# Phase 4 overnight blocker resolution

Goal: Starting from verified private main `76bbe2a1d85ea1f328cb41ddb0171c75331a1897`, deliver source-traceable real candidate data, deterministic topology/path analysis, and explicit-opt-in MapLibre UI for all three cities; reasoned-null M7 readiness; review-only M6/Hokonavi freeze packets; Hosted CI; deterministic internal RC; and one draft PR.

Success criteria:

- Arashiyama and Fujisawa are `SOURCE_STAGED=true` and `NORMALIZED_INGESTED=true` without tracked raw ZIP/PDF files.
- Kiyomizu, Arashiyama, and Fujisawa have deterministic topology and candidate-path artifacts connected to the existing viewer.
- `reports/PHASE4_DATA_INGESTION_GATE.json` and `reports/PHASE4_ANALYSIS_UI_GATE.json` are machine-readable and conservative.
- M7 is computed only with complete source-traceable evidence; otherwise it is `null` with a non-empty reason. M6 remains `NOT_COMPUTED`.
- M6 H1-H20 and Hokonavi are at most `READY_FOR_HUMAN_FREEZE`; no production freeze occurs.
- Integration branch, draft PR, Hosted CI, and byte-identical internal RC A/B are complete.

Constraints: no main push/merge, tag, release, branch deletion, force push, `--no-verify`, Sentry credentials, unsafe claims, UNKNOWN promotion, raw large archive commit, M6/Hokonavi automatic freeze, or frozen allocation-engine changes.

Priority: P0 data ingestion; P1 deterministic topology/path analysis; P2 UI; P3 official hazard only with a complete trust chain; P4 M7 readiness/limited computation; P5 freeze packets.

Rollback: discard Phase 4 feature/integration branches and worktrees; private main and the baseline tag remain unchanged.
