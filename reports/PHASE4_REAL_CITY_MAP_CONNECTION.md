# Phase 4 real-city map connection

Status: `GREEN_CANDIDATE_EXPLICIT_OPT_IN`

The existing MapLibre viewer now accepts exact hash/provenance-allowlisted candidate artifacts for Kiyomizu, Arashiyama, and Fujisawa/Enoshima. The default remains `SYNTHETIC_DEMO`; real candidate geometry requires explicit opt-in. Missing or mismatched artifacts fail closed to the synthetic view.

| City | Nodes | Edges | Components | Viewer | Hazard | M7 |
|---|---:|---:|---:|---|---|---|
| Kiyomizu | 21 | 19 | 2 | explicit opt-in | `NOT_CONNECTED` | 19 `NOT_COMPUTED` |
| Arashiyama | 530 | 578 | 9 | explicit opt-in | `NOT_CONNECTED` | 578 `NOT_COMPUTED` |
| Fujisawa/Enoshima | 16 | 15 | 1 | explicit opt-in | `NOT_CONNECTED` | 15 `NOT_COMPUTED` |

The UI exposes deterministic precomputed candidate-node selections, connected/disconnected results, ordered edge IDs, a `coordinate_degree` geometric length, provenance, evidence completeness, and M7 readiness. `coordinate_degree` is not a metre or geodesic distance.

Candidate connectivity does not establish accessibility, safety, passability, operation, evacuation suitability, or administrative validation. No hazard overlap is converted into `CLOSED`, `FAIL`, or any route recommendation. Screenshot filenames and SHA-256 values are recorded in `PHASE4_SCREENSHOT_ARTIFACTS.json` and are carried as CI/RC artifacts rather than Git binaries.
