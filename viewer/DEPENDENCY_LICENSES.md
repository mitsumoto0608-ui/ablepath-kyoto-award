# Viewer dependency and license notice

The viewer installs runtime code only from the committed npm lockfile. Versions are exact; CDN script loading is prohibited.

| Package | Exact version | License | Purpose |
|---|---:|---|---|
| `maplibre-gl` | 6.6.0 | BSD-3-Clause | WebGL 2D rendering of the same-origin, hash-verified candidate GeoJSON and a non-critical OSM raster basemap |
| `cesium` | 1.144.0 | Apache-2.0 | Lazy-loaded 3D Tiles runtime for reviewed PLATEAU metadata |

MapLibre attribution for the retained coordinate artifact is `© OpenStreetMap contributors / Data available under ODbL 1.0`. Public tile-service policy and ODbL share-alike handling remain a human release gate.

CesiumJS is used without a mandatory commercial token. The configured Project PLATEAU metadata records PDL1.0 / CC BY 4.0-compatible terms. A successful mocked tileset test proves the local runtime path only; it does not change the citypack truth flag `PLATEAU_3D_CONNECTED=false`.
