# Kyoto–Fujisawa delivery sprint

Status: **PARTIAL** (`COMPLETE=false`, `P0_COMPLETE=false`, `USER_VALIDATED=false`).

Remote delivery is paused. Read-only GitHub API inspection on 2026-09-10 found the repository public while current F6 authorizes no public Git, RC, or demo. See `DELIVERY_PUBLIC_SCOPE_RECONCILIATION.json`; no new push, merge, public attachment, or visibility change is authorized until the owner reconciles that mismatch.

The existing real-coordinate/CANDIDATE view now provides a source-side, static review workflow for Kiyomizu/Gion/connector, Arashiyama, and Enoshima/Katase. Select the city, explicitly switch to **実座標 / CANDIDATE**, select a precomputed candidate origin/destination fixture, inspect scenario-separated hazard overlap, terrain status, facility evidence and unknowns, then save CSV, JSON, or printable HTML.

Implemented:

- exact F1–F6 policy binding with zero production values; unapproved taxonomy mappings, tolerance, station interval, UNKNOWN details and long-edge splitting remain closed;
- Kyoto A31b five themes and Kyoto landslide five layers kept as separate scenarios;
- Fujisawa A40 tsunami geometry;
- explicit EPSG:4326/EPSG:6668 inputs projected independently into EPSG:6674 (Kyoto) or EPSG:6677 (Fujisawa) before source-side edge intersection;
- full-source-scan/AOI selection receipts and retained-archive-member byte checks;
- Kyoto 77 original-source facility records and attributes, and Fujisawa 57 address-only records;
- scenario/revision/coverage/missing-field/reason/owner-filtered, provenance-bearing CSV/JSON/printable HTML exports containing source URL, revision, license scope, selection/source hashes, feature IDs and limitations;
- no viewer graph, topology, path, hazard-intersection, or M7 calculation.
- connected and disconnected Kyoto examples are now named in `DELIVERY_EXPORT_EVIDENCE.json`; CSV, JSON, and printable HTML preserve the same path selection, filters, sort and candidate-edge set. The disconnected examples remain explicit reasoned-null negative cases with zero candidate rows.

Blocked or partial:

- GSI DEM elevation sampling is blocked because the retained inventory does not establish the vertical datum. Existing GML must first be compared with an authoritative official specification located and hash-bound from existing controlled holdings; no such specification is claimed to be present in this repository. Only a missing or unresolved authoritative-spec result becomes a human gate. No elevation, step, curb, longitudinal slope, cross-slope, M6 or accessibility value is inferred.
- Existing bounds establish that Fujisawa DEM1A and DEM5A contain the candidate AOI and DEM5B is outside it. Hash-mounting the retained originals and checking official product metadata can proceed without new policy; product selection, fusion, interpolation, unresolved datum interpretation and field-derived accessibility remain gated.
- Fujisawa earthquake remains inventory-only. Its declared EPSG:4301 conflicts with projected-looking native bounds; an authoritative specification found and hash-bound from existing controlled holdings may resolve this mechanically, otherwise no CRS override is permitted.
- Fujisawa liquefaction remains inventory-only. Existing EPSG:4612 files can proceed if exact official source/version/license/codebook receipts are found and hash-bound in existing controlled holdings, but no such complete receipt set is claimed here and no threshold or taxonomy may derive closure, damage, debris, safety or passability.
- Kyoto emergency open spaces and temporary-stay facilities remain metadata-only; Fujisawa facilities remain address-only with no markers or geocoding.
- PLATEAU real 3D is not connected. Existing candidate 2D is the deterministic fallback.
- M7 evidence-ready/computed counts remain 0/0. No setback, damage or debris value is inferred.

Hazard overlap is evidence only. It never creates CLOSED, FAIL, damage, debris, passability, accessibility, safety, current facility operation, or administrative-validation state.

Decision authority is separated in `DELIVERY_DECISION_BINDING_AUTHORITY.json`: `F1_F6_DECISION_BINDING.json` plus `LICENSE_FINAL_SCOPE_DECISION.json` is current; `M7_LICENSE_DECISION_BINDING.json` is a preserved historical pre-decision receipt and cannot override the current F6 scope.
