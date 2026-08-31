# Phase 4 Arashiyama P0 — source-traceable candidate ingestion

`SOURCE_STAGED=true`; `NORMALIZED_INGESTED=true`; `VIEWER_CONNECTED=false`.

The retained source is a fixed-time bounded OpenStreetMap/Overpass response:

- source class: `VGI`
- snapshot: `2026-08-29T00:00:00Z`
- raw SHA-256: `1cde93d68bebf633989e825cbd5ac1e772cee81508043f44beb311250a1e8013`
- retrieval query SHA-256: `b5c52b3ea7542261159b5764956aa9662673c0422b3509dc59e4866f00c14603`
- raw byte size: `106464`
- external trust location: `ablepath-raw/kyoto_arashiyama` (SHA verified read-only on `2026-09-01`)

Git includes the receipt, query, normalized artifacts, and compact hash-bound manifest (one artifact record for `corridor.real.geojson`); it does not include the raw response, raw official archives, or PDFs. Feature-level OSM lineage remains on normalized GeoJSON properties. Normalized candidate topology has 530 nodes, 578 edges, and 54 dangling endpoints. It remains `CANDIDATE`; route continuity is `NOT_ESTABLISHED` and all unavailable width, slope, step, access, operation, hazard, M6, and M7 evidence remains `UNKNOWN` or `null + reason`.

`ACTUAL_MODEL=UNVERIFIED`; `MODEL_ROUTE_VERIFIED=false`. `VIEWER_CONNECTED=false`; `MODEL_CONNECTED=false`; `ANALYSIS_CONNECTED=false`; `M7_CONNECTED=false`. This artifact does not claim real-geometry connection, safety, accessibility, passability, operational opening, or administrative validation.
