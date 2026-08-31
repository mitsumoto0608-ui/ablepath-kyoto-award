# Phase 4 Fujisawa / Enoshima P0 lane

Status: `READY_FOR_HUMAN_APPROVAL`.

The bounded OSM candidate subset is staged and normalized.  It is VGI,
`CANDIDATE`, and source-traceable; it is not a route, accessibility, safety,
operation, facility-entrance, capacity, or administrative claim.

## Retained OSM subset

- Source endpoint: `https://overpass-api.de/api/interpreter`; attribution:
  `https://www.openstreetmap.org/copyright`; bounded query at
  `sources/osm-corridor.overpassql`.
- Requested snapshot: `2026-08-30T00:00:00Z`; raw response SHA-256:
  `c016cd4d6e2e6de4c5a43ba181dd24ec34f3ae774fbd83662fd795f700ad3d04`;
  retained raw filename: `osm-corridor.raw.json`; trust location is recorded
  only as the relative receipt value `ablepath-raw/fujisawa_enoshima/osm-corridor.raw.json`;
  raw size: 581,965 bytes. The raw response is not in Git.
- Normalized corridor SHA-256:
  `01eae54bac6385da4aa5d39c92c935fc25dc799e91be37b030943c1ae5016c32`.
- License: ODbL-1.0, redistribution only with its attribution/share-alike
  obligations. Human license review remains pending.
- Candidate topology: 16 nodes, 15 edges, 1 component, 2 dangling endpoints,
  no duplicate IDs, self-loops, or zero-length edges.

## Coordinate boundary

The OSM source and all serialized GeoJSON are EPSG:4326 with the GeoJSON
coordinate order `longitude, latitude`.  This serialization order is not a
statement about the formal axis order of an official projected source.

Where an official Fujisawa hazard source declares EPSG:6668, its formal axis
must remain recorded as the source-declared projected-axis statement. It is
not relabelled as GeoJSON longitude/latitude and no transformation is claimed
here. Official hazard and PLATEAU capabilities are `null` with non-empty
reasons in `sources/unresolved_contracts.json` and `status.json`; no
official-derived payload is retained in this P0 subset.

## Explicit non-promotions

- Official PDFs are not tracked.
- No facility payload is included, so no tsunami-evacuation facility is
  conflated with a generic shelter.
- Facility capacity, entrance, opening/operation, arrival time, inundation
  depth, hazard-derived closure, M6, M7, KPI, and administrative validation
  remain `UNKNOWN` or `null + reason`.
- `MODEL_ROUTE_VERIFIED=false`; `ACTUAL_MODEL=UNVERIFIED`.

Human review is still required for ODbL redistribution obligations and all
official PDF/PLATEAU/hazard/facility contracts. This lane does not change
shared viewer or analysis code.
