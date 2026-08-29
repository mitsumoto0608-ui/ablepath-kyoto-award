# Multi-city static viewer contract

The viewer is a client-only React/Vite application that reads precomputed JSON. It does not calculate routes, infer closures, evaluate a pedestrian profile, predict building damage, or turn missing evidence into a favorable result.

## Truth boundary

- The shipped map coordinates are `SYNTHETIC_DEMO` and have no real-world scale or coordinate reference system.
- Official sources are represented only by IDs that resolve through each city pack's source manifest. The viewer does not silently promote metadata to geometry.
- M6 is not implemented. `profile_status` must be exactly `NOT_COMPUTED`, and the profile selector remains disabled.
- A missing demand, capacity, entrance, operation, topology, or profile prerequisite produces a KPI `value: null` with a non-empty `reason`.
- `UNKNOWN` remains distinct from PASS, OPEN, false, and zero.
- Viewer-data v1 uses closed object schemas. Extra profile, accessibility, route, or state fields are rejected, and `UNKNOWN` or metadata-only evidence cannot produce a non-`UNKNOWN` display state.
- The 3D tab is non-gating and currently reports `NOT_IMPLEMENTED`; 2D stays usable.
- Viewer-data v1 accepts row-level `OFFICIAL_METADATA_ONLY`, `VGI_METADATA_ONLY`, `SYNTHETIC_DEMO`, or `UNKNOWN`. It rejects self-asserted `REAL` and `MODEL_DERIVED` rows because this bundle has no build-verified real/model provenance contract. Future support requires source URL, revision/lineage, integrity or model identity, and input-source reference checks before those classes may be enabled.
- A city-level `official_metadata_status: OFFICIAL_METADATA_ONLY` is valid only when at least one source row has `data_class: OFFICIAL_METADATA_ONLY`; the badge cannot be asserted without matching source provenance.
- The same restriction applies to map geometry status: `REAL` and `MODEL_DERIVED` remain reserved vocabulary but are rejected until build-time provenance verification exists. An official closure cannot coexist with `PASS`.
- Source freshness uses the canonical V4 vocabulary `CURRENT_CONFIRMED`, `CURRENT_UNVERIFIED`, `POSSIBLY_STALE`, `SUPERSEDED`, or `UNKNOWN`; metadata-only status is carried separately by `data_class`.
- Integration must verify every non-fixture viewer source ID against the corresponding city-pack source manifest. UI fixture IDs remain synthetic and must not be mistaken for official sources.
- Facility, entrance, capacity, operation, demand, origin, profile, and KPI readiness remain separate fields; one readiness state must not stand in for another.

## Loader boundary

The JSON loader fails closed before rendering. It requires strict semantic-version syntax and a supported major version; bounded city/source/scenario/edge/point counts; unique stable IDs; complete source references; exact state enums; provenance consistency; finite non-negative physical values or reasoned `null`; finite SVG coordinates inside the declared view box; and the exact five KPI keys. Payloads above 2 MB are rejected. React escaping remains defense in depth rather than a substitute for contract validation.

## Reproducible state

City, view, and selected edge are recorded in URL query parameters. Unknown values fall back to documented defaults. Scenario, strict/optimistic evidence treatment, and Before/After are disabled and omitted from the URL because variant-specific precomputed outputs are not connected. They must not become active until selecting them changes a source-traceable precomputed snapshot; the browser never performs route calculation.

## Accessibility

The application includes a skip link, semantic headings and regions, labelled form controls, visible focus, a polite live region, keyboard-operable SVG edges, status text/marks in addition to color and dash patterns, a table alternative to the map, responsive layout, and reduced-motion handling. Full WCAG 2.2 AA conformance is not claimed until the recorded audit and human review are complete.

## Dependencies

| Package | Version | Purpose | License |
| --- | ---: | --- | --- |
| react / react-dom | 19.2.8 | UI component rendering | MIT |
| vite | 8.2.2 | deterministic static build/dev server | MIT |
| @vitejs/plugin-react | 6.1.1 | React transform for Vite | MIT |
| @playwright/test | 1.62.1 | deterministic browser checks/screenshots | Apache-2.0 |

Versions and license metadata were read from the npm registry on 2026-08-30. Registry data was treated as untrusted metadata; no package-provided command was copied into the repository.
