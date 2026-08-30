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

- Current authenticated state: GitHub CLI is authenticated as `mitsumoto0608-ui`; integration commits are pushed to the remote and draft PR #1 targets `main`. Auto-merge is off and `main` remains unmerged.
- Pre-governance-sync evidence: source commit `aa957e3a024561022e939b4b00579251c9062a42` passed Hosted GitHub Actions run `33296626023` (Linux Python, Windows Python, and static viewer/Node jobs all succeeded). The governance-sync commit requires a new successful Hosted run before review handoff.
- Historical only: an earlier local snapshot recorded `GITHUB_PUSH_BLOCKED` before human authentication. That condition is resolved and is not the current state.
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
8. Every commit on the integration branch, the final Hosted run, and release ZIP SHA-256. Before public distribution or merge, the owner must decide the root project LICENSE/NOTICE, third-party notices, external-metadata redistribution terms, and RC/version/tag policy. Current versions are `pyproject.toml` 0.2.0 and private viewer 0.1.0; `v0.2.0-baseline` must remain fixed. Push and draft PR creation are complete; merge still requires explicit human authorization. No fast-forward to `main` has been performed.
