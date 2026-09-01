# Known gaps and human gates

Overall status: `PARTIAL_COMPLETE`.

## Product/data gaps

- All three cities have hash-bound, source-traceable VGI real-coordinate `CANDIDATE` geometry connected to deterministic topology/path analysis and the viewer only through explicit MapLibre opt-in. These candidate-only viewer connections are not model-pipeline connections and do not establish route continuity, passability, accessibility, or safety.
- The Kiyomizu official landslide preview is quarantined as `NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT`; no official hazard polygon/raster is connected to an edge and operational effects remain `UNKNOWN`.
- The default viewer display remains `SYNTHETIC_DEMO` in all three cities. Each city can explicitly switch to its source-traceable VGI real-coordinate `CANDIDATE` layer; route continuity remains `NOT_ESTABLISHED` for every city.
- M6/profile integration is absent, so profile result is `NOT_COMPUTED` and its selector is disabled.
- Demand, current capacity, verified entrances, and operating/opening state are incomplete. All five KPI values remain reasoned `null`, never zero.
- Official hazard analysis is connected in 0 cities, and M7-ready/M7-computed edge counts are both 0. No real/candidate city graph reaches a production hazard/profile/model pipeline; `M7_CONNECTED_TO_REAL_EDGES=false`, `M6_CONNECTED=false`, `KPI_CONNECTED=false`, and `MODEL_CONNECTED=false`.
- Cesium runtime is implemented and lazy-loaded behind mocked success/failure gates. A real PLATEAU tileset is not validated or connected, and load/tile/render/timeout failure returns to the current 2D layer.
- Field verification and administrative validation have not occurred.
- City KPI ranking/comparison is not supported because assumptions and completeness differ.

Legacy city gap registers contain 31 historical records: 清水10 (OPEN 9, REQUIRES_APPLICATION 1), 嵐山13 (OPEN 13), 藤沢8 (BLOCKED 8). Those snapshots are not evidence of current artifact absence and do not override `reports/PHASE4_ANALYSIS_UI_GATE.json`, the sole current machine truth root.

## Operational gaps

- Historical integration receipts for draft PR #2 and draft PR #3 remain auditable snapshots, not current truth authority. Current remediation PR heads and Hosted CI receipts must be recorded in their own PRs; auto-merge remains off and `main` remains unchanged.
- `SERVER_SIDE_BRANCH_PROTECTION=false`; the versioned local guard is not equivalent to server-side protection. Main merge remains human-only.
- Historical only: PR #1, pre-Phase2 Hosted runs, and an earlier `GITHUB_PUSH_BLOCKED` snapshot are not current Phase 2 state.
- Accessibility has automated/source review evidence, but no formal WCAG certification or assistive-technology user validation.
- The bounded strategy result is a single fixed Windows collision replay; permanent champion promotion requires human review and broader/alternating-order evidence.

## Required human review before merge

1. Source/truth-class and freshness interpretation for all 27 metadata rows.
2. Geospatial CRS/axis/lineage、synthetic defaultを保つ判断、および3都市の明示opt-in source-traceable VGI/CANDIDATE viewer scope（全都市 `NOT_ESTABLISHED`）。
3. Hazard scenario vocabulary, `UNKNOWN` preservation, and absence of official closure inference.
4. M6/profile disablement and reasoned-null KPI contract.
5. Hokonavi information-loss mapping and the fact that no adapter to production state is connected.
6. UI safety wording, attribution, accessibility, MapLibreの3都市candidate-only scope、Cesium runtimeと未接続PLATEAUの区別、および3D→2D fallback。
7. CI/action pins, dependency/license report, and release archive manifest.
8. Every commit on the integration branch, the final Hosted run, and release ZIP SHA-256. Before public distribution or merge, the owner must decide the root project LICENSE/NOTICE, third-party notices, external-metadata redistribution terms, and RC/version/tag policy. Current versions are `pyproject.toml` 0.2.0 and private viewer 0.1.0; `v0.2.0-baseline` must remain fixed. Push and draft PR creation are complete; merge still requires explicit human authorization. No fast-forward to `main` has been performed.
