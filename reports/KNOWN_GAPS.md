# Known gaps and human gates

Overall status: `PARTIAL_COMPLETE`.

## Product/data gaps

- No city has real source-traceable geometry connected to the viewer.
- No official hazard polygon/raster is connected to an edge; overlap and operational effects remain `UNKNOWN`.
- All displayed route geometry is `SYNTHETIC_DEMO`; graph status is `CANDIDATE`.
- M6/profile integration is absent, so profile result is `NOT_COMPUTED` and its selector is disabled.
- Demand, current capacity, verified entrances, and operating/opening state are incomplete. All five KPI values remain reasoned `null`, never zero.
- No real/candidate city graph reaches a production hazard/profile/model pipeline; `MODEL_CONNECTED=false`.
- 3D/Cesium/PLATEAU is `NOT_IMPLEMENTED`; no token or unverifiable tileset is loaded. The honest 2D fallback is preserved.
- Field verification and administrative validation have not occurred.
- City KPI ranking/comparison is not supported because assumptions and completeness differ.

City gap registers contain 31 records: 清水10 (OPEN 9, REQUIRES_APPLICATION 1), 嵐山13 (OPEN 13), 藤沢8 (BLOCKED 8).

## Operational gaps

- GitHub CLI is not authenticated and remote push was blocked: `GITHUB_PUSH_BLOCKED`.
- GitHub Actions are syntax/statically reviewed only; no hosted workflow run exists for this branch.
- Accessibility has automated/source review evidence, but no formal WCAG certification or assistive-technology user validation.
- The bounded strategy result is a single fixed Windows collision replay; permanent champion promotion requires human review and broader/alternating-order evidence.

## Required human review before merge

1. Source/truth-class and freshness interpretation for all 27 metadata rows.
2. Geospatial CRS/axis/lineage and the decision to retain all geometry as synthetic candidate data.
3. Hazard scenario vocabulary, `UNKNOWN` preservation, and absence of official closure inference.
4. M6/profile disablement and reasoned-null KPI contract.
5. Hokonavi information-loss mapping and the fact that no adapter to production state is connected.
6. UI safety wording, attribution, accessibility, and 3D fallback.
7. CI/action pins, dependency/license report, and release archive manifest.
8. Every commit on the integration branch, then an explicitly authorized push/PR and merge. No fast-forward to `main` has been performed.
