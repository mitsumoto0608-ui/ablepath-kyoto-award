# Phase 2 map UI status

`MAPLIBRE_CONNECTED=false`

`CESIUM_CONNECTED=false`

`PLATEAU_3D_CONNECTED=false`

`REAL_MAP_COMPLETE=false`

`TWO_D_IMPLEMENTATION=SYNTHETIC_SVG_SCHEMATIC`

## MapLibre gate

The current viewer has no MapLibre runtime dependency. The official
[MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/) documentation and
[npm package record](https://www.npmjs.com/package/maplibre-gl) were checked on
2026-08-30 and reported `maplibre-gl=6.6.0` with a BSD-3-Clause license. An exact
dependency install was attempted once in the isolated
`task/maplibre-cesium-v1` worktree and was rejected by the dependency-safety
approval gate. No package manifest, lockfile, or `node_modules` content was
changed.

The identical install was not retried and no CDN/unpkg runtime bypass was
introduced. Those alternatives would weaken deterministic Hosted CI and the
reviewed dependency boundary. Connecting MapLibre therefore requires an
explicit human approval for the exact pinned dependency and lockfile change.

Until that gate is granted, the existing SVG is retained only as a clearly
labelled synthetic schematic. It is not a real map and does not connect any
real city geometry.

## Cesium / PLATEAU gate

No verified per-city PLATEAU 3D Tiles URL, redistribution decision, browser CORS
result, or reviewed Cesium dependency is connected in this checkpoint. The 3D
tab keeps the existing non-fatal disclosure and returns users to 2D. It does
not claim that PLATEAU or Cesium loaded successfully.

## Non-negotiable fallback behavior

- a basemap or 3D failure must never erase local evidence or turn UNKNOWN into
  PASS/OPEN;
- no commercial token is required or stored;
- the edge table remains the non-map alternative;
- M6 stays `NOT_COMPUTED` and its selector stays disabled;
- source-traceable city packages, if integrated separately, are not called
  map-connected until the renderer and its tests actually consume them.

This degraded checkpoint is not an accessibility, safety, legal, or
administrative validation.
