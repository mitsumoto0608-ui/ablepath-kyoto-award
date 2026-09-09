# Kyoto–Fujisawa delivery sprint

Status: **PARTIAL** (`COMPLETE=false`, `P0_COMPLETE=false`, `USER_VALIDATED=false`).

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

Blocked or partial:

- GSI DEM elevation sampling is blocked: the retained inventory does not establish the required vertical datum; no elevation, step, curb, longitudinal slope, cross-slope, M6 or accessibility value is inferred.
- Fujisawa earthquake and liquefaction remain inventory-only because accepted AOI geometry/CRS/license binding is incomplete.
- Kyoto emergency open spaces and temporary-stay facilities remain metadata-only; Fujisawa facilities remain address-only with no markers or geocoding.
- PLATEAU real 3D is not connected. Existing candidate 2D is the deterministic fallback.
- M7 evidence-ready/computed counts remain 0/0. No setback, damage or debris value is inferred.

Hazard overlap is evidence only. It never creates CLOSED, FAIL, damage, debris, passability, accessibility, safety, current facility operation, or administrative-validation state.
