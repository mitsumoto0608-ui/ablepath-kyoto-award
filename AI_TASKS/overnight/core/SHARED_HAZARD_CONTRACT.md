# Shared hazard core v1

This lane adds only versioned, profile-independent contracts and validation.

- `HazardScenario` carries an explicit source class, assumption authority, optional elapsed time, coverage flag, frozen four-state default, disclaimer, and source IDs.
- `EdgeHazardObservation` keeps physical overlap, depth, official closure, and `KNOWN`/`UNKNOWN` status orthogonal. It never derives closure from overlap.
- `EdgeScenarioPhysics` carries nullable widths, other physical values, and provenance. It has no M6/profile or routing state.
- The city-pack loader rejects unsupported schema majors with an actionable migration message. It does not reinterpret old data.
- While M6 and readiness prerequisites are unavailable, profile status remains `NOT_COMPUTED` and KPI values remain `null` with a non-empty reason.
- The Python validator is the runtime authority. The JSON Schema files are a portable structural subset with closed property sets and typed records; relational rules that portable JSON Schema cannot express (currently `mean_depth_m <= max_depth_m`) are named by a versioned `x-ablepath-runtime-validation` annotation and still require the Python validator. A caller must not treat schema-only validation as full contract acceptance.
- The source-manifest adapter preserves each row unchanged, recognizes three exact v1 header dialects, and normalizes only the exact `OFFICIAL_METADATA_ONLY`/`VGI_METADATA_ONLY` mappings. Other truth classes fail closed rather than being promoted.
- `load_citypack(..., trusted_root=...)` accepts only packs contained by the caller-selected trusted root and rejects symlinks/reparse points, duplicate YAML keys, aliases, oversized documents, and excessive structure depth/count.
- Runtime hazard records detach and recursively freeze nested provenance. `physical_values` cannot contain profile, accessibility, route, or state fields.
- `official_or_assumption` is an explicit evidence-authority enum. An official claim requires an official/real source class and a non-empty source list.
- `load_edge_observation_table` recognizes only the exact ordered Kiyomizu, Arashiyama, and Fujisawa v1 CSV headers, including duplicate-header rejection and bounded file/row counts. The adapters validate the current dialect semantics, accept only UNKNOWN-only physical rows, and reject populated physical fields; new physical data requires a new reviewed adapter rather than silent coercion. Pack-specific audit columns stay in an immutable raw mapping beside the profile-independent runtime object, so callers retain traceability without promoting audit metadata into physical state.

No allocation, route, UI, facility-operation, or new accessibility threshold is implemented here.
