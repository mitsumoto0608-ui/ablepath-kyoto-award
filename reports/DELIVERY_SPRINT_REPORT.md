# Kyoto–Fujisawa delivery sprint

Status: **PARTIAL** (`COMPLETE=false`, `P0_COMPLETE=false`, `USER_VALIDATED=false`).

The 2026-09-10 owner amendment authorizes public Git for reviewed code and redistributable derived artifacts. The earlier visibility/F6 mismatch is retained as history in `DELIVERY_PUBLIC_SCOPE_RECONCILIATION.md` and is resolved by `PUBLIC_GIT_SCOPE_AMENDMENT_20260910.json`. Existing-workflow Hosted CI artifacts are limited to scanned reviewed reports/static outputs/test evidence; manual public attachments, public RC/demo/release, visibility changes, and `main` merge remain unauthorized.

The existing real-coordinate/CANDIDATE view now provides a source-side, static review workflow for Kiyomizu/Gion/connector, Arashiyama, and Enoshima/Katase. Select the city, explicitly switch to **実座標 / CANDIDATE**, select a precomputed candidate origin/destination fixture, inspect scenario-separated hazard overlap, terrain status, facility evidence and unknowns, then save CSV, JSON, or printable HTML.

Implemented:

- exact F1–F6 policy binding with zero production values; unapproved taxonomy mappings, tolerance, station interval, UNKNOWN details and long-edge splitting remain closed;
- Kyoto A31b five themes and Kyoto landslide five layers kept as separate scenarios;
- Fujisawa A40 tsunami geometry;
- explicit EPSG:4326/EPSG:6668 inputs projected independently into EPSG:6674 (Kyoto) or EPSG:6677 (Fujisawa) before source-side edge intersection;
- full-source-scan/AOI selection receipts and retained-archive-member byte checks;
- Kyoto 77 original-source facility records and attributes. Fujisawa's 339/57-row address-only derivatives are excluded from the current public Git tip, viewer, and CI artifacts because provider redistribution permission is not bound; their hashes/counts remain in a metadata receipt and the prior public history remains reachable;
- scenario/revision/coverage/missing-field/reason/owner-filtered, provenance-bearing CSV/JSON/printable HTML exports containing source URL, revision, license scope, selection/source hashes, feature IDs and limitations;
- no viewer graph, topology, path, hazard-intersection, or M7 calculation.
- connected and disconnected Kyoto examples are now named in `DELIVERY_EXPORT_EVIDENCE.json`; CSV, JSON, and printable HTML preserve the same path selection, filters, sort and candidate-edge set. The disconnected examples remain explicit reasoned-null negative cases with zero candidate rows.
- GSI DEM1A and DEM5A native-cell values are connected independently for all three city graphs, with product, member SHA, grid index, surface type, vertical reference, null reason and no-interpolation method preserved in UI/export.
- Fujisawa's eight official liquefaction-distribution scenarios, one shaking-susceptibility reference layer, and one liquefaction-hazard reference layer are connected as raw source classes under the official Kanagawa catalog/definition receipt. They remain exposure evidence only.

Blocked or partial:

- DEM5B remains outside the verified candidate AOIs and is not silently substituted or mosaicked. DEM1A/5A samples are DEM-cell elevation, not surveyed walking-surface elevation; step, curb, longitudinal/cross slope, M6 and accessibility remain unknown/not computed.
- Fujisawa intensity distribution remains `CRS_UNRESOLVED`/`NOT_CONNECTED`: its declared EPSG:4301 conflicts with projected-looking native bounds and no provider correction has been found. No CRS is inferred from coordinate appearance.
- Fujisawa connected liquefaction/shaking layers preserve each official raw class and scenario. No threshold or taxonomy derives closure, damage, debris, safety or passability.
- Kyoto emergency open spaces and temporary-stay facilities remain metadata-only. Fujisawa facility row data is excluded from the current public tip and all delivery payloads pending explicit provider permission; no markers or geocoding are created. The historical public exposure is recorded rather than rewritten.
- PLATEAU real 3D is not connected. Existing candidate 2D is the deterministic fallback.
- M7 evidence-ready/computed counts remain 0/0. No setback, damage or debris value is inferred.

Hazard overlap is evidence only. It never creates CLOSED, FAIL, damage, debris, passability, accessibility, safety, current facility operation, or administrative-validation state.

Decision authority is separated in `DELIVERY_DECISION_BINDING_AUTHORITY.json`: `F1_F6_DECISION_BINDING.json` plus `LICENSE_FINAL_SCOPE_DECISION.json` is current; `M7_LICENSE_DECISION_BINDING.json` is a preserved historical pre-decision receipt and cannot override the current F6 scope.
