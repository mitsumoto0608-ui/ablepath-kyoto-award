# M7 real-edge evidence acquisition plan

This plan closes evidence fields without changing the frozen M7 formula, constants, API, or safety contract. The broad scan is complete for all 612 current real candidate edges; no edge is currently callable or evidence-ready.

## Acquisition order

1. **Edge identity and subarea receipt** — retain current candidate artifact hashes and add reviewed Kiyomizu/Gion/connector partition evidence. This does not establish passability.
2. **`clear_width_m`** — prefer reviewed official walking-space evidence, then explicit source-tagged width with exact unit/provenance, then verified field measurement. Never infer from highway class, DEM, image/raster appearance, or nominal road width.
3. **Left/right building coverage** — use official PLATEAU footprints and stable building IDs with a fixed edge direction, CRS, method/version, and `coverage_status=COMPLETE`. An empty list is evidence only when the complete-coverage receipt proves no influencing building. Multiple influencing buildings remain an interval-split proposal; do not aggregate them for the core.
4. **`height_m`** — official direct height may be a candidate. A geometry-derived height remains `DERIVED_CANDIDATE_NOT_FROZEN` until the derivation method is human-frozen.
5. **`setback_m`** — no project-frozen definition/method was found in the current contract. Keep missing. Centroid distance is prohibited. A proposal, fixture, isolated validation, independent review, and human freeze are required before use.
6. **`damage_state` / `debris_present`** — require building-specific official or validated scenario evidence. Do not derive either field from hazard overlap, intensity, liquefaction, building height, or PLATEAU presence. Unknown cannot be converted to `DAMAGED` or `false`.
7. **`variant`** — record an explicit reviewed `mean_case` or `sensitivity_high_case` decision. Never use a silent default or present the variant as a route judgment.
8. **`official_closure`** — use official closure evidence. `None` is valid only with a bounded-query receipt; preserve it exactly and never convert it to false/open.
9. **`hazard_data_status`** — connect a verified hazard-context receipt or a bounded `UNKNOWN` decision receipt. This field is not a road state and does not generate closure.

## Per-field receipt gate

Every top-level API field requires `source_id`, `revision_id`, lowercase 64-character `source_sha256`, and `evidence_status=SOURCE_TRACEABLE`. Building-side receipts additionally require `coverage_status=COMPLETE` and `observed_count` equal to the list length. Derived evidence additionally records transform ID/version and input/output SHA, but an unfrozen method cannot satisfy readiness.

## Human freezes still required

Setback definition/method, height derivation, building influence intervals, damage/debris generation, width inference, thresholds, route state, and accessibility/safety claims remain human gates. The next control integration may add accepted PLATEAU inventory evidence, but it must not silently promote any edge.

## Completion semantics

`M7_EVIDENCE_PIPELINE_COMPLETE=true` means every current edge received a deterministic, reasoned readiness receipt. It does not mean M7 ran. Until at least one real edge has complete evidence, `M7_CONNECTED_TO_REAL_EDGES=false` and every result remains `null / NOT_COMPUTED`.
