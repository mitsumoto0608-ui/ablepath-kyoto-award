# Phase 4 overnight blocker-resolution report

Status: `LOCAL_GREEN_HOSTED_CI_PENDING`. This report is an internal review receipt, not an M6/Hokonavi freeze, safety certification, administrative validation, main-merge approval, tag, or public release.

## Anchors and scope

- Source private main: `76bbe2a1d85ea1f328cb41ddb0171c75331a1897`
- Baseline tag target: `0c3289b9174bf624c95faeaa3c1643664e31c2eb`
- Integration branch: `integration/phase4-blocker-resolution-v1`
- Core integration commits: `9cad3bb`, `b47d018`, `f26ed08`, `3110989`; readiness receipt: `e83af01`; acquisition handoff integration: `3dd830c`
- `src/allocate.py` remains frozen at `2e5c6f7fb994cd2b1790daf9414e3761c6682634725583881222520d01efd15b`.

## Data and analysis result

Arashiyama and Fujisawa now have source-traceable bounded OSM/ODbL candidate geometry, normalized candidate graphs, deterministic topology/path analysis, and explicit-opt-in MapLibre display. Kiyomizu retains its existing explicit candidate mode. All three default to the synthetic schematic until the user opts in.

The path length is `coordinate_degree`, not metres or a geodesic distance. Candidate connectivity does not claim accessibility, safety, passability, evacuation suitability, or recommendation. Official hazard geometry is connected for zero cities; no overlap result creates `CLOSED`, `FAIL`, or another edge state. M6 remains `NOT_COMPUTED`. All 612 candidate edges are M7 `NOT_READY_REASONED_NULL`; ready and computed counts are zero.

Raw ZIP/PDF/snapshot bytes remain outside Git. Git contains bounded normalized artifacts and hash/URL/time/transform receipts. Formal CRS semantics and GeoJSON longitude/latitude serialization are recorded separately. Unbound PLATEAU bytes remain metadata-only or null with a non-empty reason.

## DATA ACQUISITION handoff

The reviewed remote handoff `10f62a6fbb7ff1a1e4817faf6fdb12f9bdf9f2f5` was a single commit directly on private main, changed only 21 staging/report files, and passed Hosted run `33431944640` on Linux, Windows, and Viewer. It was integrated as `3dd830c` without resetting the existing P0/P1/P2 work.

Count wording is fixed as: **44 acquired/catalogued entries + 3 `NOT_FOUND` gap entries = 47 status rows**. Exactly seven entries are `READY_FOR_INGESTION`; they are candidates for a later consumer-specific normalization/analysis step, not automatically connected data. `READY_FOR_METADATA_ONLY`, `HUMAN_ACTION_REQUIRED`, `LICENSE_REVIEW_REQUIRED`, and `NOT_FOUND` remain disconnected. Raw originals were not downloaded again and absolute raw paths were not tracked.

## Local verification

- Python: `529 passed, 1 warning`
- Runner: 120 scenarios twice; both `results/all_runs.json` SHA-256 = `96ea1404c305531ae55c6c81900887efc3423c85b89e9af88851deefd053e3c1`
- Viewer unit: `46 passed`
- Viewer build: PASS
- Viewer E2E: all 40 results completed (`37 passed`, `3` expected mobile screenshot skips); the Windows Playwright helper was stopped only after all results were reported. Hosted Linux CI is the final E2E authority.
- 320 CSS-pixel regression: PASS
- npm audit: `0 vulnerabilities`
- repository trust-boundary/large-file scan: PASS
- independent final report/contract review: COMMIT YES, no findings
- post-handoff revalidation: Python `529 passed, 1 warning`; runner SHA twice unchanged; allocator SHA unchanged; trust scan PASS

The first two Python attempts were invalid environment runs because the default temp root was unreadable and the first alternate parent did not yet exist. With a dedicated writable temp parent, the unchanged suite passed. No source/test contract was weakened.

## Lane truth

- Arashiyama: `GREEN_CITY_ARTIFACT`, source staged/normalized/analysis/viewer true in bounded candidate scope
- Fujisawa: `GREEN_CITY_ARTIFACT`, source staged/normalized/analysis/viewer true in bounded candidate scope
- Map/UI: `GREEN_CANDIDATE_EXPLICIT_OPT_IN`
- M7: `NOT_READY_REASONED_NULL` (612/612; computed 0)
- M6: `READY_FOR_HUMAN_FREEZE_PACKET_ONLY`; production `BLOCKED_CONTRACT` and `NOT_COMPUTED`
- Hokonavi: `READY_FOR_HUMAN_FREEZE_PACKET_ONLY`; Proposal V2 is not frozen or production-integrated
- `SENTRY_STATUS=IMPLEMENTED_OPT_IN_NOT_CONFIGURED`
- `CODE_GRAPH_RAG_ADOPTION=REJECT`
- `MODEL_ROUTE_VERIFIED=false`; requested routes are recorded, actual model/effort were unavailable and are not claimed
- `ADMIN_VALIDATED=false`
- `PUBLIC_RELEASE_READY=false`

## Evidence and remaining gates

The seven exact screenshot names and SHA-256 values are in `PHASE4_SCREENSHOT_ARTIFACTS.json`. Hosted CI publishes them through `viewer-artifacts`; the internal RC copies the same bytes under `viewer/dist/screenshots/`. Final integration HEAD, Hosted run URL, and deterministic RC SHA are bound in the draft PR because those values are created after this commit.

Human decisions remain: accept the two bounded city artifacts, choose M6 H1-H20, choose Hokonavi F01-F16/D01-D25, authorize any future M7 evidence connector, and approve a private-main merge. Main merge, tag, public release, Sentry credentials, scientific/safety contract changes, and M6/Hokonavi freeze were not performed.
