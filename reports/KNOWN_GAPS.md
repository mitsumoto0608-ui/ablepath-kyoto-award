# Known gaps and human gates

Overall status: `PARTIAL_COMPLETE`.

## Product/data gaps

- Kiyomizu has a hash-bound `SOURCE_TRACEABLE_REAL` / VGI corridor artifact and a 21-node/19-edge candidate graph connected to the viewer only through explicit MapLibre opt-in. This candidate-only viewer connection is not a model-pipeline connection and does not establish route continuity, passability, or safety.
- The Kiyomizu official landslide preview is quarantined as `NOT_CONNECTED_RAW_SOURCE_OUTSIDE_TRUST_ROOT`; no official hazard polygon/raster is connected to an edge and operational effects remain `UNKNOWN`.
- The default viewer display is `SYNTHETIC_DEMO` in all three cities. Kiyomizu alone can explicitly switch to its real-coordinate `CANDIDATE` layer with route continuity `NOT_ESTABLISHED`; Arashiyama and Fujisawa remain synthetic fallbacks.
- M6/profile integration is absent, so profile result is `NOT_COMPUTED` and its selector is disabled.
- Demand, current capacity, verified entrances, and operating/opening state are incomplete. All five KPI values remain reasoned `null`, never zero.
- No real/candidate city graph reaches a production hazard/profile/model pipeline; `MODEL_CONNECTED=false`.
- Cesium runtime is implemented and lazy-loaded behind mocked success/failure gates. A real PLATEAU tileset is not validated or connected, and load/tile/render/timeout failure returns to the current 2D layer.
- Field verification and administrative validation have not occurred.
- City KPI ranking/comparison is not supported because assumptions and completeness differ.

Legacy city gap registers contain 31 records: 清水10 (OPEN 9, REQUIRES_APPLICATION 1), 嵐山13 (OPEN 13), 藤沢8 (BLOCKED 8). They are not evidence that the excluded Arashiyama/Fujisawa real-data lanes were integrated.

## Operational gaps

- Current authenticated state: draft PR #2 targets `main` from `integration/realdata-model-map-v1` at `1a62a55b1ff6bd047b433bfd594b0c30e91f9f0d`; pull-request run `33330312591` succeeded. Draft PR #3 is stacked on PR #2 from `integration/phase3-parallel-v1`; after final verification, its body must record the exact truth-sync head, Hosted run, screenshot artifact, and RC SHA. Auto-merge is off and `main` remains unchanged.
- `SERVER_SIDE_BRANCH_PROTECTION=false`; the versioned local guard is not equivalent to server-side protection. Main merge remains human-only.
- Historical only: PR #1, pre-Phase2 Hosted runs, and an earlier `GITHUB_PUSH_BLOCKED` snapshot are not current Phase 2 state.
- Accessibility has automated/source review evidence, but no formal WCAG certification or assistive-technology user validation.
- The bounded strategy result is a single fixed Windows collision replay; permanent champion promotion requires human review and broader/alternating-order evidence.

## Required human review before merge

1. Source/truth-class and freshness interpretation for all 27 metadata rows.
2. Geospatial CRS/axis/lineage、synthetic defaultを保つ判断、および清水の明示opt-in real VGI/CANDIDATE viewer scope。
3. Hazard scenario vocabulary, `UNKNOWN` preservation, and absence of official closure inference.
4. M6/profile disablement and reasoned-null KPI contract.
5. Hokonavi information-loss mapping and the fact that no adapter to production state is connected.
6. UI safety wording, attribution, accessibility, MapLibreの清水限定scope、Cesium runtimeと未接続PLATEAUの区別、および3D→2D fallback。
7. CI/action pins, dependency/license report, and release archive manifest.
8. Every commit on the integration branch, the final Hosted run, and release ZIP SHA-256. Before public distribution or merge, the owner must decide the root project LICENSE/NOTICE, third-party notices, external-metadata redistribution terms, and RC/version/tag policy. Current versions are `pyproject.toml` 0.2.0 and private viewer 0.1.0; `v0.2.0-baseline` must remain fixed. Push and draft PR creation are complete; merge still requires explicit human authorization. No fast-forward to `main` has been performed.
